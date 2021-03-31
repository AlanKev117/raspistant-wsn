import rpyc
import logging
import time
import threading
import socket
from rpyc.utils.registry import UDPRegistryClient

def check_connection():
    print("Hilo de conexion a internet iniciado")
    #led=LED(4)
    is_on=False
    while True:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect(('www.google.com',80))
        except (socket.gaierror,socket.timeout):
            logging.info("Sin conexion a internet")
            #led.off()
            is_on=False
        else:
            logging.info("Conectado a internet!")
            #if not is_on:
                #led.on()
        time.sleep(5)

class RepeatedNodeNameError(Exception):
    def __init__(self, node_name):
        self.repeated_name = node_name

    def __str__(self):
        return f"Nombre repetido: {self.repeated_name}"

class RPCClient:
    def __init__(self):
        self._available_nodes = {}
        self._udp_discoverer = UDPRegistryClient()
        hilo_internet= threading.Thread(target=check_connection)
        hilo_internet.start()
    
    def discover_sensor_nodes(self):
        nodes = self._udp_discoverer.discover("SENSORNODE")
        self._available_nodes = {}
        for node in nodes:
            ip, port = node
            connection = rpyc.connect(ip, port)
            sensor_name = connection.root.get_sensor_name()
            connection.close()
            if sensor_name in self._available_nodes:
                raise RepeatedNodeNameError(sensor_name)
            self._available_nodes[sensor_name] = node
        return {**self._available_nodes}

    def get_sensor_reading(self, sensor_name):
        ip, port = self._available_nodes[sensor_name]
        print("Conectando a: %s"%ip)
        print(port)
        connection = rpyc.connect(ip, port)
        reading = connection.root.get_sensor_reading()
        connection.close()
        return reading

    def listarNodos(self):
        lista=list(self._available_nodes.keys())
        logging.info(lista)
        for i in range(len(lista)):
            logging.info("Nodo: %d %s"%(i+1,lista[i]))
            #reproducirVoz("Nodo: %d %s"%(i+1,lista[i]))
            time.sleep(1)
        return len(lista)