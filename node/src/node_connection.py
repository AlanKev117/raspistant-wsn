import time
import logging
import subprocess

from gpiozero import LED

CONNECTION_LED_PIN = 25


def check_node_connection(status, verbose):

    logger = logging.getLogger("NODE_CONNECTION")
    logger.setLevel(logging.INFO if verbose else logging.WARNING)

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
                logger.info("Conectado a la red local!")
                status["online"] = True
                led.on()
            else:
                logger.error("Sin conexion a la red local")
                status["online"] = False
                led.off()

            first_time = False
