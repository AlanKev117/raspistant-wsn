import logging
import time

from googlesamples.assistant.grpc import device_helpers

from rpc_client import RPCClient
from voice_interface import reproducir_voz

client = RPCClient()


def create_hub_device_handler(device_id):
    hub_device_handler = device_helpers.DeviceRequestHandler(device_id)

    @hub_device_handler.command('descubrir_nodos')
    def descubrir_nodos(nada):
        logging.info("Descubriendo nodos sensores.")
        nodos = client.discover_sensor_nodes()
        logging.info("Se encontraron %d nodos" % len(nodos))
        reproducir_voz("Se encontraron %d nodos" % len(nodos))

    @hub_device_handler.command('listar_nodos')
    def listar_nodos(nada):
        logging.info("Listando nodos sensores disponibles")
        time.sleep(1)
        lista = list(client.get_available_nodes().keys())
        logging.info(lista)
        for i in range(len(lista)):
            logging.info("Nodo: %d %s" % (i+1, lista[i]))
            reproducir_voz("Nodo: %d %s" % (i+1, lista[i]))
            time.sleep(1)

    @hub_device_handler.command('desconectar_nodo')
    def desconectar_nodo(sensor_name):
        logging.info("Desconectando nodo sensor %s"%sensor_name)
        client.forget_sensor(sensor_name.lower())

    @hub_device_handler.command('consultar_nodo')
    def consultar_nodo(sensor_name):
        time.sleep(1)
        logging.info("Obteniendo datos del nodo sensor %s"%sensor_name)
        measure=client.get_sensor_reading(sensor_name.lower())
        reproducirVoz("El sensor %s regresó la medición: %s"%(sensor_name,measure))
        logging.info("El sensor %s regresó la medición: %s"%(sensor_name,measure))

    # @hub_device_handler.command('action.devices.commands.OnOff')
    # def onoff(on):
    #     if on:
    #         logging.info('Turning device on')
    #     else:
    #         logging.info('Turning device off')

    # @hub_device_handler.command('com.example.commands.BlinkLight')
    # def blink(speed, number):
    #     logging.info('Blinking device %s times.' % number)
    #     delay = 1
    #     if speed == "SLOWLY":
    #         delay = 2
    #     elif speed == "QUICKLY":
    #         delay = 0.5
    #     for i in range(int(number)):
    #         logging.info('Device is blinking.')
    #         time.sleep(delay)

    return hub_device_handler
