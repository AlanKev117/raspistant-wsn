import logging
import sys
import pathlib
import threading

import click

# Ruta del proyecto agregada a PATH para imports estáticos
PROJECT_DIR = str(pathlib.Path(__file__).parent.parent.parent.resolve())
sys.path.append(PROJECT_DIR)

from hub.src.triggers import define_trigger_waiter
from hub.src.hub_assistant import HubAssistant
from hub.src.registry_server import registry_server


# Información de la entidad registrada en la consola de acciones de Google
DEVICE_MODEL_ID = "wsn-hub"
DEVICE_ID = "pi-hub"

# Botón para realizar las consultas, si es necesario
BUTTON_GPIO_PIN = 19


@click.command()
@click.option('--trigger',
              default="button",
              show_default=True,
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
def main(trigger, word, timeout, verbose):

    # Configuración del logger
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)

    # Verificamos que los argumentos de activación sean válidos
    wait_for_trigger = define_trigger_waiter(trigger, word, BUTTON_GPIO_PIN)


    try:

        # Iniciamos servidor de registro
        rs_process = threading.Thread(target=registry_server,
                                    args=(18811, timeout, verbose >= 2),
                                    daemon=True)
        rs_process.start()
        logging.info("Servidor de registro iniciado.")

        with HubAssistant(DEVICE_MODEL_ID, DEVICE_ID) as hub_assistant:
            
            # Esperamos por un detonador para la primer conversación.
            keep_conversation = False

            # Bucle de asistente.
            while True:

                if not keep_conversation:
                    wait_for_trigger()

                keep_conversation = hub_assistant.assist()

    except Exception as e:
        logging.error("Ocurrió un error inesperado en el asistente.")
        raise e


if __name__ == '__main__':
    main()
