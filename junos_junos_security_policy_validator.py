#!/usr/bin/env python3

import numpy as np
import ipaddress
import lxml.etree as ET
import re
from sys import exit
from getpass import getpass
from netmiko import ConnectHandler

'''
This is a script to validate firewall policy on Juniper SRX firewall, between multiple src and IP dst addresses, if:
1. Queried Internal IP addresses are learned via static route
2. Queried Internal IP addresses belong to same route table
3. Internal IP address must be submitted as address without prefix/mask
Script might be interrupted if conditions above not met
'''

xml_pattern = re.compile(r"\sxmlns\W.+\"|\sjunos\:.+\"")
zone_xpath = 'interface-information/logical-interface/logical-interface-zone-name'
nh_xpath = 'route-information/route-table/rt/rt-entry/nh/via'
rtbl_xpath = 'route-information/route-table'
rt_xpath = ['table-name', 'rt/rt-destination', 'rt/rt-entry/nh/via', 'rt']

# build connetion to Junos firewall
def ConnBldr(password, host='IPAddr-Sec-JunosFW', username='netadmin'):
	junos_host = {'device_type': 'juniper_junos', 'host': host, 'username': username, 'password': password}
	conn = ConnectHandler(**junos_host)
	return conn

# generate, parse XML output to string and remove Namespace and AttributeValuePair in tags
# return a list of XML elements
def XMLBldr(conn, cmd, xml_pattern, XPath):
	xml_output = conn.send_command(cmd)
	xml_root = re.sub(xml_pattern, "", xml_output)
	xml_tree = ET.fromstring(xml_root).xpath(XPath)
	return xml_tree

'''
Find the route table and outgoing intf for the requested Internal IP
Remove empty route table entry and default route entry, 
if IP is only reachable via default route, query will be terminated
Route entry and outgoing interface with max prefix length will be selected, 
if there is more than one matching entry
'''
def RtblFndr(xml_etree):
	rtbl_list = [(rt.find(rt_xpath[0]).text, rt.find(rt_xpath[1]).text, 
				ipaddress.ip_network(rt.find(rt_xpath[1]).text).prefixlen, rt.find(rt_xpath[2]).text)
				for rt in xml_etree
				if rt.find(rt_xpath[3]) != None and rt.find(rt_xpath[1]).text != '0.0.0.0/0']
	if len(rtbl_list) == 0:
		print("\n")
		print("No specific route for Internal host found, script exited.\n")
	else:
		max_len = max(list(np.array(rtbl_list)[:,2]))
	for i in rtbl_list:
		if len(rtbl_list) < 2:
			rtbl = rtbl_list[0][0]
			inside_intf = rtbl_list[0][3]
		else:
			rtbl = [rtbl_tpl[0] for rtbl_tpl in rtbl_list if int(max_len) in rtbl_tpl][0]
			inside_intf = [rtbl_tpl[3] for rtbl_tpl in rtbl_list if int(max_len) in rtbl_tpl][0]
	return rtbl, inside_intf

def BackListBldr(firewall, conn, inside_ips, bank_ips ,xml_pattern, rtbl_xpath, nh_xpath, zone_xpath):
	IPP_dicts = []
	IP_pairs = [{'inside_ip': inside_ip, 'bank_ip': bank_ip} for inside_ip in inside_ips for bank_ip in bank_ips]
	for IPP in IP_pairs:
		if '/' in IPP['bank_ip']:
			IPP['bank_ip'] = str(ipaddress.IPv4Interface(IPP['bank_ip']).ip)
		if firewall == 'IPAddr-Sec-JunosFW':
			cmd_rtbl_inside = 'show route ' + IPP['inside_ip'] + ' protocol static | display xml | no-more'
		else:
			cmd_rtbl_inside = 'show route ' + IPP['inside_ip'] + ' | display xml | no-more'
		inside_etree = XMLBldr(conn, cmd_rtbl_inside ,xml_pattern, rtbl_xpath)
		rtbl, inside_intf = RtblFndr(inside_etree)
		cmd_rtbl_bank = 'show route table ' + rtbl + ' ' + IPP['bank_ip'] + ' | display xml | no-more'
		bank_intf = XMLBldr(conn, cmd_rtbl_bank ,xml_pattern, nh_xpath)[0].text
		cmd_bank_intf = 'show interface ' + bank_intf + ' brief | display xml | no-more'
		bank_zone = XMLBldr(conn, cmd_bank_intf ,xml_pattern, zone_xpath)[0].text
		cmd_inside_intf = 'show interface ' + inside_intf + ' brief | display xml | no-more'
		inside_zone = XMLBldr(conn, cmd_inside_intf ,xml_pattern, zone_xpath)[0].text
		IPP_dict = {'rtbl': rtbl, 'inside_ip': IPP['inside_ip'], 'bank_ip': IPP['bank_ip'], 'inside_zone': inside_zone, 'bank_zone': bank_zone}
		IPP_dicts.append(IPP_dict)
	return IPP_dicts

