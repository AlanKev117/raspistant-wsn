import time
import logging
import subprocess

from gpiozero import LED

CONNECTION_LED_PIN = 25


def check_node_connection(verbose):

    logger = logging.getLogger("NODE_CONNECTION")
    logger.setLevel(logging.INFO if verbose else logging.WARNING)

    connected = None
    changed = False
    
    with LED(CONNECTION_LED_PIN) as led:

        while True:

            # Tiempo de intervalo de polling e inicio de systemd
            time.sleep(5)

            # Polling de conexión local
            ip = subprocess.check_output("hostname -I",
                                        stderr=subprocess.STDOUT,
                                        shell=True).decode()
            if ip == "\n":
                changed = connected in (True, None)
                connected = False
            else:
                changed = connected in (False, None)
                connected = True

            # Actualiza indicadores de conexión
            if changed:

                if connected:
                    logger.info("Conectado a la red local!")
                    led.on()
                else:
                    logger.error("Sin conexion a la red local")
                led.off()
