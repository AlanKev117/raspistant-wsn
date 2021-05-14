import rpyc
import logging


class SensorNodeService(rpyc.Service):

    def __init__(self, sensor, verbose=False):
        self.sensor = sensor
        self.name = self.sensor.get_name()
        self.logger = logging.getLogger(self.name)
        # Logger configuration
        h = logging.StreamHandler()
        f = logging.Formatter("%(levelname)s:NODESERVICE(%(name)s):%(msg)s")
        h.setFormatter(f)
        self.logger.addHandler(h)
        self.logger.setLevel(logging.INFO if verbose else logging.WARNING)

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_get_sensor_reading(self):
        reading = self.sensor.get_reading()
        self.logger.info(f"Enviando medición: <{reading}>...")
        return reading

    def exposed_get_sensor_type(self):
        sensor_type = self.sensor.get_type()
        self.logger.info(f"Enviando tipo de sensor: <{sensor_type}>...")
        return

    def exposed_get_sensor_name(self):
        self.logger.info("Enviando nombre de nodo...")
        return self.name
