import time
import logging
import subprocess

from gpiozero import LED

CONNECTION_LED_PIN = 25

def check_node_connection():
    
    connected = False

    logging.info("Hilo de conexion a internet iniciado")
    led = LED(CONNECTION_LED_PIN)

    while True:
        ip = subprocess.check_output("hostname -I",
                                        stderr=subprocess.STDOUT,
                                        shell=True).decode()
        if ip == "\n":
            logging.error("Sin conexion a internet")
            connected = False
        else:
            logging.info("Conectado a internet!")
            connected = True

        # Actualizar estado del led.
        if connected:
            led.on()
        else:
            led.off()

        time.sleep(5)

    
