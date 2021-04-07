"""
    DEFINE PURPOSE OF SCRIPT
"""
from netmiko import ConnectHandler
from datetime import datetime
import csv
import os
import re

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
    This app is broken up into three seperate sections
        - retrieve CDP neighbor information from a device within the device_info.csv
        - dynamically create .csv files for each device containing this information
        - maps out in the console output which port connects to which cdp neighbor
    The following block of code handles the processing of data within the device_info.csv file.
        - open the file in read-only mode and store the session as a variable csvfile
        - read through the data and store the information as variable reader
        - begin for loop
'''
with open('device_info.csv', mode='r') as csvfile:
    reader = csv.DictReader(csvfile)
    # username = raw_input('Please enter your username: \n')
    # used only when we want to prompt the user for username
    # password = raw_input('Please enter your password: \n')
    # used only when we want to prompt the user for their password
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
        switch = {'device_type': 'cisco_ios', 'ip': hostname, 'username': username, 'password': password,
                  'secret': enable_secret, 'verbose': False}
        ssh_session = ConnectHandler(**switch)
        ssh_session.enable()
        hostname = ssh_session.find_prompt()  # a netmiko function that retrieves current line from terminal
        hostname = hostname.replace("#", "")  # strips out the # sign from the Cisco prompt
        print(hostname + '\n')
        show_version = ssh_session.send_command('sh ver | i Cisco')
        userhome = os.path.expanduser('~')
        if re.search('IOS', show_version):
            show_run_txt = ssh_session.send_command('show run')
            show_version_txt = ssh_session.send_command('show version')
            show_environment_txt = ssh_session.send_command('show environment')
            show_interface_status_txt = ssh_session.send_command('show interface status')
            show_inventory_txt = ssh_session.send_command('show inventory')
            show_module_txt = ssh_session.send_command('show module')
            show_vlan_brief_txt = ssh_session.send_command('show vlan brief')
            show_spanning_tree_txt = ssh_session.send_command('show spanning-tree')
            show_ip_interface_brief_txt = ssh_session.send_command('show ip interface brief')
            show_interface_description_txt = ssh_session.send_command('show interface description')
            show_etherchannel_summary = ssh_session.send_command('show etherchannel summary')
            show_ip_arp_txt = ssh_session.send_command('show ip arp | ex Proto|Incomplete')
            show_cdp_neighbors_txt = ssh_session.send_command('show cdp neighbors detail')
            show_mac_address_table_dynamic_txt = ssh_session.send_command('show mac address-table dynamic | ex -|Vlan|Table|Total|Unicast|vlan')
            show_standby_all_txt = ssh_session.send_command('show standby all')
            show_standby_brief_txt = ssh_session.send_command('show standby brief')
            show_ip_route_summary_txt = ssh_session.send_command('show ip route summary')
            show_ip_bgp_summary_txt = ssh_session.send_command('show ip bgp summary')
            show_ip_bgp_txt = ssh_session.send_command('show ip bgp')
            show_ip_bgp_neighbors_txt = ssh_session.send_command('show ip bgp neighbors')
            show_ip_ospf_neighbor_txt = ssh_session.send_command('show ip ospf neighbor')
            show_ip_pim_rp_txt = ssh_session.send_command('show ip pim rp')
            show_ip_pim_neighbor_txt = ssh_session.send_command('show ip pim neighbor')
            show_ip_pim_rp_mapping_txt = ssh_session.send_command('show ip pim rp mapping')
            show_ip_pim_interface_txt = ssh_session.send_command('show ip pim interface')
            show_ip_pim_autorp_txt = ssh_session.send_command('show ip pim autorp')
            show_ip_mroute_summary_txt = ssh_session.send_command('show ip mroute summary')
            show_ip_access_list_txt = ssh_session.send_command('show ip access-list')
            cdp_nei_txt = ssh_session.send_command('show cdp nei det | i Device|Entry|IP|Plat|Inter')
            int_status_txt = ssh_session.send_command('show int status | ex Status')
            '''
                 create csv file for show ip interface brief
            '''
            show_output_txtfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S'))
                                               + '_show_output.txt')
            with open(show_output_txtfile, 'w') as f:
                f.write('\n-----------------------------------\n--------------show-run-------------\n---------'
                        '--------------------------\n\n')
                f.write(show_run_txt)
            with open(show_output_txtfile, 'a') as f:
                f.write('\n-----------------------------------\n-------show-version-------\n---------'
                        '---------------------------\n\n')
                f.write(show_version_txt)
                f.write('\n-----------------------------------\n-------show-environment-------\n---------'
                        '---------------------------\n\n')
                f.write(show_environment_txt)
                f.write('\n-----------------------------------\n-------show-interface-status-------\n---------'
                        '---------------------------\n\n')
                f.write(show_interface_status_txt)
                f.write('\n-----------------------------------\n-------show-inventory-------\n---------'
                        '---------------------------\n\n')
                f.write(show_inventory_txt)
                f.write('\n-----------------------------------\n-------show-module-------\n---------'
                        '---------------------------\n\n')
                f.write(show_module_txt)
                f.write('\n-----------------------------------\n-------show-vlan-brief-------\n---------'
                        '---------------------------\n\n')
                f.write(show_vlan_brief_txt)
                f.write('\n-----------------------------------\n-------show-spanning-tree-------\n---------'
                        '---------------------------\n\n')
                f.write(show_spanning_tree_txt)
                f.write('\n-----------------------------------\n-------show-interface-brief-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_interface_brief_txt)
                f.write('\n-----------------------------------\n-------show-interface-description-------\n---------'
                        '---------------------------\n\n')
                f.write(show_interface_description_txt)
                f.write('\n-----------------------------------\n-------show-etherchannel-------\n---------'
                        '---------------------------\n\n')
                f.write(show_etherchannel_summary)
                f.write('\n-----------------------------------\n-------show-ip-arp-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_arp_txt)
                f.write('\n-----------------------------------\n-------show-cdp-neighbor-------\n---------'
                        '---------------------------\n\n')
                f.write(show_cdp_neighbors_txt)
                f.write('\n-----------------------------------\n-------show-mac-address-------\n---------'
                        '---------------------------\n\n')
                f.write(show_mac_address_table_dynamic_txt)
                f.write('\n-----------------------------------\n-------show-standby-all-------\n---------'
                        '---------------------------\n\n')
                f.write(show_standby_all_txt)
                f.write('\n-----------------------------------\n-------show-standby-brief-------\n---------'
                        '---------------------------\n\n')
                f.write(show_standby_brief_txt)
                f.write('\n-----------------------------------\n-------show-ip-route-summary-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_route_summary_txt)
                f.write('\n-----------------------------------\n-------show-ip-bgp-summary-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_bgp_summary_txt)
                f.write('\n-----------------------------------\n-------show-ip-bgp-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_bgp_txt)
                f.write('\n-----------------------------------\n-------show-ip-bgp neighbor-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_bgp_neighbors_txt)
                f.write('\n-----------------------------------\n-------show-ip-ospf-neighbor-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_ospf_neighbor_txt)
                f.write('\n-----------------------------------\n-------show-pim-rp-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_rp_txt)
                f.write('\n-----------------------------------\n-------show-ip-pim-neighbor-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_neighbor_txt)
                f.write('\n-----------------------------------\n-------show-ip-pim-rp-mapping-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_rp_mapping_txt)
                f.write('\n-----------------------------------\n-------show-ip-pim-interface-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_interface_txt)
                f.write('\n-----------------------------------\n-------show-ip-pim-autorp-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_autorp_txt)
                f.write('\n-----------------------------------\n-------show-ip-mroute-summary-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_mroute_summary_txt)
                f.write('\n-----------------------------------\n-------show-ip-access-list-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_access_list_txt)
            '''
            create csv file for show interface description
            '''
            int_desc_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_interface_desc.csv')
            with open(int_desc_csvfile, 'w', newline='') as f:
                show_interface_description_txt = re.sub(r'admin down', 'admin_down', show_interface_description_txt)
                show_interface_description_list = show_interface_description_txt.splitlines()
                show_interface_description_list[:] = [item for item in show_interface_description_list if item != '']
                newlist = []
                for interface in show_interface_description_list:
                    interface = re.split(' +', interface, maxsplit=3) # split first 3 items in string
                    newlist.append(interface)
                writer = csv.writer(f)
                writer.writerows(newlist)
            '''
                create csv file for show cdp neighbor detail
            '''
            cdp_nei_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_cdp_neighbor.csv')
            with open(cdp_nei_csvfile, 'w', newline='') as f:
                cdp_nei_txt = re.sub(r'Device ID: |\(.+\)|Entry.+\(.+\):\s\n\s{2}.+\nPlatform:\s| Capabilities: .+|Interface: | Port ID \(outgoing port\): |  IP address: |Cisco .+', '', cdp_nei_txt)
                header = ['Hostname', 'Model', 'Local Interface', 'Remote Interface', 'IP Address']
                show_cdp_neighbors_list = re.split('\n|, ', cdp_nei_txt)
                show_cdp_neighbors_list[:] = [item for item in show_cdp_neighbors_list if item != '']
                show_cdp_neighbors_list = [show_cdp_neighbors_list[i:i + 5] for i in range(0, len(show_cdp_neighbors_list) + 1, 5)]
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(show_cdp_neighbors_list)
            '''
            create csv file for show mac address dynamic
            '''
            mac_add_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_mac_add.csv')
            with open(mac_add_csvfile, 'w', newline='') as f:
                header = ['VLAN', 'MAC Address', 'Interface']
                show_mac_address_table_dynamic_txt = re.sub(r'\n|DYNAMIC|dynamic|ip|ipx|assigned|other|,|x|\*|Yes+\s{0,}\d{0,}\s{0,}', ' ', show_mac_address_table_dynamic_txt) # substitute unnecessary characters in show mac outputs
                show_mac_address_table_dynamic_list = re.split(' +', show_mac_address_table_dynamic_txt) # separate string to list by spaces
                show_mac_address_table_dynamic_list[:] = [item for item in show_mac_address_table_dynamic_list if item != ''] # remove empty items in the list
                show_mac_address_table_dynamic_list = [show_mac_address_table_dynamic_list[i:i + 3] for i in range(0, len(show_mac_address_table_dynamic_list) + 1, 3)] # group items into sublists, three items per each sublist
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(show_mac_address_table_dynamic_list)
            '''
                  create csv file for show ip arp
            '''
            ip_arp_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_ip_arp.csv')
            with open(ip_arp_csvfile, 'w', newline='') as f:
                header = ['IP Address', 'Age', 'MAC Address', 'Interface']
                show_ip_arp_txt = re.sub(r'\n|Internet|ARPA', ' ', show_ip_arp_txt)
                show_ip_arp_list = re.split(' +', show_ip_arp_txt)
                show_ip_arp_list[:] = [item for item in show_ip_arp_list if item != '']
                show_ip_arp_list = [show_ip_arp_list[i:i + 4] for i in range(0, len(show_ip_arp_list) + 1, 4)]
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(show_ip_arp_list)
            '''
                  create csv file for show interface status
            '''
            int_status_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_int_status.csv')
            with open(int_status_csvfile, 'w', newline='') as f:
                header = ['Port', 'Status', 'Vlan', 'Duplex', 'Speed', 'Type']
                int_status_list = int_status_txt.splitlines()
                int_status_list[:] = [item for item in int_status_list if item != '']
                newlist = []
                for interface in int_status_list:
                    interface = interface[:10] + interface[29:] # interface = interface[:10] + interface[32:] for C6500
                    interface = re.split(' +', interface, maxsplit=5) # split first 5 items in string
                    newlist.append(interface)
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(newlist)
        elif re.search('Nexus', show_version):
            show_run_txt = ssh_session.send_command('show run')
            show_version_txt = ssh_session.send_command('show version')
            show_environment_txt = ssh_session.send_command('show environment')
            show_interface_status_txt = ssh_session.send_command('show interface status')
            show_inventory_txt = ssh_session.send_command('show inventory')
            show_module_txt = ssh_session.send_command('show module')
            show_vlan_brief_txt = ssh_session.send_command('show vlan brief')
            show_spanning_tree_txt = ssh_session.send_command('show spanning-tree')
            show_interface_brief_txt = ssh_session.send_command('show interface brief')
            show_interface_description_txt = ssh_session.send_command('show interface description')
            show_portchannell_summary = ssh_session.send_command('show port-channel summary')
            show_ip_arp_txt = ssh_session.send_command('show ip arp')
            show_cdp_neighbors_txt = ssh_session.send_command('show cdp neighbors detail')
            show_mac_address_table_dynamic_txt = ssh_session.send_command('show mac address-table dynamic')
            show_hsrp_all_txt = ssh_session.send_command('show hsrp all')
            show_hsrp_brief_txt = ssh_session.send_command('show hsrp brief')
            show_vpc_txt = ssh_session.send_command('show vpc')
            show_ip_route_summary_txt = ssh_session.send_command('show ip route summary')
            show_ip_bgp_summary_txt = ssh_session.send_command('show ip bgp summary')
            show_ip_bgp_txt = ssh_session.send_command('show ip bgp')
            show_ip_bgp_neighbors_txt = ssh_session.send_command('show ip bgp neighbors')
            show_ip_ospf_txt = ssh_session.send_command('show ip ospf')
            show_ip_ospf_int_br_txt = ssh_session.send_command('show ip ospf inter br')
            show_ip_ospf_neighbor_txt = ssh_session.send_command('show ip ospf neighbor')
            show_ip_pim_rp_txt = ssh_session.send_command('show ip pim rp')
            show_ip_pim_neighbor_txt = ssh_session.send_command('show ip pim neighbor')
            show_ip_pim_interface_txt = ssh_session.send_command('show ip pim interface')
            show_ip_pim_autorp_txt = ssh_session.send_command('show ip pim rp')
            show_ip_mroute_summary_txt = ssh_session.send_command('show ip mroute summary')
            show_ip_mroute_txt = ssh_session.send_command('show ip mroute')
            show_ip_access_list_txt = ssh_session.send_command('show ip access-list')
            show_feature_txt = ssh_session.send_command('show feature')
            show_feature_set_txt = ssh_session.send_command('show feature-set')
            show_fex_txt = ssh_session.send_command('show fex')
            show_fex_detail_txt = ssh_session.send_command('show fex det')
            show_lldp_neighbors_txt = ssh_session.send_command('show lldp neighbors')
            int_desc_txt = ssh_session.send_command('show int desc | grep ^Eth*')
            cdp_nei_txt = ssh_session.send_command('show cdp nei detail | egrep Device|IPv4|Plat|Interface')
            mac_add_txt = ssh_session.send_command('show mac add dyn | grep dynamic')
            ip_arp_txt = ssh_session.send_command('show ip arp | ex Total | ex Addr | ex IP | ex Adj')
            int_status_txt = ssh_session.send_command('show int status | ex Status')
            '''
                 create csv file for show ip interface brief
            '''
            show_output_txtfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S'))
                                               + '_show_output.txt')
            with open(show_output_txtfile, 'w') as f:
                f.write('\n-----------------------------------\n--------------show-run-------------\n---------'
                        '--------------------------\n\n')
                f.write(show_run_txt)
            with open(show_output_txtfile, 'a') as f:
                f.write('\n-----------------------------------\n-------show-version-------\n---------'
                        '---------------------------\n\n')
                f.write(show_version_txt)
                f.write('\n-----------------------------------\n-------show-environment-------\n---------'
                        '---------------------------\n\n')
                f.write(show_environment_txt)
                f.write('\n-----------------------------------\n-------show-interface-status-------\n---------'
                        '---------------------------\n\n')
                f.write(show_interface_status_txt)
                f.write('\n-----------------------------------\n-------show-inventory-------\n---------'
                        '---------------------------\n\n')
                f.write(show_inventory_txt)
                f.write('\n-----------------------------------\n-------show-module-------\n---------'
                        '---------------------------\n\n')
                f.write(show_module_txt)
                f.write('\n-----------------------------------\n-------show-vlan-brief-------\n---------'
                        '---------------------------\n\n')
                f.write(show_vlan_brief_txt)
                f.write('\n-----------------------------------\n-------show-spanning-tree-------\n---------'
                        '---------------------------\n\n')
                f.write(show_spanning_tree_txt)
                f.write('\n-----------------------------------\n-------show-interface-brief-------\n---------'
                        '---------------------------\n\n')
                f.write(show_interface_brief_txt)
                f.write('\n-----------------------------------\n-------show-interface-description-------\n---------'
                        '---------------------------\n\n')
                f.write(show_interface_description_txt)
                f.write('\n-----------------------------------\n--------show-portchannell-summary-------\n---------'
                        '---------------------------\n\n')
                f.write(show_portchannell_summary)
                f.write('\n-----------------------------------\n-------show-ip-arp-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_arp_txt)
                f.write('\n-----------------------------------\n-------show-cdp-neighbor-------\n---------'
                        '---------------------------\n\n')
                f.write(show_cdp_neighbors_txt)
                f.write('\n-----------------------------------\n-------show-mac-address-------\n---------'
                        '---------------------------\n\n')
                f.write(show_mac_address_table_dynamic_txt)
                f.write('\n-----------------------------------\n-------show-standby-all-------\n---------'
                        '---------------------------\n\n')
                f.write(show_hsrp_all_txt)
                f.write('\n-----------------------------------\n-------show-standby-brief-------\n---------'
                        '---------------------------\n\n')
                f.write(show_hsrp_brief_txt)
                f.write('\n-----------------------------------\n-------show-standby-brief-------\n---------'
                        '---------------------------\n\n')
                f.write(show_vpc_txt)
                f.write('\n-----------------------------------\n-------show-ip-route-summary-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_route_summary_txt)
                f.write('\n-----------------------------------\n-------show-ip-bgp-summary-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_bgp_summary_txt)
                f.write('\n-----------------------------------\n-------show-ip-bgp-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_bgp_txt)
                f.write('\n-----------------------------------\n-------show-ip-bgp neighbor-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_bgp_neighbors_txt)
                f.write('\n-----------------------------------\n-------show-ip-ospf-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_ospf_txt)
                f.write('\n-----------------------------------\n-------show-ip-ospf-interface-brief-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_ospf_int_br_txt)
                f.write('\n-----------------------------------\n-------show-ip-ospf-neighbor-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_ospf_neighbor_txt)
                f.write('\n-----------------------------------\n-------show-pim-rp-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_rp_txt)
                f.write('\n-----------------------------------\n-------show-ip-pim-neighbor-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_neighbor_txt)
                f.write('\n-----------------------------------\n-------show-ip-pim-interface-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_interface_txt)
                f.write('\n-----------------------------------\n-------show-ip-pim-autorp-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_pim_autorp_txt)
                f.write('\n-----------------------------------\n-------show-ip-mroute-summary-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_mroute_summary_txt)
                f.write('\n-----------------------------------\n-------show-ip-mroute-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_mroute_txt)
                f.write('\n-----------------------------------\n-------show-ip-access-list-------\n---------'
                        '---------------------------\n\n')
                f.write(show_ip_access_list_txt)
                f.write('\n-----------------------------------\n-------show-feature-------\n---------'
                        '---------------------------\n\n')
                f.write(show_feature_txt)
                f.write('\n-----------------------------------\n-------show-feature-set-------\n---------'
                        '---------------------------\n\n')
                f.write(show_feature_set_txt)
                f.write('\n-----------------------------------\n-------show-fex-------\n---------'
                        '---------------------------\n\n')
                f.write(show_fex_txt)
                f.write('\n-----------------------------------\n-------show-fex-detail-------\n---------'
                        '---------------------------\n\n')
                f.write(show_fex_detail_txt)
                f.write('\n-----------------------------------\n-------show-lldp-neighbors-------\n---------'
                        '---------------------------\n\n')
                f.write(show_lldp_neighbors_txt)
            '''
                  create csv file for show interface description
            '''
            int_desc_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_int_desc_csvfile.csv')
            ''' # head writing part
            myfile = open(int_desc_csvfile, 'w')
            fieldnames = ['Port', 'Type', 'Speed', 'Description'] # Here we will create the CSV column names to store data into
            writer = csv.DictWriter(myfile, fieldnames=fieldnames) # create a variable called 'writer' and concatenate the csv file path and fieldnames
            writer.writeheader() # Finally we write the header information to the CSV file
            ''' # head writing part
            with open(int_desc_csvfile, 'w', newline='') as f:
                header = ['Interface', 'Speed', 'Description']
                int_desc_txt = re.sub(r'\s+eth\s+', ' ', int_desc_txt)
                show_interface_description_list = int_desc_txt.splitlines()
                newlist = []
                for interface in show_interface_description_list:
                    interface = re.split(' +', interface, maxsplit=2) # split first 3 items in string
                    newlist.append(interface)
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(newlist)
            '''
                  create csv file for show cdp neighbor detail
            '''
            cdp_nei_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_cdp_neighbor.csv')
            with open(cdp_nei_csvfile, 'w', newline='') as f:
                header = ['Hostname', 'Interface Address', 'Model', 'Local Interface', 'Remote Interface', 'Mgmt Address']
                raw_list = re.split('Device ID:', cdp_nei_txt)
                raw_list[:] = [item for item in raw_list if item != '']
                newlist = []
                for cdp_neighbor in raw_list:
                    cdp_neighbor = re.sub(r'\(.+\)|Interface address\(es\):\n\s{4}.+\:\s|Platform: | Capabilities: .+|Interface: |Port ID \(outgoing port\): |    IPv4 Address: |Cisco .+|VG224|Interface address:', '', cdp_neighbor) # strip strings from output
                    newlist.append(cdp_neighbor)
                show_cdp_neighbors_list = []
                for cdp_neighbor in newlist:
                    item_list = []
                    item_list = re.split('\n|,\s{,}', cdp_neighbor)
                    item_list[:] = [item for item in item_list if item != '']
                    if len(item_list) >= 8:
                        item_list = item_list[0:2] + item_list[3:7]
                    show_cdp_neighbors_list.append(item_list)
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(show_cdp_neighbors_list)
            '''
                  create csv file for show mac address dynamic
            '''
            mac_add_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_mac_add.csv')
            with open(mac_add_csvfile, 'w', newline='') as f:
                header = ['VLAN', 'MAC Address', 'Age', 'Interface']
                mac_add_txt = re.sub(r'\+|\*|\n|\*|F    F|    dynamic   |Yes|vPC|Peer-Link', ' ', mac_add_txt)
                show_mac_address_table_dynamic_list = re.split(' +', mac_add_txt)
                show_mac_address_table_dynamic_list[:] = [item for item in show_mac_address_table_dynamic_list if item != '']
                show_mac_address_table_dynamic_list = [show_mac_address_table_dynamic_list[i:i + 4] for i in range(0, len(show_mac_address_table_dynamic_list) + 1, 4)]
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(show_mac_address_table_dynamic_list)
            '''
                  create csv file for show ip arp
            '''
            ip_arp_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_ip_arp.csv')
            with open(ip_arp_csvfile, 'w', newline='') as f:
                header = ['IP Address', 'Age', 'MAC Address', 'Interface']
                ip_arp_txt = re.sub(r'\n', ' ', ip_arp_txt)
                show_ip_arp_list = re.split(' +', ip_arp_txt)
                show_ip_arp_list[:] = [item for item in show_ip_arp_list if item != '']
                show_ip_arp_list = [show_ip_arp_list[i:i + 4] for i in range(0, len(show_ip_arp_list) + 1, 4)]
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(show_ip_arp_list)
            '''
                  create csv file for show interface status
            '''
            int_status_csvfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_int_status.csv')
            with open(int_status_csvfile, 'w', newline='') as f:
                header = ['Port', 'Status', 'Vlan', 'Duplex', 'Speed', 'Type']
                int_status_list = int_status_txt.splitlines()
                int_status_list[:] = [item for item in int_status_list if item != '']
                newlist = []
                for interface in int_status_list:
                    interface = interface[:14] + interface[33:]
                    interface = re.split(' +', interface, maxsplit=5) # split first 5 items in string
                    newlist.append(interface)
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(newlist)
'''
    MAIN APP - FINISH
'''

'''
    TIMESTAMPS - FINISH
'''