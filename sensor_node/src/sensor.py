from abc import ABC, abstractmethod
from random import randint

from gpiozero import DigitalInputDevice


class Sensor(ABC):

    @abstractmethod
    def __init__(self, name):
        pass

    @abstractmethod
    def get_measurement(self):
        pass
    
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass


class DummySensor(Sensor):

    def __init__(self, name):
        self.name = name

    def get_measurement(self):
        return bool(randint(0, 1))

    def get_name(self):
        return self.name

    def deactivate(self):
        pass


class PIRSensor(Sensor):

    def __init__(self):
        self.pir_sensor = DigitalInputDevice(pin=14, pull_up=True)

    def get_measurement(self):
        return self.pir_sensor.is_active

    def get_name(self):
        return self.name

    def deactivate(self):
        self.pir_sensor.close()
