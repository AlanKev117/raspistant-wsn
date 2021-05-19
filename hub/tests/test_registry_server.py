import time
from multiprocessing import Process

import pytest
from rpyc.utils.registry import UDPRegistryClient

from hub.src.registry_server import registry_server
from sensor_node.src.sensor_node import sensor_node

# Argumentos del servidor de registro
PORT = 18811  # puerto por defecto
PRUNING_TIME = 3 # segundos de tiempo de eliminación

# Argumentos del nodo sensor
SENSOR_NAME = "prueba"
SENSOR_TYPE = "dummy"
SENSOR_SERVER_PORT = 4000


@pytest.fixture
def registry_server_process():
    rs_process = Process(target=registry_server,
                         args=(PORT, PRUNING_TIME),
                         daemon=True)
    rs_process.start()

    return rs_process


@pytest.fixture
def sensor_node_process():
    sn_process = Process(target=sensor_node,
                         args=(SENSOR_NAME, SENSOR_TYPE, SENSOR_SERVER_PORT),
                         daemon=True)
    sn_process.start()

    # Tiempo de tolerancia para que el nodo se registre en el servidor
    time.sleep(1)

    return sn_process


def test_registry_server(registry_server_process, sensor_node_process):
    """
    Se prueba que el nodo sensor pueda registrarse al servidor de registro y
    que este pueda proporcionar los datos de red de dicho nodo cuando se le
    consulte.
    """

    # Iniciamos cliente UDP para servidor de registro
    rc = UDPRegistryClient() # el puerto por defecto es PORT

    # Solicitamos los datos del nodo que se creó
    nodes = rc.discover("SENSORNODE")

    # Verificamos que recibimos datos de nodos
    assert len(nodes) > 0, "Nodo sensor no encontrado"

    # Verificamos que sean los datos del nodo inicializado
    _, sensor_port = nodes[0]
    assert sensor_port == SENSOR_SERVER_PORT, "Nodo sensor no coincide"

    sensor_node_process.terminate()

    # Esperamos que el servidor de registro elimine el nodo sensor
    time.sleep(PRUNING_TIME)

    # Descubrimos nuevamente nodos, no deberíamos encontrar ninguno
    nodes = rc.discover("SENSORNODE")
    assert len(nodes) == 0, "Se descubrieron nodos sensores desactivados"

    registry_server_process.terminate()
