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
@click.option('--name', default="aleatorio",
              metavar='<nombre del sensor>', show_default=True,
              help='Nombre con el que se llamará al nodo desde el asistente')
@click.option('--type', default="dummy",
              metavar='<tipo de sensor>', show_default=True,
              help='Tipo de sensor que se conectará al nodo.')
@click.option('--port', default=18861,
              metavar='<puerto>', show_default=True,
              help='Puerto por el que el nodo recibe peticiones de medición')
@click.option('--verbose', '-v', is_flag=True, help='Modo verbose')
def main(sensor_name, sensor_type, server_port, verbose):
    logging.basicConfig(level=logging.INFO if verbose else logging.ERROR)
    sensor_node_process(sensor_name, sensor_type, server_port)


def sensor_node_process(name, type, port):
    sensor_types = {
        "dummy": DummySensor,
        "pir": PIRSensor,
        "hall": HallSensor
    }

    sensor = sensor_types[type](name)
    service = classpartial(SensorNodeService, sensor)

    hilo_internet = threading.Thread(
        target=check_node_connection, daemon=True)
    hilo_internet.start()

    t = ThreadedServer(service, port=port,
                       registrar=UDPRegistryClient(timeout=0))
    logging.info(f"Nodo sensor {name} iniciado.")
    t.start()
    sensor.deactivate()


if __name__ == "__main__":
    main()
