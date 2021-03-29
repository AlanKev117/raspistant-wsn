import logging
from multiprocessing import Process

import pytest

from hub.src.rpc_client import RPCClient, RepeatedNodeNameError

# Argumentos del servidor de registro
PORT = 18811  # puerto por defecto
PRUNING_TIME = 3  # segundos de tiempo de eliminación

# Argumentos del nodo sensor (nombre, tipo, puerto)
SENSOR_1_ARGS = ("prueba a", "dummy", 4000)
SENSOR_2_ARGS = ("prueba b", "dummy", 5000)
SENSORS_ARGS = [SENSOR_1_ARGS, SENSOR_2_ARGS]

@pytest.fixture
def logger():
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger()


def rpc_integration_test(logger):
    """
    Se prueba el correcto funcionamiento en conjunto de los nodos sensores,
    el cliente rpc del asistente de voz y el servidor de registro.
    """
    
    nodes = rpc_client.discover_sensor_nodes()

    assert len(nodes) == i, "Error al descubrir nodos sensores"

    for sensor_name, _, sensor_port in SENSORS_ARGS[:i]:
        assert sensor_name in nodes, f"Nodo {sensor_name} no identificado"
        assert sensor_port == nodes[sensor_name][1], f"Puerto difiere para nodo {sensor_name}"

    for sensor_name in nodes:
        reading = rpc_client.get_sensor_reading(sensor_name)
        assert reading in (True, False), "Error en medición de nodo"
        logger.INFO(f"Medición de {sensor_name}: {reading}")
        
