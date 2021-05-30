import time
from threading import Thread
from subprocess import Popen

import pytest

from node.src.sensor_node import sensor_node_process
from hub.src.raspistant import raspistant_process, DEVICE_MODEL_ID, DEVICE_ID


@pytest.fixture
def repeated_name():
    return "aleatorio"


@pytest.fixture
def timeout_seconds():
    return 65


@pytest.fixture
def verbose_level():
    return 2


@pytest.fixture
def raspistant_thread(timeout_seconds, verbose_level):
    """Hilo que representa el asistente de voz con todas sus funcionalidades.

    Args:
        timeout_seconds: tiempo en segundos que el asistente recuerda a los
            nodos sensores.
        verbose_level: nivel que indica la cantidad de logs a mostrar por
            parte del assistente.
    """
    return Thread(target=raspistant_process, args=(DEVICE_MODEL_ID,
                                                   DEVICE_ID,
                                                   "button",
                                                   timeout_seconds,
                                                   verbose_level))


@pytest.fixture
def sensor_nodes(repeated_name, timeout_seconds):
    """Fixture con lista de hilos de nodos sensores. Consta de 
    dos nodos repetidos y dos nodos con nombre único.

    Args:
        repeated_name: nombre a repetirse en dos nodos de la lista.
    """
    return [Thread(target=sensor_node_process,
                   args=(repeated_name,  # node_name,
                         "dummy",  # sensor_type,
                         3000,  # node_port,
                         timeout_seconds / 60,  # timeout_minutes,
                         True),  # verbose
                   daemon=True),
            Thread(target=sensor_node_process,
                   args=(repeated_name,  # node_name,
                         "dummy",  # sensor_type,
                         4000,  # node_port,
                         timeout_seconds / 60,  # timeout_minutes,
                         True),  # verbose
                   daemon=True),
            Thread(target=sensor_node_process,
                   args=("raro",  # node_name,
                         "dummy",  # sensor_type,
                         5000,  # node_port,
                         timeout_seconds / 60,  # timeout_minutes,
                         True),  # verbose
                   daemon=True),
            Thread(target=sensor_node_process,
                   args=("curioso",  # node_name,
                         "dummy",  # sensor_type,
                         6000,  # node_port,
                         timeout_seconds / 60,  # timeout_minutes,
                         True),  # verbose
                   daemon=True)]


def test_raspistant(sensor_nodes, raspistant_thread):
    """Prueba el funcionamiento del proceso principal de asistencia de voz.
    Se invocan 4 nodos sensores de los cuales 2 tienen nombre repetido.

    Args:
        sensor_nodes: nodos sensores de simulación a ser invocados.
        raspistant_thread: hilo del asistente de voz.
    """

    raspistant_thread.start()

    for node in sensor_nodes:
        node.start()

    # Tiempo de tolerancia para registro
    time.sleep(15)

    # Tiempo de interacción en el que se verifica el correcto funcionamiento
    # del asistente con base en los logs mostrados.
    time.sleep(120)
