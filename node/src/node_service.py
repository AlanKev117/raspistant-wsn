import rpyc

try:
    from .sensor import Sensor
except (SystemError, ImportError):
    from sensor import Sensor


class SensorNodeService(rpyc.Service):

    def __init__(self, sensor: Sensor):
        self.sensor = sensor
    
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_get_sensor_reading(self):
        return self.sensor.get_measurement()

    def exposed_get_sensor_name(self):
        return self.sensor.get_name()

  
