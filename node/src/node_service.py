import rpyc
import logging


class SensorNodeService(rpyc.Service):

    def __init__(self, sensor, silent_logger=False):
        self.sensor = sensor
        self.name = self.sensor.get_name()
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(
            logging.WARNING if silent_logger else logging.INFO)
        

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_get_sensor_reading(self):
        reading = self.sensor.get_reading()
        self.logger.info(f"Enviando medición: <{reading}>...")

        return reading

    def exposed_get_sensor_type(self):
        self.logger.info()
        return self.sensor.get_type()

    def exposed_get_sensor_name(self):
        self.logger.info("Enviando nombre de nodo...")
        return self.name
