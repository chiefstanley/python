#!/usr/bin/env python3

import threading
import time
from getpass import getpass
from netmiko import ConnectHandler

def cmd_getter(rtr, passwd):
	cpe_host = {'device_type': 'cisco_ios', 'host': rtr, 'username': 'netadmin', 'password': passwd}
	conn = ConnectHandler(**cpe_host)
	with open('data/commands', 'r') as cmds:
		for cmd in cmds.read().splitlines():
			show_config = conn.send_command(cmd)
			print("\n"*3, "-"*10, "Checking config of", rtr, "-"*10, "\n"*3)
			print(cmd, "\n"*2)
			print(show_config, "\n"*2)
	conn.disconnect()

Password = getpass("Password:")
start = time.perf_counter()
with open('data/cpes', 'r') as rtrs:
	getter_threads = []
	for rtr in rtrs.read().splitlines():
		t = threading.Thread(target=cmd_getter, args=(rtr, passwd))
		t.start()
		getter_threads.append(t)
	for thread in getter_threads:
		thread.join()

finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2)} second(s)')


