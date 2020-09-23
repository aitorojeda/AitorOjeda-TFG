from flask import Flask
from flask import render_template, redirect, request

import sqlite3
from db import *
nombre_global=""
tam_global=""
app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def config():

	return render_template('config.html',)

@app.route('/Inicio',methods=['GET','POST'])
def Inicio():
	global nombre_global
	global tam_global
	database = r"/home/kali/Desktop/database.db"
	conn=sqlite3.connect(database)
	conn.row_factory = sqlite3.Row

	cur = conn.cursor()
	cur.execute("SELECT mac,mac_info,rssi,fechaHora FROM DataSniff WHERE tam =? UNION SELECT mac,mac_info,rssi,fechaHora FROM DataSniffRandom WHERE tam = ? ",(tam_global,tam_global,))
	rowsNoR = cur.fetchall();
	cur2 = conn.cursor()
	#cur2.execute("SELECT mac,mac_info,rssi,fechaHora FROM DataSniff WHERE tam NOT IN ('?') UNION SELECT mac,mac_info,rssi,fechaHora FROM DataSniffRandom WHERE tam NOT IN ('?')",(tam_global,tam_global,))
	#rowsR = cur2.fetchall();
	cur.execute("SELECT COUNT(*) FROM (SELECT mac FROM DataSniff WHERE tam IN (?) UNION SELECT mac FROM DataSniffRandom WHERE tam IN (?))",(tam_global,tam_global,))
	res=cur.fetchone()[0];
	
	cur.execute("SELECT * FROM Config WHERE nombre = ?",(nombre_global,))
	configRes=cur.fetchall()
	conn.close()
	return render_template('index.html',rowsNoR = rowsNoR, res = res, configRes=configRes)

@app.route('/Respuesta',methods=['POST','GET'])
def Respuesta():
	global nombre_global
	global tam_global
	database = r"/home/kali/Desktop/database.db"
	conn=sqlite3.connect(database)
	sql_create_config_table = """ CREATE TABLE IF NOT EXISTS "Config" (
	"nombre" text,
	"aforo" text,
	"tam" text,
	PRIMARY KEY("nombre")
	); """
	create_table(conn,sql_create_config_table)
	conn.close()
	if request.method == 'POST':
		try:	
			conn=sqlite3.connect(database)

			nombre_global = request.form['nombreSala']
			aforo = request.form['aforoSala']
			tam_global = request.form['tam']

			cur = conn.cursor()
			cur.execute("INSERT INTO Config (nombre,aforo,tam) VALUES (?,?,?)",(nombre_global,aforo,tam_global))
			msg = "Sala guardada correctamente"
			conn.commit()
			
		except:
			msg = "Error al guardar la sala"
			conn.rollback()
			
			
		finally:
			return render_template('respuesta.html',msg = msg)
			conn.close()
	
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')


