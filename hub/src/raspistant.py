# Copyright 2021 Alan Fuentes
# Copyright 2021 Yael Estrada
# Copyright 2021 Noé Acosta

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Programa Principal del Hub Asistente.
    
    Este código se encarga de inicializar y ejecutar el programa del 
    asistente de voz y que a su vez se conecta a los nodos sensores e 
    interactua con ellos mediante RPC.

    Uso típico:
      python raspistant.py
"""

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

# Configuraciones Iniciales.
@click.command()
@click.option('--model',
              default=DEVICE_MODEL_ID,
              metavar='<id de modelo>',
              help=("ID del modelo del dispositivo"))
@click.option('--device',
              default=DEVICE_ID,
              metavar='<id de dispositivo>',
              help=("ID de la instancia de un modelo de dispositivo"))
@click.option('--trigger',
              default="button",
              show_default=True,
              type=click.Choice(["button", "key"]),
              help=(('Forma de activar el asistente')))
@click.option('--timeout',
              default=65,
              type=click.IntRange(5, 365, clamp=True),
              metavar='<segundos>',
              show_default=True,
              help=('Intervalo de tiempo en segundos que el asistente '
                    'recordará un nodo que se acaba de registrar.'))
@click.option('-v', '--verbose',
              count=True,
              metavar="<-v -vv -vvv ...>",
              help=("Define el comportamiento de los logs. "
                    "Mientras más repeticiones, se muestran más logs:\n"
                    "ninguna, sin logs; una, logs de asistente; dos o más, "
                    "logs de asistente y conexión."))
def main(model, device, trigger, timeout, verbose):
    raspistant_process(model, device, trigger, timeout, verbose)


def raspistant_process(model, device, trigger, timeout, verbose):
    """ Proceso del asistente de voz.

        Esta función es la que dispara el proceso principal que va a ejecutar
        el programa.

        Args:
          model:
            ID del modelo de dispositivo creado en la consola de acciones.
          device:
            ID del dispositivo creado en la consola de acciones.
          trigger:
            Activador para el lanzamiento del asistente.
          word:
            Palabra clave para activar el asistente.
          timeout:
            Intervalo de tiempo en segundos que el asistente recordará un nodo
            que se acaba de registrar.
          verbose:
            Define el comportamiento de los logs.

    """
    
    # Configuración del logger
    assistant_logger = logging.getLogger("ASSISTANT")
    assistant_logger.setLevel(logging.INFO if verbose else logging.WARNING)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO if verbose else logging.WARNING)
    formatter = logging.Formatter(
      fmt='%(levelname)s - %(name)s - %(asctime)s.%(msecs)03d - %(message)s', 
      datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    assistant_logger.addHandler(handler)

    # Verificamos que los argumentos de activación sean válidos
    wait_for_trigger = define_trigger_waiter(trigger, BUTTON_GPIO_PIN)

    try:

        # Iniciamos servidor de registro
        rs_process = threading.Thread(target=registry_server,
                                      args=(18811, timeout, verbose >= 2),
                                      daemon=True)
        rs_process.start()
        assistant_logger.info("Servidor de registro iniciado.")

        with HubAssistant(model, device) as hub_assistant:

            # Esperamos por un detonador para la primer conversación.
            keep_conversation = False

            # Bucle de asistente.
            while True:

                if not keep_conversation:
                    wait_for_trigger()

                keep_conversation = hub_assistant.assist()

    except Exception as e:
        assistant_logger.error("Ocurrió un error inesperado en el asistente.")
        raise e


if __name__ == '__main__':
    main()