def FrontListBldr(firewall, conn, inside_ips, bank_ips ,xml_pattern, rtbl_xpath, nh_xpath, zone_xpath):
	FrontIPP_dicts = []
	FrontIP_pairs = [{'inside_ip': inside_ip, 'bank_ip': bank_ip} for inside_ip in inside_ips for bank_ip in bank_ips]
	for FrontIPP in FrontIP_pairs:
		if '/' in FrontIPP['bank_ip']:
			FrontIPP['bank_ip'] = str(ipaddress.IPv4Interface(FrontIPP['bank_ip']).ip)
		if firewall == 'IPAddr-Sec-JunosFW':
			cmd_front_rtbl_bank = 'show route ' + FrontIPP['bank_ip'] + ' protocol static | display xml | no-more'
		else:
			cmd_front_rtbl_bank = 'show route ' + FrontIPP['bank_ip'] + ' | display xml | no-more'
		front_bank_etree = XMLBldr(conn, cmd_front_rtbl_bank ,xml_pattern, rtbl_xpath)
		front_rtbl, front_bank_intf = RtblFndr(front_bank_etree)
		cmd_front_rtbl_inside = 'show route table ' + front_rtbl + ' ' + FrontIPP['inside_ip'] + ' | display xml | no-more'
		front_inside_intf = XMLBldr(conn, cmd_front_rtbl_inside ,xml_pattern, nh_xpath)[0].text
		front_cmd_inside_intf = 'show interface ' + front_inside_intf + ' brief | display xml | no-more'
		front_inside_zone = XMLBldr(conn, front_cmd_inside_intf ,xml_pattern, zone_xpath)[0].text
		front_cmd_bank_intf = 'show interface ' + front_bank_intf + ' brief | display xml | no-more'
		front_bank_zone = XMLBldr(conn, front_cmd_bank_intf ,xml_pattern, zone_xpath)[0].text
		FrontIPP_dict = {'rtbl': front_rtbl, 'inside_ip': FrontIPP['inside_ip'], 'bank_ip': FrontIPP['bank_ip'], 'front_inside_zone': front_inside_zone, 'front_bank_zone': front_bank_zone}
		FrontIPP_dicts.append(FrontIPP_dict)
	return FrontIPP_dicts

# print out result based on policy-name
def ResultPrinter(conn, banner_zone_policy, cmd_show_zone_policy, banner_global_policy, cmd_show_global_policy):
    show_policy = re.findall(r':\s(.*?),', conn.send_command(cmd_show_zone_policy))
    if show_policy[0] != 'Default-Policy':
        print(banner_zone_policy)
        print("Zone Policy: ", show_policy[0])
        print("Action: ", show_policy[1], "\n"*3)
    else:
        show_global_policy = re.findall(r':\s(.*?),', conn.send_command(cmd_show_global_policy))
        print(banner_zone_policy)
        print("Zone Policy: ", show_policy[0])
        print("Action: ", show_policy[1], "\n")
        print(banner_global_policy)
        print("Global Policy: ", show_global_policy[0])
        print("Action: ", show_global_policy[1], "\n"*3)

