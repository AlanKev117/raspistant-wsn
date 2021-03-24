from googlesamples.assistant.grpc.pushtotalk import device_helpers
import logging
import time
import rpyc
import os
from gtts import gTTS
from playsound import playsound

nodos_sensores={}

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
        listaNodosSensores=rpyc.discover("SENSORNODE")
        nodos=0
        for i in range(len(listaNodosSensores)):
            ip,port=listaNodosSensores[i]
            print("Nodo sensor encontrado: IP: %s"%ip)
            con=rpyc.connect(ip,port)
            name=con.root.get_Name()
            print("Nombre: %s"%name)
            nodos_sensores[name]=(ip,port)
            nodos+=1
        time.sleep(1)
        reproducirVoz("Se encontraron %s nodos"%nodos)

    @hub_device_handler.command('listarNodos')
    def listaNodos(nada):
        logging.info("Listando nodos sensores encontrados")
        lista=list(nodos_sensores.keys())
        print(lista)
        for i in range(len(lista)):
            logging.info("Nodo: %d %s"%(i+1,lista[i]))
            reproducirVoz("Nodo: %d %s"%(i+1,lista[i]))
            time.sleep(1)

    def reproducirVoz(cadena):
        lan="es"
        myobj=gTTS(text=cadena,lang=lan,slow=False)
        myobj.save('/tmp/voice_command.mp3')
        playsound('/tmp/voice_command.mp3')
        os.remove('/tmp/voice_command.mp3')

    return hub_device_handler
