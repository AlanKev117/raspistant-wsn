import socket
import time
import logging
import subprocess
from .voice_interface import reproducir_audio
from gpiozero import LED


class ConnectionNotifier:
    def __init__(self):
        self.is_on = False

    def check_sensor_node_connection(self):
        logging.info("Hilo de conexion a internet iniciado")
        led = LED(18)
        while True:
            ip=subprocess.check_output("hostname -I",stderr=subprocess.STDOUT,shell=True).decode()
            if ip=="\n":
                logging.error("Sin conexion a internet")
                self.is_on = False
            else:
                self.is_on = True
                logging.info("Conectado a internet!")
            # Actualizar estado del led.
            if self.is_on:
            	#print("Encendido")
                led.on()
            else:
            	#print("Apagado")
                led.off()
            time.sleep(5)

    def check_assistant_connection(self):
        logging.info("Hilo de conexion a internet iniciado")
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            try:
                s.connect(('www.google.com', 80))
            except (socket.gaierror, socket.timeout):
                logging.error("Sin conexion a internet")
                if self.is_on:
                    reproducir_audio("/tmp/desconectado.mp3")
                self.is_on = False
            else:
                if self.is_on == False:
                    reproducir_audio("/tmp/conectado.mp3")
                self.is_on = True
                logging.info("Conectado a internet!")
            s.close()
            time.sleep(5)
