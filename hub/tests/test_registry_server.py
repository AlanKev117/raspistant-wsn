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

import threading
import time
from multiprocessing import Process

from rpyc.utils.factory import DiscoveryError

import pytest
import rpyc

from hub.src.registry_server import registry_server
from node.src.sensor_node import sensor_node_process


@pytest.fixture
def registry_server_port():
    return 18811


@pytest.fixture
def registry_pruning_timeout():
    return 30


@pytest.fixture
def registry_verbose():
    return True


@pytest.fixture
def registry_server_thread(registry_server_port,
                           registry_pruning_timeout,
                           registry_verbose):
    """Fixture con hilo de servidor de registro.

    Args:
        registry_server_port: puerto por el que el servidor recibe 
            mensajes de registro.
        registry_pruning_timeout: tiempo que tarda el servidor en olvidar 
            un nodo tras emitir un mensaje de registro.
        registry_verbose: indica si el hilo produce logs o no.
    """
    return threading.Thread(target=registry_server,
                            args=(registry_server_port,
                                  registry_pruning_timeout,
                                  registry_verbose),
                            daemon=True)


@pytest.fixture
def node_process(registry_pruning_timeout):
    """Fixture con el proceso de un nodo sensor de simulación.

    Args:
        registry_pruning_timeout: tiempo en minutos que tarda cada mensaje de
            registro en ser enviado.
    """
    return Process(target=sensor_node_process,
                   args=("aleatorio",  # node_name,
                         "dummy",  # sensor_type,
                         3000,  # node_port,
                         registry_pruning_timeout // 60,  # timeout_minutes,
                         True),  # verbose
                   daemon=True)


def test_registry_server(registry_server_thread,
                         node_process,
                         registry_pruning_timeout):
    """Prueba el servidor de registro. Que habilite el descubrimiento de nodos
    en la red y que funcionen adecuadamente los temporizadores de olvido de
    nodos sensores.

    Args:
        registry_server_thread: fixture que contiene el hilo del servidor de 
            registro.
        node_process: fixture con el proceso de nun nodo sensor de simulación
        registry_pruning_timeout: tiempo en segundos que tardará el servidor
            en olvidar un nodo tras este haber enviado su último mensaje de
            registro.
    """
    # Inician ambos procesos
    registry_server_thread.start()
    node_process.start()

    # Tiempo de tolerancia para registro
    time.sleep(5)

    # Se descubren nodos sensores
    try:
        device = rpyc.discover("SENSORNODE")
    except DiscoveryError:
        pytest.fail("Debería haber un nodo disponible", pytrace=True)

    assert len(device) > 0

    # Termina el proceso de nodo. Se espera el tiempo de olvido y se descubren
    # de nuevo los nodos disponibles.
    node_process.terminate()
    time.sleep(registry_pruning_timeout)

    with pytest.raises(DiscoveryError):
        device = rpyc.discover("SENSORNODE")

    node_process.close()
