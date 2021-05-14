import socket
import time
import logging

from hub.src.voice_interface import hablar, OFFLINE_AUDIO_PATH, ONLINE_AUDIO_PATH

def check_assistant_connection():

    logging.info("Hilo de conexion a internet iniciado")
    
    connected = False
    changed = False
    first_time = True

    while True:
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
                logging.info("Conectado a internet!")
                hablar(text=None, cache=ONLINE_AUDIO_PATH)
            else:
                logging.error("Sin conexion a internet!")
                hablar(text=None, cache=OFFLINE_AUDIO_PATH)

            first_time = False

        time.sleep(5)