def main():
	bank_ips = input("Customer IP(for e.g. 10.1.1.1 10.1.1.2): ").replace(';',' ').replace(',',' ').split()
	inside_ips = input("Internal Server IPs(for e.g. 1.1.1.1 2.2.2.2 3.3.3.3 4.4.4.4): ").replace(';',' ').replace(',',' ').split()
	proto = input("Protocol(tcp/udp): ")
	ports = re.findall(r'\d+', input("Destination Ports(for e.g. 80, 443, 30000, 40000): "))
	dirct = input("Traffic Direction: 0 - internal, 1 - inbound, 2 - outbound:\n")
	firewall = input("Target Firewall: Please select one of IPAddr-Sec-JunosFW, IPAddr-Sec-CiscoASA or IPAddr-DMZ-JunosFW\n")
	password = getpass("TACACS Password/RSA Token: ")
	FWConn = ConnBldr(password, firewall)
	# extract single interfaces and routing table from lists above
	# so far the script cannot handle query of ip addresses from multiple routing tables
	back_dicts = BackListBldr(firewall, FWConn, inside_ips, bank_ips ,xml_pattern, rtbl_xpath, nh_xpath, zone_xpath)
	if int(dirct) == 0:
		front_dicts = FrontListBldr(firewall, FWConn, inside_ips, bank_ips ,xml_pattern, rtbl_xpath, nh_xpath, zone_xpath)
		policy_dicts = [{**front_dict, **back_dict, "proto": proto, "port": port} 
			for front_dict in front_dicts
			for back_dict in back_dicts 
			for port in ports]
		# strip duplicate dicts in the list specifically due to front- and back-end scrub for internal traffic which keeping its order by sorted()
		# enable print in ZoneListBldr to verify
		policy_dicts = [dict(t) for t in {tuple(sorted(d.items())) for d in policy_dicts}]
	else:
		policy_dicts = [{**back_dict, "proto": proto, "port": port} 
			for back_dict in back_dicts 
			for port in ports]
	for pol_dict in policy_dicts:
		print(pol_dict)
	for pol_dict in policy_dicts:
		print("*"*80)
		if int(dirct) == 1:
			banner_zone_policy = " ".join(["Validating Backend zone policy for traffic from", pol_dict['bank_ip'], "to", pol_dict['inside_ip'], pol_dict['proto'], "port", pol_dict['port']])
			banner_global_policy = " ".join(["Validating Backend global policy for traffic from", pol_dict['bank_ip'], "to", pol_dict['inside_ip'], pol_dict['proto'], "port", pol_dict['port']])
			cmd_show_zone_policy = " ".join(['show security match-policies from-zone', pol_dict['bank_zone'], 'source-ip', pol_dict['bank_ip'],
									'source-port 65000 to-zone', pol_dict['inside_zone'], 'destination-ip', pol_dict['inside_ip'],
									'destination-port', pol_dict['port'], 'protocol', pol_dict['proto'], ' | match action-type'])
			cmd_show_global_policy = " ".join(['show security match-policies global from-zone', pol_dict['bank_zone'], 'source-ip', pol_dict['bank_ip'],
									'source-port 65000 to-zone', pol_dict['inside_zone'], 'destination-ip', pol_dict['inside_ip'],
									'destination-port', pol_dict['port'], 'protocol', pol_dict['proto'], ' | match action-type'])
			print('Backend Customer Zone:', pol_dict['bank_zone'], '\n', 'Backend Internal Zone:', pol_dict['inside_zone'], '\n')
			ResultPrinter(FWConn, banner_zone_policy, cmd_show_zone_policy, banner_global_policy, cmd_show_global_policy)
		elif int(dirct) == 2:
			banner_zone_policy = " ".join(["Validating Backend zone policy for traffic from", pol_dict['inside_ip'], "to", pol_dict['bank_ip'], pol_dict['proto'], "port", pol_dict['port']])
			banner_global_policy = " ".join(["Validating Backend global policy for traffic from", pol_dict['inside_ip'], "to", pol_dict['bank_ip'], pol_dict['proto'], "port", pol_dict['port']])
			cmd_show_zone_policy = " ".join(['show security match-policies from-zone', pol_dict['inside_zone'], 'source-ip', pol_dict['inside_ip'],
									'source-port 65000 to-zone', pol_dict['bank_zone'], 'destination-ip', pol_dict['bank_ip'],
									'destination-port', pol_dict['port'], 'protocol', pol_dict['proto'], ' | match action-type'])
			cmd_show_global_policy = " ".join(['show security match-policies global from-zone', pol_dict['inside_zone'], 'source-ip', pol_dict['inside_ip'],
									'source-port 65000 to-zone', pol_dict['bank_zone'], 'destination-ip', pol_dict['bank_ip'],
									'destination-port', pol_dict['port'], 'protocol', pol_dict['proto'], ' | match action-type'])
			print('Backend Customer Zone:', pol_dict['bank_zone'], '\n', 'Backend Internal Zone:', pol_dict['inside_zone'], '\n')
			ResultPrinter(FWConn, banner_zone_policy, cmd_show_zone_policy, banner_global_policy, cmd_show_global_policy)
		elif int(dirct) == 0:
			banner_zone_policy = " ".join(["Validating Backend zone policy for traffic from", pol_dict['bank_ip'], "to", pol_dict['inside_ip'], pol_dict['proto'], "port", pol_dict['port']])
			banner_global_policy = " ".join(["Validating Backend global policy for traffic from", pol_dict['bank_ip'], "to", pol_dict['inside_ip'], pol_dict['proto'], "port", pol_dict['port']])
			banner_front_zone_policy = " ".join(["Validating Frontend zone policy for traffic from", pol_dict['bank_ip'], "to", pol_dict['inside_ip'], pol_dict['proto'], "port", pol_dict['port']])
			banner_front_global_policy = " ".join(["Validating Frontend global policy for traffic from", pol_dict['bank_ip'], "to", pol_dict['inside_ip'], pol_dict['proto'], "port", pol_dict['port']])
			cmd_show_zone_policy = " ".join(['show security match-policies from-zone', pol_dict['bank_zone'], 'source-ip', pol_dict['bank_ip'],
									'source-port 65000 to-zone', pol_dict['inside_zone'], 'destination-ip', pol_dict['inside_ip'],
									'destination-port', pol_dict['port'], 'protocol', pol_dict['proto'], ' | match action-type'])
			cmd_show_global_policy = " ".join(['show security match-policies global from-zone', pol_dict['bank_zone'], 'source-ip', pol_dict['bank_ip'],
									'source-port 65000 to-zone', pol_dict['inside_zone'], 'destination-ip', pol_dict['inside_ip'],
									'destination-port', pol_dict['port'], 'protocol', pol_dict['proto'], ' | match action-type'])
			cmd_show_front_zone_policy = " ".join(['show security match-policies from-zone', pol_dict['front_bank_zone'], 'source-ip', pol_dict['bank_ip'],
									'source-port 65000 to-zone', pol_dict['front_inside_zone'], 'destination-ip', pol_dict['inside_ip'],
									'destination-port', pol_dict['port'], 'protocol', pol_dict['proto'], ' | match action-type'])
			cmd_show_front_global_policy = " ".join(['show security match-policies global from-zone', pol_dict['front_bank_zone'], 'source-ip', pol_dict['bank_ip'],
									'source-port 65000 to-zone', pol_dict['front_inside_zone'], 'destination-ip', pol_dict['inside_ip'],
									'destination-port', pol_dict['port'], 'protocol', pol_dict['proto'], ' | match action-type'])
			print('Frontend Customer Zone:', pol_dict['front_bank_zone'], '\n', 'Frontend Internal Zone:', pol_dict['front_inside_zone'], '\n')
			ResultPrinter(FWConn, banner_front_zone_policy, cmd_show_front_zone_policy, banner_front_global_policy, cmd_show_front_global_policy)
			print('+'*60)
			print('Backend Customer Zone:', pol_dict['bank_zone'], '\n', 'Backend Internal Zone:', pol_dict['inside_zone'], '\n')
			ResultPrinter(FWConn, banner_zone_policy, cmd_show_zone_policy, banner_global_policy, cmd_show_global_policy)
	FWConn.disconnect()

if __name__=="__main__":
	main()
