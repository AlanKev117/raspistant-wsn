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

from sensor_node.src.node_service import SensorNodeService
from sensor_node.src.sensor import Sensor, DummySensor, HallSensor, PIRSensor
from misc.connection_notifier import ConnectionNotifier

@click.command()
@click.option('--sensor-name', default="aleatorio",
              metavar='<nombre del sensor>', show_default=True,
              help='Nombre con el que se llamará al nodo desde el asistente')
@click.option('--sensor-type', default="dummy",
              metavar='<tipo de sensor>', show_default=True,
              help='Tipo de sensor que se conectará al nodo.')
@click.option('--server-port', default=18861,
              metavar='<puerto>', show_default=True,
              help='Puerto por el que el nodo recibe peticiones de medición')
@click.option('--verbose', '-v', is_flag=True, help='Modo verbose')
def main(sensor_name, sensor_type, server_port, verbose):
    logging.basicConfig(level=logging.INFO if verbose else logging.ERROR)
    sensor_node(sensor_name, sensor_type, server_port)


def sensor_node(sensor_name, sensor_type, server_port):
    sensor_types = {
        "dummy": DummySensor,
        "pir": PIRSensor,
        "hall": HallSensor
    }

    sensor = sensor_types[sensor_type](sensor_name)
    service = classpartial(SensorNodeService, sensor)

    conexion = ConnectionNotifier()
    hilo_internet = threading.Thread(
        target=conexion.check_sensor_node_connection, daemon=True)
    hilo_internet.start()

    t = ThreadedServer(service, port=server_port,
                       registrar=UDPRegistryClient(timeout=0))
    logging.info(f"Nodo sensor {sensor_name} iniciado.")
    t.start()
    sensor.deactivate()


if __name__ == "__main__":
    main()
