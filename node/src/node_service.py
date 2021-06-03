# Copyright 2021 Alan Fuentes
# Copyright 2021 Yael Estrada
# Copyright 2021 Noé Acosta

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rpyc
import logging


class SensorNodeService(rpyc.Service):
    """ Clase SensorNodeService

        Esta clase implementa el servicio del nodo sensor que será
        accesible para el asistente de voz mediante las llamadas RPC
        aquí se tendrán implementados los atributos y métodos del 
        nodo sensor.

        Args:
            sensor:
                Instancia del objeto del nodo sensor al que pertenece el
                servicio
            name:
                Nombre propio del sensor
            logger:
                Salida de los logs del nodo sensor.
    """
    def __init__(self, sensor, verbose=False):
        self.sensor = sensor
        self.name = self.sensor.get_name()
        self.logger = logging.getLogger(f"NODE_SERVICE/{self.name}")
        # Logger configuration
        self.logger.setLevel(logging.INFO if verbose else logging.WARNING)

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_get_sensor_reading(self):
        """ Obtener lectura del sensor

            Esta obtiene la lectura del nodo sensor en el momento
            que se manda a llamar.
            
            Returns:
                Lectura del sensor
        """
        reading = self.sensor.get_reading()
        self.logger.info(f"Enviando medición: <{reading}>...")
        return reading

    def exposed_get_sensor_type(self):
        sensor_type = self.sensor.get_type()
        self.logger.info(f"Enviando tipo de sensor: <{sensor_type}>...")
        return sensor_type

    def exposed_get_sensor_name(self):
        self.logger.info("Enviando nombre de nodo...")
        return self.name
