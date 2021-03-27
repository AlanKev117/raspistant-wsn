from multiprocessing import Process
import time

import pytest
import rpyc
from rpyc.utils.registry import UDPRegistryClient

from sensor_node.src.sensor_node import sensor_node

# Argumentos del nodo sensor
SENSOR_NAME = "prueba"
SENSOR_TYPE = "dummy"
SENSOR_SERVER_PORT = 3333


@pytest.fixture
def sensor_node_process():
    sn_process = Process(target=sensor_node,
                         args=(SENSOR_NAME, SENSOR_TYPE, SENSOR_SERVER_PORT),
                         daemon=True)
    sn_process.start()
    return sn_process


def get_data_from_device(ip, port):
    conn = rpyc.connect(ip, port)

    reading = conn.root.get_sensor_reading()
    name = conn.root.get_sensor_name()

    conn.close()

    return reading, name


def test_sensor_node(sensor_node_process):
    reading, name = get_data_from_device(ip="localhost",
                                         port=SENSOR_SERVER_PORT)

    assert reading in (True, False), "Measurement corrupted"
    assert name == SENSOR_NAME, "Corrupted sensor name"

    sensor_node_process.terminate()
