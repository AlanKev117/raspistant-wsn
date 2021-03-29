import rpyc
from rpyc.utils.registry import UDPRegistryClient

class RepeatedNodeNameError(Exception):
    def __init__(self, node_name):
        self.repeated_name = node_name

    def __str__(self):
        return 

class RPCClient:
    def __init__(self):
        self._available_nodes = {}
        self._udp_discoverer = UDPRegistryClient()
    
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
        connection = rpyc.connect(ip, port)
        reading = connection.root.get_sensor_reading()
        connection.close()
        return reading
    