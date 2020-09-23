import time
import datetime
from db import *
def tempo():
	database = r"/home/kali/Desktop/database.db"
	conn=create_connection(database)
	contador=0

	while True:
		cur = conn.cursor()
		time.sleep(60)
		print("Minuto {contador}")
		contador=contador+1
		cur.execute("DELETE FROM DataSniff WHERE TTL=0")
		cur.execute("DELETE FROM DataSniffRandom WHERE TTL=0")
		cur.execute("UPDATE DataSniff SET TTL = TTL - 1")
		conn.commit()
		cur.execute("UPDATE DataSniffRandom SET TTL = TTL - 1")
		conn.commit()		
tempo()
