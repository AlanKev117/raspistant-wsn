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

""" Programa Principal del Nodo sensor.
    
    Este código se encarga de inicializar y ejecutar el programa del 
    nodo sensor y que a su vez se conecta a la red local del hogar 
    para que el asistente los identifique y pueda interactuar con ellos.

    Uso típico:
      python sensor_node.py
"""
import logging
import threading
import sys
import pathlib

import click
from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial
from rpyc.utils.registry import UDPRegistryClient

# Ruta del proyecto agregada a PATH para imports estáticos
PROJECT_DIR = str(pathlib.Path(__file__).parent.parent.parent.resolve())
sys.path.append(PROJECT_DIR)

from node.src.node_connection import check_node_connection
from node.src.node_service import SensorNodeService
from node.src.sensor import DummySensor, HallSensor, PIRSensor

# Configuraciones Iniciales.
@click.command()
@click.option('--node-name', default="aleatorio",
              metavar='<nombre del sensor>', show_default=True,
              help='Nombre con el que se llamará al nodo desde el asistente')
@click.option('--sensor-type', default="dummy",
              metavar='<tipo de sensor>', show_default=True,
              help='Tipo de sensor que se conectará al nodo.')
@click.option('--port', default=18861,
              metavar='<puerto>', show_default=True,
              help='Puerto por el que el nodo recibe peticiones de medición')
@click.option('--timeout', default=1,
              type=click.IntRange(0, 6, clamp=True),
              metavar='<minutos>', show_default=True,
              help=('Intervalo de tiempo en minutos que el nodo pasará sin '
                    'registrarse en el asistente de voz. Si es 0, el nodo '
                    'intentará registrarse múltiples veces por segundo.'))
@click.option('-v', '--verbose', 
              count=True, metavar="<-v * n veces>", 
              help=("Bandera que define el comportamiento de los logs."
                    "Mientras más repeticiones, se muestran más logs:\n"
                    "ninguna, sin logs; una, logs de nodo; dos o más, "
                    "logs de nodo y conexión."))
def main(node_name, sensor_type, port, timeout, verbose):
    """ Funcion principal

    Esta función es la que dispara el proceso principal que va a ejecutar
    el programa.

    Args:
        node_name:
            Nombre propio del nodo sensor.
        sensor_type:
            Tipo del nodo sensor.
        port:
            Puerto por el cual el nodo recibe las peticiones.
        timeout:
            Intervalo de tiempo en segundos que el asistente recordará un nodo
            que se acaba de registrar.
        verbose:
            Define el comportamiento de los logs.
    """  

    sensor_node_process(node_name, sensor_type, port, timeout, verbose)


def sensor_node_process(node_name, sensor_type, port, timeout, verbose):
    """ Proceso principal del nodo sensor

    Args:
        node_name:
            Nombre propio del nodo sensor.
        sensor_type:
            Tipo del nodo sensor.
        port:
            Puerto por el cual el nodo recibe las peticiones.
        timeout:
            Intervalo de tiempo en segundos que el asistente recordará un nodo
            que se acaba de registrar.
        verbose:
            Define el comportamiento de los logs.
    """  
    logging.basicConfig(level=logging.INFO if verbose else logging.ERROR)
    
    # Hilo de conexión
    conn_thread = threading.Thread(target=check_node_connection, 
                                   args=((verbose >= 2,)), 
                                   daemon=True)
    conn_thread.start()
    logging.info(f"Hilo de detección de conexión a red local iniciado.")

    # Preparamos el servicio de acuerdo con el tipo de sensor.
    sensor_types = {
        "dummy": DummySensor,
        "pir": PIRSensor,
        "hall": HallSensor
    }
    sensor = sensor_types[sensor_type](node_name)
    service = classpartial(SensorNodeService, sensor, verbose)

    # Loggers para servicio de medición y cliente de registro
    service_logger = logging.getLogger(f"NODE_SERVICE/{node_name}")
    service_logger.setLevel(logging.INFO if verbose else logging.WARNING)
    udp_logger = logging.getLogger("REGCLNT/UDP")
    udp_logger.setLevel(logging.INFO if verbose >= 2 else logging.WARNING)

    # Hilo de servicio de medición con su cliente de registro
    t = ThreadedServer(service, 
                       port=port,
                       registrar=UDPRegistryClient(timeout=timeout,
                                                   logger=udp_logger), 
                       logger=service_logger)
    t.start()
    logging.info(f"Hilo de servicio de medición iniciado.")

    # Desactiva pin de entrada de sensor al finalizar proceso.
    sensor.deactivate()


if __name__ == "__main__":
    main()
