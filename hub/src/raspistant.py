import logging
import sys
import pathlib
import threading

import click

# Append project path to PATH for following absolute imports work
PROJECT_DIR = str(pathlib.Path(__file__).parent.parent.parent.resolve())
sys.path.append(PROJECT_DIR)

from hub.src.assistant_connection import check_assistant_connection
from hub.src.voice_interface import hablar, TELL_ME_PATH
from hub.src.registry_server import registry_server
from hub.src.hub_assistant import HubAssistant, DEVICE_CONFIG_PATH

@click.command()
@click.option('--device-model-id', '--model',
              metavar='<device model id>',
              help=(('Identificador del modelo registrado del dispositivo. '
                     'Si no se especifica, se lee del archivo '
                     f'{DEVICE_CONFIG_PATH}. '
                     'Si no se encuentra el archivo, se darán instrucciones '
                     'avanzadas.')))
@click.option('--device-id', '--device',
              metavar='<device id>',
              help=(('Identificador de instancia registrada del dispositivo. '
                     'Si no se especifica, se lee del archivo '
                     f'{DEVICE_CONFIG_PATH}. '
                     'Si no se encuentra el archivo, se darán instrucciones '
                     'avanzadas.')))
@click.option('--trigger-word', '--word',
              metavar='<palabra>',
              default=None,
              help=(('Palabra clave para activar el asistente. '
                     'Si no se especifica, la activación se da '
                     'presionando una tecla')))
@click.option('--verbose', '-v',
              is_flag=True,
              default=False,
              help='Verbose logging.')
def main(device_model_id, device_id, trigger_word, verbose):

    # Configuración del logger.
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)

    # Iniciamos detector de conexión a internet.
    hilo_internet = threading.Thread(
        target=check_assistant_connection, daemon=True)
    hilo_internet.start()

    # Iniciamos servidor de registro
    rs_process = threading.Thread(target=registry_server,
                                  args=(18811, 5),
                                  daemon=True)
    rs_process.start()

    try:

        with HubAssistant(device_model_id, device_id) as hub_assistant:

            # Esperamos por un detonador para la primer conversación.
            wait_for_trigger = True

            # Bucle de asistente.
            while True:

                if wait_for_trigger:
                    if trigger_word is None:
                        click.pause(info=('Presiona una tecla para activar '
                                          'el asistente...'))
                    else:
                        print(f'Di "{trigger_word}" para activar el asistente...')
                        hub_assistant.wait_for_hot_word(trigger_word)
                    hablar(text=None, cache=TELL_ME_PATH)

                keep_conversation = hub_assistant.assist()

                # Esperar otro detonador si la conversación terminó
                wait_for_trigger = not keep_conversation

    except Exception as e:
        logging.error("Error en asistente.", stack_info=True)
        logging.error(e)


if __name__ == '__main__':
    main()
