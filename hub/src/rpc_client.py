import logging

import rpyc
from rpyc.utils.registry import UDPRegistryClient

class RPCClient:
    def __init__(self):
        self._available_nodes = {}
        self._udp_discoverer = UDPRegistryClient()

    def discover_sensor_nodes(self):
        nodes = self._udp_discoverer.discover("SENSORNODE")
        self._available_nodes = {}
        repeated = []
        for node in nodes:
            ip, port = node
            connection = rpyc.connect(ip, port)
            sensor_name = connection.root.get_sensor_name()
            connection.close()
            
            # Identificar nombres repetidos.
            if sensor_name in self._available_nodes:
                repeated.append(sensor_name)
            else:
                self._available_nodes[sensor_name.lower()] = node
            
            # Excluir elementos con nombres repetidos.
            for repeated_name in repeated:
                self._available_nodes.pop(repeated_name, None)
            
        return {**self._available_nodes}, repeated

    def get_sensor_reading(self, sensor_name):
        ip, port = self._available_nodes[sensor_name]
        logging.info("Conectando a {}:{}".format(ip, port))
        connection = rpyc.connect(ip, port)
        reading = connection.root.get_sensor_reading()
        sensor_type = connection.root.get_sensor_type()
        connection.close()
        return reading, sensor_type
        
    def get_available_nodes(self):
        return self._available_nodes

    def forget_sensor(self,sensor_name):
        if sensor_name in self._available_nodes: 
            self._available_nodes.pop(sensor_name)
            return True
        else:
            return False

