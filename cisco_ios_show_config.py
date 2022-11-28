#!/usr/bin/env python3

from getpass import getpass
from netmiko import ConnectHandler

Password = getpass("Password:")
with open('data/cpes', 'r') as rtrs:
	for rtr in rtrs.read().splitlines():
		print("\n"*3, "-"*10, "Checking config of", rtr, "-"*10, "\n"*3)
		cpe_host = {'device_type': 'cisco_ios', 'host': rtr, 'username': 'netadmin', 'password': Password}
		conn = ConnectHandler(**cpe_host)
		with open('data/commands', 'r') as cmds:
			for cmd in cmds.read().splitlines():
				print(cmd, "\n"*2)
				show_config = conn.send_command(cmd)
				print(show_config, "\n"*2)


