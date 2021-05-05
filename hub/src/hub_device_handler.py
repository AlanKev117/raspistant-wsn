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
        nodos, repetidos = client.discover_sensor_nodes()
        logging.info("Se encontraron %d nodos" % len(nodos))
        hablar("Se encontraron %d nodos" % len(nodos))
        cantidad_repetidos = len(repetidos)
        logging.info(f"Se encontraron {cantidad_repetidos} nodos repetidos")
        if cantidad_repetidos > 0:
            nombres_repetidos = ", ".join(repetidos)
            repetidos_msg = (f"Encontré los siguientes nodos repetidos: "
                             f"{nombres_repetidos}. "
                             f"Corrige el nombre de los nodos e intenta "
                             f"descubrirlos de nuevo")
            hablar(repetidos_msg)

    @hub_device_handler.command('listar_nodos')
    def listar_nodos(nada):
        logging.info("Listando nodos sensores disponibles")
        time.sleep(1)
        lista = list(client.get_available_nodes().keys())
        logging.info(lista)
        for i in range(len(lista)):
            logging.info("Nodo %d: %s" % (i+1, lista[i]))
            hablar("Nodo %d: %s" % (i+1, lista[i]))
            time.sleep(1)
        if len(lista) == 0:
            hablar("No tengo nodos sensores guardados")

    @hub_device_handler.command('desconectar_nodo')
    def desconectar_nodo(sensor_name):
        try:
            logging.info("Desconectando nodo sensor %s" % sensor_name)
            client.forget_sensor(sensor_name.lower())
        except:
            # No existe la llave o fue imposible conectarse.
            logging.warning(f"Nodo <{sensor_name}> no registrado")


    @hub_device_handler.command('consultar_nodo')
    def consultar_nodo(sensor_name):
        time.sleep(1)
        logging.info("Obteniendo datos del nodo sensor %s" % sensor_name)
        try:
            measurement, sensor_type = client.get_sensor_reading(
                sensor_name.lower())
            if sensor_type == "HallSensor":
                state = "cerrado" if measurement == True else "abierto"
                res = f"El estado de {sensor_name} es: {state}"
            elif sensor_type == "PIRSensor":
                state = "con movimiento" if measurement == True else "quieto"
                res = f"El estado de {sensor_name} es: {state}"
            else:
                res = (f"El sensor {sensor_name} "
                       f"regresó la medición: {measurement}")
            logging.info(res)
            hablar(res)

        except:
            # No existe la llave o fue imposible conectarse.
            logging.error(f"Imposible conectarse con {sensor_name}", stack_info=True)
            hablar(f"Lo siento, no me pude conectar con el nodo {sensor_name}")

    return hub_device_handler
