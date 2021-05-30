import threading
import time
from subprocess import Popen

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
    """Fixture que representa el nodo sensor a invocar durante la prueba.

    Args:
        node_name: nombre del nodo sensor.
        sensor_type: tipo de sensor con el que el nodo hace mediciones.
        node_port: puerto por el que el nodo escucha peticiones de medición.
        timeout_minutes: tiempo en minutos que tarda el nodo en mandar
            un mensaje de registro.
    """
    return threading.Thread(target=sensor_node_process,
                            args=(node_name,
                                  sensor_type,
                                  node_port,
                                  timeout_minutes,
                                  verbose),
                            daemon=True)


def test_sensor_node(sensor_node_thread, node_name):
    """Ejecuta un nodo sensor, se prueba que pueda enviar mediciones y sus
    metadatos. Requiere que un servidor de registro se encuentre disponible en
    la red local. Para ello, se puede ejecutar el script genérico
    bin/rpyc_registry.py, incluido en la librería rpyc.

    Nótese que el directorio 'bin' se refiere al directorio 'bin' de un 
    ambiente virtual de Python, o bien, al directorio $HOME/.local/bin/

    Args:
        sensor_node_thread: fixture que simboliza el nodo sensor a invocar.
        node_name: fixture que indica el nombre del nodeo a invocar.
    """

    # Se inicia servidor de registro genérico
    pid = Popen(["rpyc_registry.py"]).pid

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
