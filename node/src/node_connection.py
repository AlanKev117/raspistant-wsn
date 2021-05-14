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

        # Tiempo de intervalo de polling e inicio de systemd
        time.sleep(5)

        # Polling de conexión local
        ip = subprocess.check_output("hostname -I",
                                     stderr=subprocess.STDOUT,
                                     shell=True).decode()
        if ip == "\n":
            changed = connected
            connected = False
        else:
            changed = not connected
            connected = True

        # Actualiza indicadores de conexión
        if first_time or changed:

            if connected:
                logging.info("Conectado a internet!")
                led.on()
            else:
                logging.error("Sin conexion a internet")
                led.off()

            first_time = False
