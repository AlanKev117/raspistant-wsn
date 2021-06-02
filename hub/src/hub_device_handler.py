""" Este módulo contiene todas las device actions que se pueden invocar mediante
    el asistente de voz.

    Para crear una nueva device action, basta con crear una función dentro de la
    función create_hub_device_handler(), con los parámetros definidos en el archivo
    "actions.json" y establecer lo que quiere que se haga una vez invocada la
    función. También es necesario agregar el decorador @hub_device_handler.command()
    para especificar a cual action pertenece dentro del archivo antes mencionado.

"""
import logging
import time

from googlesamples.assistant.grpc import device_helpers
from hub.src.rpc_client import RPCClient
from hub.src.voice_interface import hablar


def create_hub_device_handler(device_id):
    """ Crea el device handler que se encargará de ejecutar las device actions 
        personalizadas que se mandarán a llamar desde el asistente de voz.
        Si el comando de voz no es soportado por el asistente de Google,
        aquí deberás crear una device action que soporte el comando y realice
        las acciones esperadas.

        Args:  
            device_id:
                Identificador del dispositivo registrado en la API de Google Assistant

        Returns:
            hub_device_handler:
                Objeto que maneja las operaciones que hace el asistente de voz con los
                comandos personalizados que se agregaron.
    """
    
    hub_device_handler = device_helpers.DeviceRequestHandler(device_id)

    #   Se crea un cliente RPC para conectarse con los nodos sensores
    client = RPCClient()

    #   Decorador de la función, para identificar a que comando pertenece en el 
    #   archivo "actions.json"
    @hub_device_handler.command('descubrir_nodos')
    def descubrir_nodos(nada):
        """ Descubre los nodos que están conectados a la misma red del asistente de voz.
            
            Esta función usa el cliente RPC para enviar una peticion a la red para
            encontrar los nodos sensores que se encuentran actualmente registrados en el
            servidor de registro y a los cuales se puede tener acceso mediante una llamada
            a procedimiento remoto.
        """
        logging.info("Descubriendo nodos sensores.")

        #   Se envía la petición al cliente RPC, y con ésta se obtiene el numero de nodos
        #   distintos en la red y tambien nos regresa la cantidad de nodos con un nombre
        #   repetido.
        nodos, repetidos = client.discover_sensor_nodes()

        # Notificar cantidad de nodos
        cantidad_nodos = len(nodos)
        if cantidad_nodos == 1:
            nodos_msg = "Se encontró un nodo"
        else:
            nodos_msg = "Se encontraron %d nodos" % cantidad_nodos
        logging.info(nodos_msg)

        hablar(nodos_msg)

        # Manejo de nodos con nombre repetido
        cantidad_repetidos = len(repetidos)
        if cantidad_repetidos > 0:
            # Manejo de singular
            ese, articulo = "s", "los"
            if cantidad_repetidos == 1:
                ese, articulo = "", "el"

            nombres_repetidos = ", ".join(repetidos)
            repetidos_msg = (f"Encontré {articulo} siguiente{ese} nodo{ese} "
                             f"repetido{ese}: {nombres_repetidos}. "
                             f"Asegúrate de que todos los nodos tengan un "
                             f"nombre único.")
            logging.warning(repetidos_msg)
            hablar(repetidos_msg)

    @hub_device_handler.command('listar_nodos')
    def listar_nodos(nada):
        """ Lista los nodos sensores que se encontraron previamente con la funcion
            descubrir_nodos()
            
            Esta funcion recorre el diccionario almacenado en el cliente RPC del asistente
            y lista cada uno de los sensores que éstán registrados, mencionando su nombre
            propio asignado al iniciar el nodo sensor.
        """
        logging.info("Listando nodos sensores disponibles")
        lista = list(client.get_available_nodes().keys())
        cantidad_lista = len(lista)

        # Listado de nodos dictados por el asistente de voz
        if cantidad_lista == 0:
            logging.info("Sin nodos sensores guardados")
            hablar("No tengo nodos sensores guardados")
        else:
            logging.info(f"Nodos a listar: {lista}")
            articulo = "un" if cantidad_lista == 1 else f"{cantidad_lista}"
            nodo_palabra = "nodo" if cantidad_lista == 1 else "nodos"
            hablar(f"Listando {articulo} {nodo_palabra}.")
            for i in range(cantidad_lista):
                time.sleep(1)
                logging.info("Nodo %d: %s" % (i+1, lista[i]))
                hablar("Nodo %d: %s" % (i+1, lista[i]))

    @hub_device_handler.command('desconectar_nodo')
    def desconectar_nodo(sensor_name):
        """ Desconectar un nodo sensor del asistente.

            Elimina un nodo sensor del diccionario de nodos disponibles para que
            ya no sea posible acceder a el.

            Args:
                sensor_name:
                    Nombre propio del sensor que se quiere desconectar.
        """
        try:
            logging.info("Desconectando nodo sensor %s" % sensor_name)
            client.forget_sensor(sensor_name.lower())
        except:
            # No existe la llave o fue imposible conectarse.
            logging.warning(f"Nodo <{sensor_name}> no registrado")

    @hub_device_handler.command('consultar_nodo')
    def consultar_nodo(sensor_name):
        """ Obtiene la medicion de un nodo sensor.

            Esta funcion hace una llamada a procedimiento remoto mediante el
            cliente RPC para obtener lo que el sensor está midiendo en ese
            instante, el sensor le regresa el dato al asistente y este lo procesa
            para dictarlo por medio de voz al usuario.

            Args:
                sensor_name:
                    Nombre propio del sensor que se quiere consultar.

        """

        logging.info("Obteniendo datos del nodo sensor %s" % sensor_name)

        try:
            measurement, sensor_type = client.get_sensor_reading(
                sensor_name.lower())
            
            if sensor_type == "HallSensor":
                state = "cerrado" if measurement == True else "abierto"
                res = f"El estado de {sensor_name} es: {state}"
            elif sensor_type == "PIRSensor":
                state = "con movimiento" if measurement == True else "quieto"
                res = f"El estado de {sensor_name} es: {state}"
            else:
                res = (f"El sensor {sensor_name} "
                       f"regresó la medición: {measurement}")
            logging.info(res)
            hablar(res)

        except:
            # No existe la llave o fue imposible conectarse.
            logging.error(f"Imposible conectarse con {sensor_name}")
            hablar(f"Lo siento, no me pude conectar con el nodo {sensor_name}")

    return hub_device_handler
