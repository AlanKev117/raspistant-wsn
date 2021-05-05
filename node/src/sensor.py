from abc import ABC, abstractmethod
from random import randint

from gpiozero import DigitalInputDevice, DigitalOutputDevice

PIR_PIN = 24
HALL_PIN = 23

class Sensor(ABC):

    @abstractmethod
    def __init__(self, name):
        pass

    @abstractmethod
    def get_reading(self):
        pass
    
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass


class DummySensor(Sensor):

    def __init__(self, name):
        self.name = name

    def get_reading(self):
        return bool(randint(0, 1))

    def get_name(self):
        return self.name

    def get_type(self):
        return "DummySensor"

    def deactivate(self):
        pass


class PIRSensor(Sensor):

    def __init__(self, name):
        self.name = name
        self.pir_sensor = DigitalInputDevice(pin=PIR_PIN, pull_up=False)

    def get_reading(self):
        return self.pir_sensor.is_active

    def get_name(self):
        return self.name

    def get_type(self):
        return "PIRSensor"

    def deactivate(self):
        self.pir_sensor.close()

class HallSensor(Sensor):

    def __init__(self, name):
        self.name = name
        self.hall_sensor = DigitalInputDevice(pin=HALL_PIN, pull_up=True)

    def get_reading(self):
        return self.hall_sensor.is_active

    def get_name(self):
        return self.name

    def get_type(self):
        return "HallSensor"

    def deactivate(self):
        self.hall_sensor.close()
