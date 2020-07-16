"""
This is module showing specific output.
Module is named as <producer>_<platform>_<action>_<item>
"""

import os
import re
import csv
from itertools import chain
from datetime import datetime


def show_crypto(ssh_session, hostname):
	show_crypto_ipsec_sa_raw = ssh_session.send_command('show crypto ipsec sa')
	extract_crypto_ikev2_sa_stats = ssh_session.send_command('show crypto ikev2 sa | i READY')
	extract_crypto_ipsec_stats = ssh_session.send_command('show crypto ipsec sa | i caps|ident|endp|outbound spi')
	'''
		create txt file of show crypto ipsec related output for reference
	'''
	show_output_txtfile = os.path.join(os.getcwd(), hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S'))
									   + '_show_crypto.txt')
	with open(show_output_txtfile, 'w') as f:
		f.write('\n-----------------------------------'
				'\n-------show crypto ipsec sa--------\n'
				'-------------------------------------\n')
		f.write(show_crypto_ipsec_sa_raw)
	'''
		 create csv file for show crypto ipsec sa
	'''
	ikev2_sa_csv = os.path.join(os.getcwd(),
								hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_show_ikev2.csv')
	with open(ikev2_sa_csv, 'w', newline='') as f:
		header = ['Tunnel-id', 'Local-IP', 'Remote-IP', 'fvrf', 'ivrf']
		'''
		convert output string to source list with active ikev2 sas
		'''
		ikev2_sa_list = extract_crypto_ikev2_sa_stats.splitlines()
		'''
		create parent list for as value source of csv file
		'''
		ikev2_sa_item = []
		for peer in ikev2_sa_list:
			peer = re.sub('READY|/500', '', peer) # remove irrelevant characters from 'peer' string
			peer = re.split(' +|/', peer, maxsplit=5) # split 'peer' string into list with 5 items
			peer.pop()
			ikev2_sa_item.append(peer) # append child list 'peer' to parent list
		writer = csv.writer(f)
		writer.writerow(header)
		writer.writerows(ikev2_sa_item) # write parent list to csv file
	ipsec_sa_csv = os.path.join(os.getcwd(),
								hostname + str(datetime.now().strftime('_%Y%m%d%H%M%S')) + '_show_ipsec.csv')
	with open(ipsec_sa_csv, 'w', newline='') as f:
		header = ['Local-Endpt', 'Remote-Endpt',
				  'Local-Ident', 'Remote-Ident', 'Encryt', 'Decryt', 'Outbnd-SPI']
		ipsec_conns = extract_crypto_ipsec_stats.split(sep="local  ident")
		del ipsec_conns[0]
		conns_list = []
		for conn in ipsec_conns:
			ident = re.findall(
				r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d+/\d+",
				conn, re.MULTILINE)
			'''
			collect matched strings as list based on preceding strings
			'''
			local_endpt = re.findall(r"(?<=local crypto endpt.: )\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
									 conn, re.MULTILINE)
			remote_endpt = re.findall(r"(?<=remote crypto endpt.: )\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
									  conn, re.MULTILINE)
			encry_count = re.findall(r"(?<=pkts encrypt: )\d+",
									 conn, re.MULTILINE)
			decry_count = re.findall(r"(?<=pkts decrypt: )\d+",
									 conn, re.MULTILINE)
			spi = re.findall(r"(?<=current outbound spi: ).+",
							 conn, re.MULTILINE)
			'''
			chain previous lists to one iterable object and convert it to a child list, for a single SPI
			'''
			conn_list = list(chain(local_endpt, remote_endpt, ident, encry_count, decry_count, spi))
			'''
			append the child list to the parent list, for all SPIs
			'''
			conns_list.append(conn_list)
		print(conns_list)
		writer = csv.writer(f)
		writer.writerow(header)
		writer.writerows(conns_list)