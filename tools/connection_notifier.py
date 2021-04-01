import socket
import time
import logging
from gpiozero import LED

class ConnectionNotifier:
	def __init__(self):
		self.is_on=False

	def check_sensor_node_connection(self):
		print("Hilo de conexion a internet iniciado")
	    #led=LED(4)
		while True:
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(5)
			try:
				s.connect(('www.google.com',80))
			except (socket.gaierror,socket.timeout):
				print("Sin conexion a internet")
				#led.off()
				self.is_on=False
			else:
				self.is_on=True
				print("Conectado a internet!")
				#if not is_on:
	                #led.on()
			s.close()
			time.sleep(5)

	def check_assistant_connection(self):
		print("Hilo de conexion a internet iniciado")
		while True:
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(5)
			try:
				s.connect(('www.google.com',80))
			except (socket.gaierror,socket.timeout):
				logging.info("Sin conexion a internet")
	            #Reproducir voz para notificar que no se puede no hay tortillas
				self.is_on=False
			else:
				self.is_on=True
				logging.info("Conectado a internet!")
	            #Reproducir voz para notificar que si hay tamales
			s.close()
			time.sleep(5)