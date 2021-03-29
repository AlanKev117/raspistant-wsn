import sys
sys.path.insert(1, '/home/yael/Documentos/TT/raspistant-wsn/hub')
from helpers import descubrirNodos
from helpers import consultarNodo
from helpers import desconectarNodo
from helpers import listarNodos
sys.path.insert(1, '/home/yael/Documentos/TT/raspistant-wsn/sensor_node/src')
from sensor import DummySensor
import logging

