import logging
from os import stat
import threading
import sys
import pathlib

import click
from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial
from rpyc.utils.registry import UDPRegistryClient

PROJECT_DIR = str(pathlib.Path(__file__).parent.parent.parent.resolve())
sys.path.append(PROJECT_DIR)

from node.src.node_connection import check_node_connection
from node.src.node_service import SensorNodeService
from node.src.sensor import DummySensor, HallSensor, PIRSensor

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
@click.option('--verbose', '-v', is_flag=True, help='Modo verbose')
def main(node_name, sensor_type, port, timeout, verbose):
    sensor_node_process(node_name, sensor_type, port, timeout, verbose)


def sensor_node_process(node_name, sensor_type, port, timeout, verbose):
    
    logging.basicConfig(level=logging.INFO if verbose else logging.ERROR)
    
    sensor_types = {
        "dummy": DummySensor,
        "pir": PIRSensor,
        "hall": HallSensor
    }

    sensor = sensor_types[sensor_type](node_name)
    service = classpartial(SensorNodeService, sensor, verbose)
    status = {"online": False}


    # Hilo de conexión
    conn_thread = threading.Thread(target=check_node_connection, 
                                   args=(status, verbose), 
                                   daemon=True)
    conn_thread.start()
    logging.info(f"Hilo de detección de conexión a red local iniciado.")

    while not status["online"]:
        pass

    # Hilo de servicio de medición
    t = ThreadedServer(service, 
                       port=port,
                       registrar=UDPRegistryClient(timeout=timeout))
    t.start()
    logging.info(f"Hilo de servicio de medición iniciado.")

    # Desactiva pin de entrada de sensor
    sensor.deactivate()


if __name__ == "__main__":
    main()
