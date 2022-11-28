#!/usr/bin/env python3

import csv
import sys
import ipaddress
import os
import re
from getpass import getpass
from netmiko import ConnectHandler
from collections import OrderedDict, Counter


def RNHFinder(output):
    if 'Protocol' in output:
        regex = r"Protocol next hop: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        NH = re.findall(regex, output, re.MULTILINE)[0]
        return NH
    else:
        regex = r"Next hop: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        NH = re.findall(regex, output, re.MULTILINE)[0]
        return NH

def FNHFinder(show_route):
    show_route_tables = re.sub("\n +\n", "\n\n", show_route)            # replace irregular regex pattern
    route_tables_list = show_route_tables.split("\n\n")             # split output to list of routing-instances
    rts_list = []
    for rtable in route_tables_list:
        rtable = re.sub("].+|:.+|\*|\[|>|to|via", "", rtable)       # remove unrelated output elements
        rt_list = list(filter(None, re.split("\n| +|/", rtable)))   # remove empty items and split route entry to list
        while len(rt_list) > 7:                                     # remove 2nd-best NH addr if more than 1 & outbd intf
            del rt_list[-1]                                         #   by its position in the route entry list 
        if len(rt_list) == 0:
            pass
        else:
            rts_list.append(rt_list)
    mml = max([int(a[2]) for a in rts_list])                            # extract max mask length
    matched_rts_list = [rt for rt in rts_list if int(rt[2]) == mml]     # extract route entry with max mask length
    nh_list = [i[5] for i in matched_rts_list]                          # create a list of NH addr 
    nh_dict = {nh: count for nh, count in Counter(nh_list).items()}     # create a dict of NH addr and count of that addr
    if len(nh_dict) == 1:                                               # if dict has only 1 item, the only NH will be selected as valid NH
        nh = [nh for nh, nh_cnt in nh_dict.items()]
        next_hop = nh[0]
    else:                                                               # otherwise the NH with 1 count will be selected as valid NH
        nh = [nh for nh, nh_cnt in nh_dict.items() if nh_cnt < 2]
        next_hop = nh[0]
    return next_hop

def NHMatcher(ipaddr, intf_table):
    with open(intf_table, 'r') as intf_csv:
        intf_rdr = csv.DictReader(intf_csv)
        for row in intf_rdr:
            try:
                if ipaddr == row['IP'] and (row['Type'] == 'JRTR' or row['Type'] == 'CRTR' or row['Type'] == 'CNRTR'):
                    NHRTR, NHAddr, NHRI, NHType = row['router'], row['IP'], row['routing_table'], row['Type']
                    return [NHRTR, NHAddr, NHRI, NHType]
                else:
                    pass
            except:
                print("Next hop address", ipaddr, "not on the list")

def NHCounter(ipaddr, intf_table):
    with open(intf_table, 'r') as intf_csv:
        intf_rdr = csv.DictReader(intf_csv)
        NHCTR = 0
        for row in intf_rdr:
            if ipaddr == row['IP']:
                NHCTR += 1
        return NHCTR

def ShowOutput(Password, ReqIP, DevType='JFW', Host='IPAddr-Pri-JunosFW', Rtbl='', Username='netadmin'):
    if DevType == 'JRTR':
        DevType = 'juniper_junos'
        junos_host = {'device_type': DevType, 'host': Host, 'username': Username, 'password': Password}
        conn = ConnectHandler(**junos_host)
        command = "show route table " + Rtbl + " " + ReqIP + " extensive active-path | match \"Next hop\" | no-more"
        show_route = conn.send_command(command)
    elif DevType == 'JFW':
        DevType = 'juniper_junos'
        junos_host = {'device_type': DevType, 'host': Host, 'username': Username, 'password': Password}
        conn = ConnectHandler(**junos_host)
        command = "show route " + ReqIP + " | match \"routes|\"\\*\\[\"|to\" | no-more"
        show_route = conn.send_command(command)
    return show_route

target_ip=input("please enter an IP address or file with requested IPs:")
Password = getpass("Password:\n\n")
intf_table = 'data/core-device-interfaces.csv'


InitOutput = ShowOutput(Password, target_ip)
InitNHList = NHMatcher(FNHFinder(InitOutput), intf_table)
if InitNHList:
    print("Found matched Interface IP", InitNHList[1], "on routing table", re.sub(".inet.0", "", InitNHList[2]), "of", InitNHList[0])
else:
    print("No matched device for IP", target_ip)
NHRTR, NHAddr, NHRI, NHType = InitNHList[0], InitNHList[1], InitNHList[2], InitNHList[3]
Hop = 1
while NHAddr:
    print("Checking device", NHRTR, "\n")
    if NHType == 'JRTR':
        CurrentRI = NHRI
        RtblOutput = ShowOutput(Password, target_ip, NHType, NHRTR, NHRI)
        NHList = NHMatcher(RNHFinder(RtblOutput), intf_table)
        NHAddr = RNHFinder(RtblOutput)
        NHCTR = NHCounter(RNHFinder(RtblOutput), intf_table)
        Hop += 1
        if NHList is None:
            print("Next hop address", NHAddr, "not on the list")
            break
        print("Found No.", Hop, "Hop", NHList[1], "on route table", re.sub(".inet.0", "", CurrentRI), "of", NHList[0])
        NHRTR, NHRI, NHType = NHList[0], NHList[2], NHList[3]
        if NHRI == 'inet.0':
            NHRI = CurrentRI
        elif NHCTR > 1:
            NHRI = CurrentRI
        else:
            pass
    elif NHType == 'CNRTR':
        print("Next hop is Nexus Switch", NHRTR, ", Under development")
        break
    elif NHType == 'JFW':
        RtblOutput = ShowOutput(Password, target_ip, NHType, NHRTR, NHRI)
        NHList = NHMatcher(FNHFinder(RtblOutput), intf_table)
        Hop += 1
        print("Found No.", Hop, NHList[1], "on router", NHList[0])
        NHRTR, NHAddr, NHRI, NHType = NHList[0], NHList[1], NHList[2], NHList[3]
        if NHRI == 'inet.0':
            NHRI = CurrentRI
        elif NHCTR > 1:
            NHRI = CurrentRI
        else:
            pass
    else:
        print("Next hop address", NHAddr, "not on the list!!!")
