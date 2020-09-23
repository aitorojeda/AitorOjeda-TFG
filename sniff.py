# The previous line ensures that this script is run under the context
# of the Python interpreter. Next, import the Scapy functions:
import time
import datetime
import netaddr
import sys
import os
from scapy.all import *
from pprint import pprint
from db import *

# Define the interface name that we will be sniffing from, you can
# change this if needed.
interface = "wlan0mon"
# Next, declare a Python list to keep track of client MAC addresses
# that we have already seen so we only print the address once per client.
# observedclients = []
# The sniffmgmt() function is called each time Scapy receives a packet
# (we'll tell Scapy to use this function below with the sniff() function).
# The packet that was sniffed is passed as the function argument, "p".
def sniffmgmt(packet):
	def comprobarMACNoRandom(conn,mac,rssi,fechaHora,tam):
		sql= ''' SELECT COUNT(*) FROM DataSniff'''
		cur = conn.cursor()
		cur.execute(sql)
		contador=cur.fetchone()[0]
		
		if contador == 0:
			return False
		cur.execute("SELECT mac FROM DataSniff WHERE mac=?",(mac,))
		aux = cur.fetchone()
		if not aux:
			return False
		else:
			cur.execute("UPDATE DataSniff SET rssi = ?,fechaHora = ?, TTL = 5, tam = ? WHERE mac = ?",(rssi,fechaHora,tam,mac,))
			conn.commit()
			return True

	def comprobarMACRandom(conn,mac,rssi,fechaHora,tam):
		aux_string=mac[0:7]
		sql= ''' SELECT COUNT(*) FROM DataSniffRandom'''
		cur = conn.cursor()
		cur.execute(sql)
		contador=cur.fetchone()[0]
		
		if contador == 0:
			return False
		cur2= conn.cursor()
		aux = cur2.execute("SELECT mac FROM DataSniffRandom WHERE mac LIKE '"+aux_string+"%'").fetchone()
		if not aux:
			return False
		if aux:
			cur.execute("UPDATE DataSniffRandom SET rssi = ?,fechaHora = ?, TTL = 5, tam = ? WHERE mac = ?",(rssi,fechaHora,tam,mac,))
			conn.commit()
			return True

	database = r"/home/kali/Desktop/database.db"
	conn=create_connection(database)
	now = datetime.now()
	dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
	if not packet.haslayer(Dot11):
		return

	# we are looking for management frames with a probe subtype
	# if neither match we are done here
	if packet.type != 0 or packet.subtype != 0x04:
		return

	# list of output fields
	fields = []
	try:
		parsed_mac = netaddr.EUI(packet.addr2)
		mac_info = parsed_mac.oui.registration().org
	except netaddr.core.NotRegisteredError:
		mac_info = "UNKNOWN"
	tam=""
	rssi_val = packet.dBm_AntSignal
	if rssi_val > -65:
		tam = "pequenia" 
	elif rssi_val <= -65 and rssi_val>= -78:
		tam = "mediana"
	else:
		tam="grande"
	dir_mac = packet.addr2
	paquete = dt_string + " " + dir_mac + " " + mac_info + " " + str(rssi_val) + " " + tam
	TTL=5
	task=(dir_mac,mac_info,rssi_val,dt_string,TTL,tam)
	if mac_info != "UNKNOWN":
		if comprobarMACNoRandom(conn,dir_mac,rssi_val,dt_string,tam) == False:	
			create_no_random_data(conn,task)
	else:
		if comprobarMACRandom(conn,dir_mac,rssi_val,dt_string,tam) == False:
			create_random_data(conn,task)
	print(paquete)
def main():
	database = r"/home/kali/Desktop/database.db"
	conn=create_connection(database)
	sql_create_sniff_table = """ CREATE TABLE IF NOT EXISTS "DataSniff" (
	"mac" text,
	"mac_info" text,
	"rssi" text,
	"fechaHora" text,
	"TTL" text,
	"tam" text,
	PRIMARY KEY("mac")
); """
	sql_create_sniff_random_table = """ CREATE TABLE IF NOT EXISTS "DataSniffRandom" (
	"mac" text,
	"mac_info" text,
	"rssi" text,
	"fechaHora" text,
	"TTL" text,
	"tam" text,
	PRIMARY KEY("mac")
); """
	create_table(conn,sql_create_sniff_table)
	create_table(conn,sql_create_sniff_random_table)
	sniff(iface=interface, prn=sniffmgmt)
if __name__ == '__main__':
	main()

