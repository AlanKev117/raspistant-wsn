import socket
import time
import logging

from hub.src.voice_interface import hablar, OFFLINE_AUDIO_PATH, ONLINE_AUDIO_PATH

def check_assistant_connection(status, verbose):

    logger = logging.getLogger("ASSISTANT_CONNECTION")
    h = logging.StreamHandler()
    f = logging.Formatter("%(levelname)s:%(name)s:%(msg)s")
    h.setFormatter(f)
    logger.addHandler(h)
    logger.setLevel(logging.INFO if verbose else logging.WARNING)
    
    connected = False
    changed = False
    first_time = True

    while True:
        
        # Tiempo de polling e inicio de espera para systemd
        time.sleep(5)

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
                status["online"] = True
                hablar(text=None, cache=ONLINE_AUDIO_PATH)
            else:
                logger.error("Sin conexion a internet!")
                status["online"] = False
                hablar(text=None, cache=OFFLINE_AUDIO_PATH)

            first_time = False

        
