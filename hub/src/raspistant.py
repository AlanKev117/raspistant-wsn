import logging
import sys
import pathlib
import click
import threading

# Para uso de imports estáticos, añadimos la ruta del proyecto al sys path.
PROJECT_DIR = str(pathlib.Path(__file__).parent.parent.parent.resolve())
sys.path.append(PROJECT_DIR)

from misc.connection_notifier import ConnectionNotifier
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
@click.option('--trigger', '-t',
              type=click.Choice(['keystroke', 'hotword']),
              default='keystroke',
              help=(('Seleccione "keystroke" para activar el asistente con '
                     'cualquier tecla del teclado o seleccione "hotword" para '
                     'activarlo al pronunciar "Ok Google".')))
@click.option('--verbose', '-v',
              is_flag=True,
              default=False,
              help='Verbose logging.')
def main(device_model_id, device_id, trigger, verbose):

    # Configuración del logger.
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)

    # Iniciamos detector de conexión a internet.
    conexion = ConnectionNotifier()
    hilo_internet = threading.Thread(
        target=conexion.check_assistant_connection, daemon=True)
    hilo_internet.start()

    try:

        with HubAssistant(device_model_id, device_id) as hub_assistant:

            # Esperamos por un detonador para la primer conversación.
            wait_for_trigger = True

            # Bucle de asistente.
            while True:
                if wait_for_trigger:
                    if trigger == "keystroke":
                        click.pause(info=('Presiona una tecla para activar '
                                          'el asistente...'))
                    else:
                        print('Di "Ok, Google" para activar el asistente...')
                        hub_assistant.wait_for_hot_word("ok google")
                keep_conversation = hub_assistant.assist()
                
                # Esperar otro detonador si la conversación terminó
                wait_for_trigger = not keep_conversation

    except Exception as e:
        logging.error("Error en asistente.", stack_info=True)
        logging.error(e)


if __name__ == '__main__':
    main()
