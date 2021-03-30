
from gtts import gTTS
from playsound import playsound
import logging
import time
import rpyc
import os

nodos_sensores={}

def reproducirVoz(cadena):
    lan="es"
    try:
    	myobj=gTTS(text=cadena,lang=lan,slow=False)
    	myobj.save('/tmp/voice_command.mp3')
    	playsound('/tmp/voice_command.mp3')
    	os.remove('/tmp/voice_command.mp3')
    	return True
    except:
    	return False;

def listarNodos():
	lista=list(nodos_sensores.keys())
	logging.info(lista)
	for i in range(len(lista)):
		logging.info("Nodo: %d %s"%(i+1,lista[i]))
		#reproducirVoz("Nodo: %d %s"%(i+1,lista[i]))
		time.sleep(1)
	return len(lista)

def descubrirNodos():
	try:
		listaNodosSensores=rpyc.discover("SENSORNODE")
	except:
		return None
	for i in range(len(listaNodosSensores)):
		ip,port=listaNodosSensores[i]
		logging.info("Nodo sensor encontrado: IP: %s"%ip)
		con=rpyc.connect(ip,port)
		name=con.root.get_Name()
		logging.info("Nombre: %s"%name)
		nodos_sensores[name]=(ip,port)
	time.sleep(1)
	#reproducirVoz("Se encontraron %s nodos"%len(nodos_sensores))
	return len(nodos_sensores)

def consultarNodo(nodo):
	ip,port=nodos_sensores[nodo]
	try:
		sensor=rpyc.connect(ip,port)
		medicion=sensor.root.get_Measure()
		logging.info("El nodo sensor regresó esta lectura: %s"%medicion)
		#reproducirVoz("El nodo sensor regresó esta lectura: %s"%medicion)
		return True
	except:
		logging.info("Error obteniendo medida del nodo sensor")
		return False

def desconectarNodo(nodo):
	nodos_sensores.pop(nodo)
	#reproducirVoz("Se desconectó el nodo sensor: %s"%nodo)
	return True