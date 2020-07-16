"""
    DEFINE PURPOSE OF SCRIPT
"""
import csv
import cisco_ios_show_crypto
from datetime import datetime
from netmiko import SSHDetect, ConnectHandler

'''
    AUTHOR INFORMATION
'''
__author__ = 'Calvin Remsburg'
# (c) 2016, packetferret.

'''
    TIMESTAMPS - START
'''
app_timestamp_start = datetime.now()

'''
    MAIN APP - START
    This app is broken up into two separate sections
        - retrieve show output information from a device within the device_info.csv
        - dynamically create .csv files for each device containing this information
    The following block of code handles the processing of data within the device_info.csv file.
        - open the file in read-only mode and store the session as a variable csv file
        - read through the data and store the information as variable reader
        - begin for loop
'''
with open('device_info.csv', mode='r') as csvfile:
    reader = csv.DictReader(csvfile)
    '''
        The following block of code handles the heart and soul of the app, the mighty for loop
            - for every iteration of data within a row of variable reader, proceed...
    '''
    for row in reader:
        loop_timestamp_start = datetime.now()
        '''
            The following block of code handles the building of the ssh session through Netmiko
                - pulls the hostname, username, and password from the .csv file
                - builds a dictionary with this informaiton
                - creates an SSH session and stores it as ssh_session variable
                - finds the hostname and replaces the # sign from the prompt
                - prints out to the console a bunch of pretty formatting to highlight what device we're 
                  currently iterating through.
                - grabs the output of a show cdp neighbor detail, only including relevant information
        '''
        hostname = row['hostname']
        username = row['username']
        password = row['password']
        enable_secret = row['enable_secret']
        target_device = {'device_type': 'autodetect', 'ip': hostname, 'username': username, 'password': password,
                  'secret': enable_secret, 'verbose': False}
        ssh_session = ConnectHandler(**target_device)
        detected_type = SSHDetect(**target_device).autodetect()
        ssh_session.enable()
        hostname = ssh_session.find_prompt().replace("#", "")  # strips out the # sign from the Cisco prompt
        print(hostname + ' is a ' + detected_type + '\n')
        if detected_type == 'cisco_ios':
            '''
            call platform specific module handling individual task
            '''
            cisco_ios_show_crypto.show_crypto(ssh_session, hostname)
        '''		
        elif detected_type == 'cisco_asa':
		'''
'''
    MAIN APP - FINISH
'''

'''
    TIMESTAMPS - FINISH
'''