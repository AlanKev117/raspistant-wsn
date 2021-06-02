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
