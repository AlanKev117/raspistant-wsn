import pytest

from node.src.sensor import PIRSensor

@pytest.fixture
def pir_sensor_name():
    return "pir"

@pytest.fixture
def pir_sensor(pir_sensor_name):
    return PIRSensor(pir_sensor_name)


def get_node_data(pir_sensor, pir_sensor_name):
    name = pir_sensor.get_name()
    stype = pir_sensor.get_type()
    assert name == pir_sensor_name
    assert stype == "PIRSensor"

def get_reading_events(pir_sensor):
    initial_reading = pir_sensor.get_reading()
    assert initial_reading in (True, False)

    second_reading = pir_sensor.get_reading()
    assert second_reading in (True, False)

    while initial_reading == second_reading:
        second_reading = pir_sensor.get_reading()
    
    third_reading = pir_sensor.get_reading()
    assert third_reading in (True, False)

    while second_reading == third_reading:
        second_reading = pir_sensor.get_reading()


def test_hall_sensor(pir_sensor, pir_sensor_name):
    get_node_data(pir_sensor, pir_sensor_name)
    get_reading_events(pir_sensor)
    pir_sensor.deactivate()
    try:
        pir_sensor.get_reading()
        inactive_node = False
    except:
        inactive_node = True
    assert inactive_node == True