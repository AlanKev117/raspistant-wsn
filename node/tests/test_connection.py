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

import pytest

from node.src.node_connection import check_node_connection


@pytest.fixture
def verbose():
    return True


@pytest.fixture
def check_connection_thread(verbose):
    """Hilo de detección de conexión a la red local.

    Args:
        verbose: indica si el hilo debe mostrar o no mensajes en terminal.
    """
    return threading.Thread(target=check_node_connection,
                            args=((verbose,)),
                            daemon=True)


def test_check_connection_thread(check_connection_thread):
    """Ejecuta el hilo de revisión de conexión a internet por un minuto, mismo
    en el que se interrumpirá la conexión a la red local para luego
    ser reestablecida.

    Una ejecución exitosa de esta funcionalidad mostrará
    los logs adecuados en cada momento. Al final de la misma, el LED
    de conexión deberá permanecer apagado.
    """
    check_connection_thread.start()
    time.sleep(60)
