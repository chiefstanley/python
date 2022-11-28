#!/usr/bin/env python3

import csv
from getpass import getpass
from netmiko import ConnectHandler
from time import sleep

Password = getpass("Password:")
ritm = input("RITM number: ")
cpes = 'RITMs/' + ritm + '_cpes'
target_hosts = 'RITMs/' + ritm + '_hosts'
with open(cpes, 'r') as devices:
	#Trim ending newline of each item while converting TextIOWrapper to list
	devs = devices.read().splitlines()
	print(devs)
	for dev in devs:
		print("\n"*2, dev, "\n"*2)
		cpe_router = {'device_type': 'cisco_ios', 'host': dev, 'username': 'netadmin', 'password': Password, 'timeout': 10}
		conn = ConnectHandler(**cpe_router)
		show_overlay = conn.send_command("show vrf OVERLAY | i Gi")
		srcintf = show_overlay.strip()
		conn.disconnect()
		with open(target_hosts, 'r') as hosts_csv:
			hosts_rdr = csv.DictReader(hosts_csv)
			for row in hosts_rdr:
				with open(cpes, 'r') as devices:
					#Trim ending newline of each item while converting TextIOWrapper to list
					command = "telnet " + row['dstip'] + " " + row['dstport'] + " /vrf OVERLAY /source-interface " + srcintf
					conn = ConnectHandler(**cpe_router)
					conn.write_channel(command+'\n')
					sleep(1)
					CNTL_SHIFT_6=chr(29)
					conn.write_channel(CNTL_SHIFT_6)
					show_result=conn.read_channel()
					print(show_result,"\n"*2)
					conn.disconnect()
