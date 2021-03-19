import rpyc

from sensor import Sensor

class SensorNodeService(rpyc.Service):

    def __init__(self, sensor: Sensor):
        self.sensor = sensor
    
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        self.sensor.deactivate()

    def exposed_get_sensor_reading(self):
        return self.sensor.get_measurement()

  
