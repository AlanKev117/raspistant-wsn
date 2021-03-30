import sys
sys.path.insert(1, '/home/yael/Documentos/TT/raspistant-wsn/hub')
from helpers import descubrirNodos
from helpers import consultarNodo
from helpers import desconectarNodo
from helpers import listarNodos
sys.path.insert(1, '/home/yael/Documentos/TT/raspistant-wsn/sensor_node/src')
from sensor import DummySensor
import logging

nodos={}

SENSOR_NAME = "prueba"
SENSOR_TYPE = "dummy"
SENSOR_HOST= "192.168.1.71"
SENSOR_SERVER_PORT = 3333
PORT = 18811  # puerto por defecto
PRUNING_TIME = 3 # segundos de tiempo de eliminación

@pytest.fixture
def registry_server_process():
    rs_process = Process(target=registry_server,
                         args=(PORT, PRUNING_TIME),
                         daemon=True)
    rs_process.start()

    return rs_process

@pytest.fixture
def sensor_node_process():
    sn_process = Process(target=sensor_node,
                         args=(SENSOR_NAME, SENSOR_TYPE, SENSOR_SERVER_PORT),
                         daemon=True)
    sn_process.start()
    return sn_process

def test_hub_discovery():
	global nodos
	nodos=descubrirNodos()
	if len(nodos)==0:
		logging.info("No se encontraron nodos sensores")
	else:
		logging.info("Se encontraron nodos sensores")

def test_hub_consult():
	nodos["prueba"]=(SENSOR_HOST,SENSOR_SERVER_PORT)
	b=consultarNodo("prueba",nodos)
	assert b in (True,False)

def test_hub_disconnect():
	nodos["prueba"]=(SENSOR_HOST,SENSOR_SERVER_PORT)
	b=desconectarNodo("prueba")
	assert b==True

def test_hub_listar():
	nodos["prueba"]=(SENSOR_HOST,SENSOR_SERVER_PORT)
	b=listarNodos()
	if b==0:
		logging.info("No hay nodos sensores registrados")
	else:
		logging.info("Se listaron los %s nodos"%b)
