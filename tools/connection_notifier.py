import socket
import time
import logging
from gpiozero import LED


class ConnectionNotifier:
    def __init__(self):
        self.is_on = False

    def check_sensor_node_connection(self):
        print("Hilo de conexion a internet iniciado")
        #led = LED(18)
        while True:
            ip=socket.gethostbyname(socket.gethostname())
            add=str(ip)
            if add.startswith("127.0.0"):
                print("Sin conexion a internet")
                self.is_on = False
            else:
                self.is_on = True
                print("Conectado a internet!")
            # Actualizar estado del led.
            if self.is_on:
                led.on()
            else:
                led.off()
            time.sleep(5)

    def check_assistant_connection(self):
        print("Hilo de conexion a internet iniciado")
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            try:
                s.connect(('www.google.com', 80))
            except (socket.gaierror, socket.timeout):
                logging.info("Sin conexion a internet")
                self.is_on = False
            else:
                self.is_on = True
                logging.info("Conectado a internet!")
            s.close()

            # Actualizar estado de conexión.
            if self.is_on:
                # Reproducir voz para notificar que si hay tamales
            else:
                # Reproducir voz para notificar que no se puede no hay tortillas
            time.sleep(5)
