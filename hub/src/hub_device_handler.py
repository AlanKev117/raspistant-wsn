import logging
import time
import sys
import pathlib
from googlesamples.assistant.grpc import device_helpers

from hub.src.rpc_client import RPCClient
from misc.voice_interface import hablar


def create_hub_device_handler(device_id):

    hub_device_handler = device_helpers.DeviceRequestHandler(device_id)

    client = RPCClient()

    @hub_device_handler.command('descubrir_nodos')
    def descubrir_nodos(nada):
        logging.info("Descubriendo nodos sensores.")
        nodos = client.discover_sensor_nodes()
        logging.info("Se encontraron %d nodos" % len(nodos))
        hablar("Se encontraron %d nodos" % len(nodos))

    @hub_device_handler.command('listar_nodos')
    def listar_nodos(nada):
        logging.info("Listando nodos sensores disponibles")
        time.sleep(1)
        lista = list(client.get_available_nodes().keys())
        logging.info(lista)
        for i in range(len(lista)):
            logging.info("Nodo: %d %s" % (i+1, lista[i]))
            hablar("Nodo: %d %s" % (i+1, lista[i]))
            time.sleep(1)

    @hub_device_handler.command('desconectar_nodo')
    def desconectar_nodo(sensor_name):
        logging.info("Desconectando nodo sensor %s" % sensor_name)
        client.forget_sensor(sensor_name.lower())

    @hub_device_handler.command('consultar_nodo')
    def consultar_nodo(sensor_name):
        time.sleep(1)
        logging.info("Obteniendo datos del nodo sensor %s" % sensor_name)
        measure = client.get_sensor_reading(sensor_name.lower())
        hablar("El sensor %s regresó la medición: %s" % (sensor_name, measure))
        logging.info("El sensor %s regresó la medición: %s" %
                     (sensor_name, measure))

    return hub_device_handler
