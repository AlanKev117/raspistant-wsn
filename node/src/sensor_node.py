import logging
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
              type=click.IntRange(0, 15, clamp=True),
              metavar='<minutos>', show_default=True,
              help=('Intervalo de tiempo en minutos que el nodo pasará sin '
                    'registrarse en el asistente de voz. Si es 0, '))
@click.option('--verbose', '-v', is_flag=True, help='Modo verbose')
def main(node_name, sensor_type, port, timeout, verbose):
    logging.basicConfig(level=logging.INFO if verbose else logging.ERROR)
    sensor_node_process(node_name, sensor_type, port)


def sensor_node_process(node_name, sensor_type, port, timeout):
    sensor_types = {
        "dummy": DummySensor,
        "pir": PIRSensor,
        "hall": HallSensor
    }

    sensor = sensor_types[sensor_type](node_name)
    service = classpartial(SensorNodeService, sensor)

    hilo_internet = threading.Thread(
        target=check_node_connection, daemon=True)
    hilo_internet.start()

    t = ThreadedServer(service, port=port,
                       registrar=UDPRegistryClient(timeout=1))
    logging.info(f"Nodo sensor {node_name} iniciado.")
    t.start()
    sensor.deactivate()


if __name__ == "__main__":
    main()
