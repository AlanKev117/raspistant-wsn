import time
import logging
import subprocess

from gpiozero import LED

CONNECTION_LED_PIN = 25

def check_node_connection():
    
    logging.info("Hilo de conexion a red local iniciado")

    connected = False
    changed = False
    first_time = True
    led = LED(CONNECTION_LED_PIN)

    while True:
        
        ip = subprocess.check_output("hostname -I",
                                        stderr=subprocess.STDOUT,
                                        shell=True).decode()
        if ip == "\n":
            changed = connected
            connected = False
            led.off()
        else:
            changed = not connected
            connected = True
            led.on()

        # Actualiza log de estado de conexión.
        if first_time or changed:
            
            if connected:
                logging.info("Conectado a internet!")
            else:
                logging.error("Sin conexion a internet")
            
            first_time = False


        time.sleep(5)

    
