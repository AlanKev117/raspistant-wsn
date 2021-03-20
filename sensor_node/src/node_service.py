import rpyc

from sensor import Sensor

class SensorNodeService(rpyc.Service):

    def __init__(self, sensor: Sensor):
        self.sensor = sensor
        self.clients = 0
    
    def on_connect(self, conn):
        self.clients += 1
        if self.clients > 1:
            print("Client already connected")
            conn.close()

    def on_disconnect(self, conn):
        pass

    def exposed_get_sensor_reading(self):
        return self.sensor.get_measurement()

    def exposed_get_sensor_name(self):
        return self.sensor.get_name()

  
