import logging
import time
import sys

from googlesamples.assistant.grpc.pushtotalk import device_helpers

try:
    from .rpc_client import RPCClient
except (ImportError, SystemError):
    from rpc_client import RPCClient


def hub_device_handler_creator(device_id):
    client = RPCClient()
    hub_device_handler = device_helpers.DeviceRequestHandler(device_id)

    @hub_device_handler.command('action.devices.commands.OnOff')
    def onoff(on):
        if on:
            logging.info('Turning device on')
        else:
            logging.info('Turning device off')

    @hub_device_handler.command('com.example.commands.BlinkLight')
    def blink(speed, number):
        logging.info('Blinking device %s times.' % number)
        delay = 1
        if speed == "SLOWLY":
            delay = 2
        elif speed == "QUICKLY":
            delay = 0.5
        for i in range(int(number)):
            logging.info('Device is blinking.')
            time.sleep(delay)

    @hub_device_handler.command('descubrirNodos')
    def descubreNodos(void):
        logging.info("Descubriendo nodos sensores.")
        nodos = client.discover_sensor_nodes()
        logging.info("Se encontraron %d nodos" % len(nodos))

    return hub_device_handler
