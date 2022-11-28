#!/usr/bin/env python2

import paramiko
import socket
import os
import csv
import time
from datetime import datetime
from getpass import getpass

username = raw_input("Please enter your username: ")
password = getpass()

def get_output(hostname, cmds, target_text):
    remote_conn_pre=paramiko.SSHClient()
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_conn_pre.connect(hostname, port=22, username=username, password=password, look_for_keys=False, allow_agent=False, timeout=10)
    print "SSH connection established to %s" % hostname
    remote_conn = remote_conn_pre.invoke_shell()
    remote_conn.send("terminal length 0\n")
    time.sleep(.5)    
    output = ''
    for cmd in cmds:
        cmd += "\n"
        remote_conn.send(cmd)
        time.sleep(7)
        while remote_conn.recv_ready():
            data = remote_conn.recv(65535)
            output += data
            '''
            print output
            if remote_conn.exit_status_ready():
                break
            '''
    with open(target_text, 'a') as f:
        f.write(output)
    return target_text

with open('device_info.csv', mode='r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            loop_timestamp_start = datetime.now()    
            hostname = row['hostname']    
            path = '/home/netadmin/discovery'
            discovery = ['show run', 'show version', 'show inventory', 'show ip interface brief', 'show interface description', 'show ip bgp summary', 'show ip bgp']                
            show_output_txtfile = os.path.join(path, hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_show_output.txt')             
            get_output(hostname, discovery, show_output_txtfile)                
        except socket.timeout as error:
            print "SSH connection to %s timeout" % hostname
        except socket.gaierror as error:
            print "Unknown host %s" % hostname
