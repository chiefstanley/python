#!/usr/bin/env python3

from operator import itemgetter
import ipaddress as IP
import re
from netmiko import ConnectHandler
from getpass import getpass
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

src_ips = re.split(', *|; *| *', input("Source IPs: "))
dst_ips = re.split(', *|; *| *', input("Destination IPs: "))
proto = input("Protocol: ")
ports = re.findall(r'\d+', input("Destination Ports: "))
ASAs = list(input("Please select: asa1 asa2 asa3 asa4\n").split())
password = getpass("Password: ")

def ASARouteGen(conn, password):
    conn.enable()
    conn.send_command('terminal pager 0')
    show_route = conn.send_command('show route | b Gateway')
    str_asaroute = re.sub("\n\s+|Gateway\s.+", " ", show_route) # fold multi-line route entries to one line
    str_asaroute = re.sub(".+LR-TACACS.+", "", str_asaroute) # remove route LR-TACACS from route-table
    asaroute_list = list(filter(None, str_asaroute.split("\n")))
    return asaroute_list

def QueryListGen(asaroute_list ,src_ips, dst_ips, proto, ports):
    Dict_List, routes_list = [], []
    ip_pairs = [{'src': src_ip, 'dst': dst_ip} for src_ip in src_ips for dst_ip in dst_ips]
    for ip_pair in ip_pairs:
        if '/' in ip_pair['src']:
            src_ip = str(IP.IPv4Interface(ip_pair['src']).ip)
        else:
            src_ip = str(IP.ip_address(ip_pair['src']))
        if '/' in ip_pair['dst']:
            dst_ip = str(IP.IPv4Interface(ip_pair['dst']).ip)
        else:
            dst_ip = str(IP.ip_address(ip_pair['dst']))
        src_subnet = IP.ip_network(src_ip)
#       print(src_ip, dst_ip)
        for route in asaroute_list:
            rt_list = route.split()                                                                                                                                  
            _, sbnt, msk, *mgt_dst, intf = rt_list
            subnet = IP.ip_network("/".join([sbnt, msk]))
            prf_len = subnet.prefixlen
            route_tuple = (subnet, prf_len, intf)
            routes_list.append(route_tuple)
        matched_subnets = [(route[0], route[1], route[2]) for route in routes_list if src_subnet.overlaps(route[0])]
        max_len = max([route[1] for route in matched_subnets])
        for subnet in matched_subnets:
            if len(matched_subnets) < 2:
                intf = matched_subnets[0][2]
            else:
                intf = [subnet[2] for subnet in matched_subnets if subnet[1] == max_len][0]
        Dict = {'ip_src': src_ip, "ip_dst": dst_ip, 'src_intf': intf}
        Dict_List.append(Dict)
    Policy_Dicts = [{**Dict, "proto": proto, "port": int(port)} for Dict in Dict_List for port in ports]
#   Policy_Dicts = [dict(t) for t in {tuple(sorted(d.items())) for d in Policy_Dicts}]
    Policy_Dicts = sorted([dict(t) for t in {tuple(sorted(d.items())) for d in Policy_Dicts}], key=itemgetter('ip_src', 'ip_dst', 'port'))
#   for PDict in Policy_Dicts:
#       print(PDict)
    return Policy_Dicts

def main():
    print("\n")
    for asa in ASAs:
        print("Validation on", asa, "...\n")
        asa_host = {'device_type': 'cisco_asa', 'host': asa, 'username': 'netadmin', 'password': password, 'secret': password}
        asa_conn = ConnectHandler(**asa_host)
        asa134_rtbl = ASARouteGen(asa_conn, password)
        query_list = QueryListGen(asa134_rtbl, src_ips, dst_ips, proto, ports)
        for query in query_list:
            print("*"*80)
            cmd_packet_tracer = " ".join(['packet-tracer input', query['src_intf'], query['proto'], query['ip_src'], '65000', query['ip_dst'], str(query['port']), 'detailed'])
            show_packet_tracer = asa_conn.send_command(cmd_packet_tracer)
            action = re.search('Action:\s(.+)', show_packet_tracer)
            acl = re.search('access-list.+extended.+', show_packet_tracer)
            print("Secure policy for traffic from", query['ip_src'], "to", query['ip_dst'], "port", query['port'], "on", asa, "\n")
            if acl is not None:
                print("Source Interface:")
                print(" ", query['src_intf'])
                print("Policy Action:")
                print(" ", action.group(1))
                print("Access Policy: ")
                print(" ", acl.group(0), "\n\n")
            else:
                print("Source Interface:")
                print(" ", query['src_intf'])
                print("Policy Action:")
                print(" ", action.group(1))
        asa_conn.disconnect()

if __name__=="__main__":
    main()
