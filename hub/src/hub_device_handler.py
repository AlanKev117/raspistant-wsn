from googlesamples.assistant.grpc import device_helpers
from rpc_client import RPCClient
from voice_interface import *
import logging
import time

client=RPCClient()

def create_hub_device_handler(device_id):
    hub_device_handler = device_helpers.DeviceRequestHandler(device_id)

    @hub_device_handler.command('descubrir_nodos')
    def descubrir_nodos(nada):
        logging.info("Descubriendo nodos sensores.")
        nodos=client.discover_sensor_nodes()
        logging.info("Se encontraron %d nodos"%len(nodos))
        reproducirVoz("Se encontraron %d nodos"%len(nodos))

    @hub_device_handler.command('listar_nodos')
    def listar_nodos(self):
        logging.info("Listando nodos sensores disponibles")
        time.sleep(1)
        lista=list(client.get_available_nodes().keys())
        logging.info(lista)
        for i in range(len(lista)):
            logging.info("Nodo: %d %s"%(i+1,lista[i]))
            reproducirVoz("Nodo: %d %s"%(i+1,lista[i]))
            time.sleep(1)
        return len(lista)

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