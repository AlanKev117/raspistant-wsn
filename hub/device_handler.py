from googlesamples.assistant.grpc.pushtotalk import device_helpers
import logging
import time
import socket
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
        ipaddress=socket.gethostbyname(socket.gethostname())
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.2)
        message=ipaddress
        server.sendto(str.encode(message), ('192.168.1.255', 37020))
        print("Paquete enviado")
        server.close()
        #Lo ponemos en modo escucha para que reciba a los nodos sensores
        server=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((str(ipaddress),37020))
        server.settimeout(15)
        okstr="OK"
        nodos=0
        while True:
            try:
                name,addr=server.recvfrom(1024)
                print("Nodo sensor encontrado con el nombre: %s y la direccion: %s"%(name.decode(),addr))
                server.sendto(str.encode("OK"),(addr[0],37020))
                nodos_sensores[name.decode()]=addr
                nodos=nodos+1
            except socket.timeout as e:
                print("Se han dejado de descubrir nodos")
                reproducirVoz("Se encontraron %s nodos"%nodos)
                server.close()
                break

    @hub_device_handler.command('listarNodos')
    def listaNodos(nada):
        logging.info("Listando nodos sensores encontrados")
        lista=nodos_sensores.keys()
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
