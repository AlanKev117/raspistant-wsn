import socket
import time
import logging

from hub.src.voice_interface import hablar, OFFLINE_AUDIO_PATH, ONLINE_AUDIO_PATH

def check_assistant_connection(status, verbose):

    logger = logging.getLogger("ASSISTANT_CONNECTION")
    logger.setLevel(logging.INFO if verbose else logging.WARNING)
    
    connected = False
    changed = False
    first_time = True

    while True:

        # Polling de conexión a internet
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect(('www.google.com', 80))
        except (socket.gaierror, socket.timeout):
            changed = connected
            connected = False
        else:
            changed = not connected
            connected = True
        s.close()

        # Actualiza indicadores de conexión
        if first_time or changed:

            if connected:
                logger.info("Conectado a internet!")
                hablar(text=None, cache=ONLINE_AUDIO_PATH)
                status["online"] = True
            else:
                logger.error("Sin conexion a internet!")
                if status["assistant-running"]:
                    hablar(text=None, cache=OFFLINE_AUDIO_PATH)
                status["online"] = False

            first_time = False

        # Tiempo de polling e inicio de espera para systemd
        time.sleep(5)
        