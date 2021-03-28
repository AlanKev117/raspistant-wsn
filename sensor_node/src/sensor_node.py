import click
from rpyc.utils.server import ThreadedServer, OneShotServer
from rpyc.utils.helpers import classpartial
from rpyc.utils.registry import UDPRegistryClient

try:
    from .node_service import SensorNodeService
    from .sensor import *
except (SystemError, ImportError):
    from node_service import SensorNodeService
    from sensor import *


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
def main(sensor_name, sensor_type, server_port):
    sensor_node(sensor_name, sensor_type, server_port)

def sensor_node(sensor_name, sensor_type, server_port):
    sensor_types = {
        "dummy": DummySensor,
        "pir": PIRSensor
    }

    sensor = sensor_types[sensor_type](sensor_name)
    service = classpartial(SensorNodeService, sensor)
    
    t = ThreadedServer(service, port=server_port, registrar=UDPRegistryClient(timeout=0))
    print(f"Nodo sensor {sensor_name} iniciado.")
    t.start()
    sensor.deactivate()

if __name__ == "__main__":
    main()
