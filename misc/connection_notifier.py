import socket
import time
import logging
import subprocess
from gpiozero import LED

from misc.voice_interface import hablar, OFFLINE_AUDIO_PATH, ONLINE_AUDIO_PATH

CONNECTION_LED_PIN = 25

class ConnectionNotifier:
    def __init__(self):
        self.is_on = False

    def check_sensor_node_connection(self):
        
        logging.info("Hilo de conexion a internet iniciado")
        led = LED(CONNECTION_LED_PIN)
        
        while True:
            ip = subprocess.check_output("hostname -I",
                                         stderr=subprocess.STDOUT,
                                         shell=True).decode()
            if ip == "\n":
                logging.error("Sin conexion a internet")
                self.is_on = False
            else:
                logging.info("Conectado a internet!")
                self.is_on = True
            
            # Actualizar estado del led.
            if self.is_on:
            	#print("Encendido")
                led.on()
            else:
            	#print("Apagado")
                led.off()
            
            time.sleep(5)

    def check_assistant_connection(self):
        
        changed = False
        first_time = True
        logging.info("Hilo de conexion a internet iniciado")
        
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            try:
                s.connect(('www.google.com', 80))
            except (socket.gaierror, socket.timeout):
                changed = self.is_on
                self.is_on = False
            else:
                changed = not self.is_on
                self.is_on = True
            s.close()


            if first_time or changed:

                if self.is_on:
                    logging.info("Conectado a internet!")
                    hablar(text=None, cache=ONLINE_AUDIO_PATH)
                else:
                    logging.error("Sin conexion a internet!")
                    hablar(text=None, cache=OFFLINE_AUDIO_PATH)

                first_time = False

            time.sleep(5)
            