import socket
import time
import logging

from hub.src.voice_interface import (
    hablar,
    OFFLINE_AUDIO_PATH,
    ONLINE_AUDIO_PATH
)

from hub.src.triggers import speak_lock

POLLING_PAUSE_TIME = 3
CONNECTION_TEST_ADDRESS = "assistant.googleapis.com"
CONNECTION_TEST_PORT = 80

def check_assistant_connection(status, verbose):

    logger = logging.getLogger("ASSISTANT_CONNECTION")
    logger.setLevel(logging.INFO if verbose else logging.WARNING)
    
    connected = None
    notify = False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        s.settimeout(5)
        
        # Polling de conexión a internet
        while True:

            try:
                s.connect((CONNECTION_TEST_ADDRESS, CONNECTION_TEST_PORT))
            # Error externo de conexión
            except socket.timeout:
                notify = connected in (None, True)
                connected = False
            # Error interno de conexión
            except:
                continue
            # Sin error
            else:
                notify = connected in (None, False)
                connected = True

            # Actualiza indicadores de conexión
            if notify:
                if connected:
                    logger.info("Conectado a internet!")
                    status["online"] = True
                    audio_path = ONLINE_AUDIO_PATH
                else:
                    logger.error("Sin conexion a internet!")
                    status["online"] = False
                    audio_path = OFFLINE_AUDIO_PATH
                speak_lock.acquire()
                hablar(text=None, cache=audio_path)
                speak_lock.release()

            # Tiempo de polling e inicio de espera para systemd
            time.sleep(POLLING_PAUSE_TIME)
            