from googlesamples.assistant.grpc.pushtotalk import device_helpers
import logging
import time
from helpers import descubrirNodos
from helpers import listarNodos

def hub_device_handler_creator(device_id):
    hub_device_handler = device_helpers.DeviceRequestHandler(device_id)

    @hub_device_handler.command('action.devices.commands.OnOff')
    def onoff(on):
        if on:
            logging.info('Turning device on')
        else:
            logging.info('Turning device off')

    @hub_device_handler.command('com.example.commands.BlinkLight')
    def blink(speed, number):
        logging.info('Dispositivo parpadeando %s veces.' % number)
        delay = 1
        if speed == "LENTO":
            delay = 2
        elif speed == "RAPIDO":
            delay = 0.5
        for i in range(int(number)):
            logging.info('Parpadeando.')
            time.sleep(delay)

    @hub_device_handler.command('descubrirNodos')
    def descubreNodos(nada):
        logging.info("Descubriendo nodos sensores.")
        nodos=descubrirNodos()
        logging.info("Se encontraron %d nodos"%nodos)

    @hub_device_handler.command('listarNodos')
    def listaNodos(nada):
        logging.info("Listando nodos sensores encontrados")
        time.sleep(2)
        listarNodos()

    @hub_device_handler.command('consultarNodo')
    def consultaNodo(name):
        logging.info("Obteniendo medición del nodo sensor: %s"%name)
        time.sleep(1)
        consultarNodo(name)

    @hub_device_handler.command('desconectarNodo')
    def desconectaNodo(name):
        logging.info("Desconectando el nodo sensor: %s"%name)
        time.sleep(1)
        desconectarNodo(name)

    return hub_device_handler
