import time
import logging
import subprocess

from gpiozero import LED

CONNECTION_LED_PIN = 25

def check_node_connection(self):
    
    self.is_on = False

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
            led.on()
        else:
            led.off()

        time.sleep(5)

    
