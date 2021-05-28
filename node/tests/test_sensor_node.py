import threading
import time

import rpyc
import pytest

from node.src.sensor_node import sensor_node_process


@pytest.fixture
def node_name():
    return "aleatorio"


@pytest.fixture
def sensor_type():
    return "dummy"


@pytest.fixture
def node_port():
    return 3000


@pytest.fixture
def timeout_minutes():
    return 1


@pytest.fixture
def verbose():
    return True


@pytest.fixture
def sensor_node_thread(node_name,
                       sensor_type,
                       node_port,
                       timeout_minutes,
                       verbose):
    return threading.Thread(target=sensor_node_process,
                            args=(node_name,
                                  sensor_type,
                                  node_port,
                                  timeout_minutes,
                                  verbose),
                            daemon=True)


def test_sensor_node(sensor_node_thread):
    """Ejecuta un nodo sensor, se prueba que pueda enviar mediciones y sus
    metadatos.
    """

    # Inicia nodo sensor con tiempo de ajuste para emisión de mensajes de
    # registro
    sensor_node_thread.start()
    time.sleep(5)

    # Se descubre y se conecta al nodo sensor
    node_connection = rpyc.connect_by_service("SENSORNODE")

    # Se obtienen datos del nodo.
    name = node_connection.root.get_sensor_name()
    reading = node_connection.root.get_sensor_reading()
    stype = node_connection.root.get_sensor_type()

    assert name == node_name
    assert stype == "DummySensor"
    assert reading in (True, False)
