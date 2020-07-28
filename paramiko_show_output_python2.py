#!/usr/bin/env python2

import paramiko
import os
import csv
import re
import time
from datetime import datetime
from itertools import chain
from getpass import getpass

ip = raw_input("Please enter your IP address: ")
username = raw_input("Please enter your username: ")
vpn_peer = raw_input("Please enter remote peer IP address: ")
password = getpass()

remote_conn_pre=paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote_conn_pre.connect(ip, port=22, username=username,
        password=password, 
        look_for_keys=False, allow_agent=False)

remote_conn = remote_conn_pre.invoke_shell()
output = remote_conn.recv(65535)
print output

remote_conn.send("terminal length 0\n")
time.sleep(.5)

remote_conn.send("show crypto ipsec sa peer " + vpn_peer + "\n")
time.sleep(.5)
ipsec_sa_output = remote_conn.recv(65535)
print ipsec_sa_output

ipsec_sa_csv = os.path.join(os.getcwd(), ip + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_show_ipsec.csv')

with open(ipsec_sa_csv, 'wb') as f:
    header = ['VRF', 'Local-Endpt', 'Remote-Endpt', 'Local-Ident', 'Remote-Ident', 'Encryt', 'Decryt', 'Outbnd-SPI']
    ipsec_conns = ipsec_sa_output.split('protected')
    del ipsec_conns[0]
    conns_list = []
    for conn in ipsec_conns:
        ident = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d+/\d+", conn, re.MULTILINE)
        local_endpt = re.findall(r"(?<=local crypto endpt.: )\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", conn, re.MULTILINE)
        remote_endpt = re.findall(r"(?<=remote crypto endpt.: )\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", conn, re.MULTILINE)
        encry_count = re.findall(r"(?<=pkts encrypt: )\d+", conn, re.MULTILINE)
        decry_count = re.findall(r"(?<=pkts decrypt: )\d+", conn, re.MULTILINE)
        spi = re.findall(r"(?<=current outbound spi: ).+", conn, re.MULTILINE)
        vrf = re.findall(r"(?<= vrf: ).+", conn, re.MULTILINE)
        conn_list = list(chain(vrf, local_endpt, remote_endpt, ident, encry_count, decry_count, spi))
	conns_list.append(conn_list)
    print(conns_list)
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(conns_list)
