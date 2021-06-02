""" Cliente rpc

    Este programa implementa un cliente por medio de RPC, o
    como sus siglas en inglés lo dicen: Llamada a Procedimiento
    Remoto. Este se conecta con los nodos sensores dentro de la
    red del hogar para obtener su información o realizar consultas
    a cada uno de forma síncrona.

    Typical Usage:
        client= RPCClient();

"""
import logging

import rpyc
from rpyc.utils.registry import UDPRegistryClient

class RPCClient:
    """ Clase RPCClient

        Esta clase implementa los métodos que se utilizarán para que
        el asistente de voz se comunique con todos los nodos sensores,
        contiene todas las funciones para descubrir, consultar u olvidar
        un nodo sensor.

        Args:
            available_nodes:
                Es un diccionario donde se guarda como llave el nombre
                propio del nodo sensor y como valor se guarda la IP y el
                puerto de donde se comunica ese nodo.
            udp_discoverer:
                Este objeto contiene el cliente que consultará el servidor
                de registro mediante el protocolo UDP para obtener los datos
                de los nodos sensores conectados a la red.
    """
    def __init__(self):
        self._available_nodes = {}
        self._udp_discoverer = UDPRegistryClient()

    def discover_sensor_nodes(self):
        """ Descubrir nodos sensores

            Esta función descubre los nodos sensores que se encuentran conectado
            al servidor de registro y los registra en su diccionario para tener
            acceso a ellos posteriormente, se guardan solamente sus datos de IP
            y puerto con valor.
            La operacion la hace conectándose a cada nodo sensor mediante sus datos
            de red y por medio de una RPC se manda a llamar el método get_sensor_name
            de cada sensor que nos regresa el nombre propio de éste. 
            Si hay un nombre repetido se exluye de la lista para no haber problemas
            a la hora de consultarlos.

            Returns:
                self._available_nodes
                    El diccionario de nodos registrados
                repeated:
                    Lista de nombres repetidos que se encontraron
        """

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
        """ Consultar un nodo sensor

            Ésta función recibe una cadena que es el nombre del sensor que
            se quiere consultar y obtiene los datos de red de éste nodo desde
            el diccionario donde se almacenan.
            Posteriormente usando esos datos se conecta al nodo sensor y mediante
            una RPC manda a llamar el método get_sensor_reading para obtener la lectura
            de ese nodo y el método get_sensor_type para obtener el tipo de sensor que
            es y saber como se va a procesar la medición. 

            Args:
                sensor_name:
                    Nombre propio del sensor que se quiere consultar.
            Returns:
                reading:
                    Medicion del nodo sensor consultado.
                sensor_type:
                    Tipo del nodo sensor consultado.
        """

        ip, port = self._available_nodes[sensor_name]
        logging.info("Conectando a {}:{}".format(ip, port))
        connection = rpyc.connect(ip, port)
        reading = connection.root.get_sensor_reading()
        sensor_type = connection.root.get_sensor_type()
        connection.close()
        return reading, sensor_type
        
    def get_available_nodes(self):
        return self._available_nodes

    def forget_sensor(self, sensor_name):
        """ Olvidar un nodo sensor

            Ésta función elimina un nodo sensor del diccionario de nodos disponibles
            de forma que el asistente ya no pueda interactuar con ellos.
            Solamente olvida el nodo sensor por parte del asistente, pero el nodo sensor
            seguirá funcionando independientemente sin tener ninguna conexión con 
            el asistente de voz.

            Args:
                sensor_name:
                    Nombre propio del sensor que se quiere olvidar.
            Returns:
                Booleano que indica si se eliminó el nodo sensor. 
        """

        if sensor_name in self._available_nodes: 
            self._available_nodes.pop(sensor_name)
            return True
        else:
            return False

