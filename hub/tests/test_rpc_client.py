import time
from multiprocessing import Process

import pytest

from registry_server.src.registry_server import registry_server
from sensor_node.src.sensor_node import sensor_node
from hub.src.rpc_client import RPCClient

# Argumentos del servidor de registro
PORT = 18811  # puerto por defecto
PRUNING_TIME = 3  # segundos de tiempo de eliminación

# Argumentos del nodo sensor (nombre, tipo, puerto)
SENSOR_1_ARGS = ("prueba a", "dummy", 4000)
SENSOR_2_ARGS = ("prueba b", "dummy", 5000)
SENSORS_ARGS = [SENSOR_1_ARGS, SENSOR_2_ARGS]


@pytest.fixture
def registry_server_process():
    rs_process = Process(target=registry_server,
                         args=(PORT, PRUNING_TIME),
                         daemon=True)
    rs_process.start()

    return rs_process


@pytest.fixture
def dummy_nodes():
    dummy_nodes_list = []

    for sensor_args in SENSORS_ARGS:
        sn_process = Process(target=sensor_node,
                             args=sensor_args,
                             daemon=True)
        sn_process.start()
        dummy_nodes_list.append(sn_process)

    # Tiempo de tolerancia para que los nodos se registren en el servidor
    time.sleep(1)

    return dummy_nodes_list


def test_rpc_client(registry_server_process, dummy_nodes):
    """
    Se prueba que el cliente RPC que corre en el asistente de voz, sea capaz de
    detectar nodos sensores y solicitar mediciones de los mismos.
    """

    rpc_client = RPCClient()
    NUMBER_OF_NODES = len(dummy_nodes)
    # Dos nodos a probarse
    for i in range(NUMBER_OF_NODES, -1, -1):
        
        nodes = rpc_client.discover_sensor_nodes()

        assert len(nodes) == i, "Error al descubrir nodos sensores"

        for sensor_name, _, sensor_port in SENSORS_ARGS[:i]:
            assert sensor_name in nodes, f"Nodo {sensor_name} no identificado"
            assert sensor_port == nodes[sensor_name][1], f"Puerto difiere para nodo {sensor_name}"

        for sensor_name in nodes:
            reading = rpc_client.get_sensor_reading(sensor_name)
            assert reading in (True, False), "Error en medición de nodo"
        
        if i > 0:
            # Esperamos que el servidor de registro elimine el nodo sensor
            dummy_nodes[i - 1].terminate()
            time.sleep(PRUNING_TIME)

    registry_server_process.terminate()
