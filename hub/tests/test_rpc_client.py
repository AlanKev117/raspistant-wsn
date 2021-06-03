# Copyright 2021 Alan Fuentes
# Copyright 2021 Yael Estrada
# Copyright 2021 Noé Acosta

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from threading import Thread
from subprocess import Popen

import pytest

from hub.src.rpc_client import RPCClient
from node.src.sensor_node import sensor_node_process


@pytest.fixture
def repeated_name():
    return "aleatorio"


@pytest.fixture
def sensor_nodes(repeated_name):
    """Fixture con lista de hilos de nodos sensores. Consta de 
    dos nodos repetidos y dos nodos con nombre único.

    Args:
        repeated_name: nombre a repetirse en dos nodos de la lista.
    """
    return [Thread(target=sensor_node_process,
                   args=(repeated_name,  # node_name,
                         "dummy",  # sensor_type,
                         3000,  # node_port,
                         1,  # timeout_minutes,
                         True),  # verbose
                   daemon=True),
            Thread(target=sensor_node_process,
                   args=(repeated_name,  # node_name,
                         "dummy",  # sensor_type,
                         4000,  # node_port,
                         1,  # timeout_minutes,
                         True),  # verbose
                   daemon=True),
            Thread(target=sensor_node_process,
                   args=("raro",  # node_name,
                         "dummy",  # sensor_type,
                         5000,  # node_port,
                         1,  # timeout_minutes,
                         True),  # verbose
                   daemon=True),
            Thread(target=sensor_node_process,
                   args=("curioso",  # node_name,
                         "dummy",  # sensor_type,
                         6000,  # node_port,
                         1,  # timeout_minutes,
                         True),  # verbose
                   daemon=True)]


def test_rpc_client(sensor_nodes, repeated_name):
    """Prueba el funcionamiento del cliente RPC que correrá en 
    el asistente de voz.

    Args:
        sensor_nodes: nodos sensores de simulación a ser invocados.
        repeated_name: nombre repetido intencionalmente dentro de los nodos.
    """

    # Se invoca servidor de registro genérico
    pid = Popen(["rpyc_registry.py"]).pid

    for node in sensor_nodes:
        node.start()
    client = RPCClient()

    # Tiempo de tolerancia para registro
    time.sleep(15)

    nodes, repeated = client.discover_sensor_nodes()
    assert len(nodes) == 2 and repeated_name not in nodes
    assert [repeated_name] == repeated

    names = list(nodes.keys())

    reading, stype = client.get_sensor_reading(names[0])
    assert reading in (True, False)
    assert stype == "DummySensor"

    available = client.get_available_nodes()
    assert available == nodes

    client.forget_sensor(names[1])
    available = client.get_available_nodes()
    assert names[1] not in available
