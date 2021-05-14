import logging
import time

from googlesamples.assistant.grpc import device_helpers

from hub.src.rpc_client import RPCClient
from hub.src.voice_interface import hablar

def create_hub_device_handler(device_id):

    hub_device_handler = device_helpers.DeviceRequestHandler(device_id)

    client = RPCClient()

    @hub_device_handler.command('descubrir_nodos')
    def descubrir_nodos(nada):

        logging.info("Descubriendo nodos sensores.")
        
        nodos, repetidos = client.discover_sensor_nodes()
        
        # Notificar cantidad de nodos
        cantidad_nodos = len(nodos)
        if cantidad_nodos == 1:
            nodos_msg = "Se encontró un nodo"
        else:
            nodos_msg = "Se encontraron %d nodos" % cantidad_nodos
        logging.info(nodos_msg)
        hablar(nodos_msg)
        
        # Manejo de nodos con nombre repetido
        cantidad_repetidos = len(repetidos)
        if cantidad_repetidos > 0:
            # Manejo de singular
            ese, articulo = "s", "los"
            if cantidad_repetidos == 1:
                ese, articulo = "", "el"

            nombres_repetidos = ", ".join(repetidos)
            repetidos_msg = (f"Encontré {articulo} siguiente{ese} nodo{ese} "
                             f"repetido{ese}: {nombres_repetidos}. "
                             f"Asegúrate de que todos los nodos tengan un "
                             f"nombre distinto entre ellos e intenta "
                             f"descubrirlos de nuevo.")
            logging.warning(repetidos_msg)
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
            logging.error(f"Imposible conectarse con {sensor_name}")
            hablar(f"Lo siento, no me pude conectar con el nodo {sensor_name}")

    return hub_device_handler
