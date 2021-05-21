import logging
import sys
import pathlib
import threading
import os

import click

# Ruta del proyecto agregada a PATH para imports estáticos
PROJECT_DIR = str(pathlib.Path(__file__).parent.parent.parent.resolve())
sys.path.append(PROJECT_DIR)

from hub.src.assistant_connection import check_assistant_connection
from hub.src.voice_interface import (
    hablar,
    ERROR_AUDIO_PATH,
    TELLME_AUDIO_PATH,
    SHUTDOWN_AUDIO_PATH,
)
from hub.src.registry_server import registry_server
from hub.src.hub_assistant import HubAssistant, DEVICE_CONFIG_PATH
from hub.src.triggers import (
    get_trigger_function,
    wait_for_hot_word, 
    wait_for_button_pressed_and_released
)

@click.command()
@click.option('--device-model-id', '--model',
              metavar='<device model id>',
              help=(('Identificador del modelo registrado del dispositivo. '
                     'Si no se especifica, se lee del archivo '
                     f'{DEVICE_CONFIG_PATH}. ')))
@click.option('--device-id', '--device',
              metavar='<device id>',
              help=(('Identificador de instancia registrada del dispositivo. '
                     'Si no se especifica, se lee del archivo '
                     f'{DEVICE_CONFIG_PATH}. '
                     'Si no se encuentra el archivo, se darán instrucciones '
                     'avanzadas.')))
@click.option('--trigger',
              default="button",
              type=click.Choice(["button", "key", "word"]),
              help=(('Forma de activar el asistente')))                     
@click.option('--word',
              metavar='<palabra o frase corta>',
              default=None,
              help=(('Palabra clave para activar el asistente. '
                     'Útil solo para --trigger = word')))
@click.option('--timeout', default=65,
              type=click.IntRange(5, 365, clamp=True),
              metavar='<segundos>', show_default=True,
              help=('Intervalo de tiempo en segundos que el asistente '
                    'recordará un nodo que se acaba de registrar.'))
@click.option('-v', '--verbose', 
              count=True, metavar="<-v -vv -vvv ...>", 
              help=("Define el comportamiento de los logs. "
                    "Mientras más repeticiones, se muestran más logs:\n"
                    "ninguna, sin logs; una, logs de asistente; dos o más, "
                    "logs de asistente y conexión."))
def main(device_model_id, device_id, trigger, word, timeout, verbose):

    # Configuración del logger
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)

    # Bandera de estado de conexión a internet.
    # Será manejada por hilo de detección de conexión a internet.
    status = {"online": False}

    # Iniciamos detector de conexión a internet.
    conn_thread = threading.Thread(target=check_assistant_connection,
                                   args=(status, verbose >= 2),
                                   daemon=True)
    conn_thread.start()
    logging.info("Hilo de conexión a internet iniciado.")

    # Pausamos creación de servidor de registro hasta detectar conexión.
    while not status["online"]:
        pass

    # Iniciamos servidor de registro
    rs_process = threading.Thread(target=registry_server,
                                  args=(18811, timeout, verbose >= 2),
                                  daemon=True)
    rs_process.start()
    logging.info("Hilo de servidor de registro iniciado.")

    # Habilitamos apagado por botón integrado.
    try:
        
        def shutdown_callback():
            hablar(text=None, cache=SHUTDOWN_AUDIO_PATH)
            os.system("sudo halt")
        
        button = Button(19, hold_time=10)
        button.when_held = shutdown_callback
    except:
        logging.warning("Tu dispositivo no podrá ser apagado mediante botón")
    
    # Configuración del detonador: botón, tecla, palabra/frase.
    try:
        if trigger == "button":
            wait_for_trigger = get_trigger_function(
                "Presiona el botón para activar el asistente...",
                lambda: wait_for_button_pressed_and_released(button)
            )
        elif trigger == "key":
            wait_for_trigger = get_trigger_function(
                "Presiona una tecla para activar el asistente...",
                lambda: click.pause(None)
            )
        else: # trigger == "word"
            wait_for_trigger = get_trigger_function(
                f"Di '{word}' para activar el asistente...",
                lambda: wait_for_hot_word(word)
            )
    except:
        logging.error("Error al configurar el activador del asistente.")
        sys.exit(-1)


    try:

        with HubAssistant(device_model_id, device_id) as hub_assistant:

            # Esperamos por un detonador para la primer conversación.
            keep_conversation = False

            # Bucle de asistente.
            while True:

                if not status["online"]:
                    continue

                if not keep_conversation:                    
                    wait_for_trigger()
                    hablar(text=None, cache=TELLME_AUDIO_PATH)

                keep_conversation = hub_assistant.assist()

    except Exception as e:
        logging.error("Ocurrió un error inesperado en el asistente.")
        hablar(text=None, cache=ERROR_AUDIO_PATH)
        raise e

if __name__ == '__main__':
    main()
