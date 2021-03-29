import logging
from multiprocessing import Process

import pytest

from hub.src.rpc_client import RPCClient 

# Argumentos del nodo sensor (nombre, tipo, puerto)
SENSOR_1_ARGS = ("sensor hall", "hall", 3000)
SENSOR_2_ARGS = ("sensor pir", "pir", 3000)
SENSORS_ARGS = [SENSOR_1_ARGS, SENSOR_2_ARGS]

def test_rpc_integration(caplog):
    """
    Se prueba el correcto funcionamiento en conjunto de los nodos sensores,
    el cliente rpc del asistente de voz y el servidor de registro.
    """
    caplog.set_level(logging.INFO)
    rpc_client = RPCClient()
    nodes = rpc_client.discover_sensor_nodes()

    assert len(nodes) == 2, "Error al descubrir nodos sensores"

    for sensor_name, _, sensor_port in SENSORS_ARGS:
        assert sensor_name in nodes, f"Nodo {sensor_name} no identificado"
        assert sensor_port == nodes[sensor_name][1], f"Puerto difiere para nodo {sensor_name}"

    for sensor_name in nodes:
        reading = rpc_client.get_sensor_reading(sensor_name)
        assert reading in (True, False), "Error en medición de nodo"
        logging.info(f"Medición de {sensor_name}: {reading}")
        
