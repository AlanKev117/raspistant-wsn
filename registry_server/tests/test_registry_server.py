import time
from pathlib import Path
from multiprocessing import Process

import pytest
from rpyc.utils.registry import UDPRegistryClient

from registry_server.src.registry_server import registry_server as RegistryServer
from sensor_node.src.sensor_node import sensor_node as SensorNode

# Argumentos del servidor de registro
PORT = 18811  # puerto por defecto
PRUNING_TIME = 3

# Argumentos del nodo sensor
SENSOR_NAME = "aleatorio"
SENSOR_TYPE = "dummy"
SENSOR_SERVER_PORT = 4000


@pytest.fixture()
def registry_server():
    rs_process = Process(target=RegistryServer, args=(PORT, PRUNING_TIME), daemon=True)
    rs_process.start()
    return rs_process


@pytest.fixture()
def sensor_node():
    sn_process = Process(target=SensorNode, args=(SENSOR_NAME, SENSOR_TYPE, SENSOR_SERVER_PORT), daemon=True)
    sn_process.start()
    time.sleep(1)
    return sn_process

def test_registry_server(registry_server, sensor_node):
    """
    Se debe tener en ejecución una instancia de nodo sensor (sensor_node.py) de
    tipo "dummy", así como tener una instancia del servidor de registro
    (registry_server.py) en el puerto por defecto (18811) para correr el test.

    Se prueba que el nodo sensor pueda registrarse al servidor de registro y
    que este pueda proporcionar los datos de red de dicho nodo cuando se le
    consulte.
    """

    # Nos conectamos el servidor de registro
    rc = UDPRegistryClient()
    nodes = rc.discover("SENSORNODE")

    # Verificamos funcionamiento
    assert len(nodes) > 0, "Nodo sensor no encontrado"
    _, sensor_port = nodes[0]
    assert sensor_port == SENSOR_SERVER_PORT, "Nodo sensor no coincide"

    # Desactivamos el nodo sensor
    sensor_node.terminate()

    # Esperamos el tiempo de eliminación
    time.sleep(PRUNING_TIME)

    nodes = rc.discover("SENSORNODE")
    assert len(nodes) == 0, "Se descubrieron nodos sensores desactivados"
    registry_server.terminate()
