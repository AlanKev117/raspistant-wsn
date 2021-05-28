import logging

import pytest

from node.src.sensor import HallSensor


@pytest.fixture
def hall_sensor_name():
    return "hall"


@pytest.fixture
def hall_sensor(hall_sensor_name):
    return HallSensor(hall_sensor_name)


def get_node_data(hall_sensor, hall_sensor_name):
    name = hall_sensor.get_name()
    stype = hall_sensor.get_type()
    assert name == hall_sensor_name
    assert stype == "HallSensor"


def get_reading_events(hall_sensor, caplog):

    initial_reading = hall_sensor.get_reading()
    assert initial_reading in (True, False)
    logging.info(f"Medición inicial: {initial_reading}")

    second_reading = hall_sensor.get_reading()
    assert second_reading in (True, False)

    while initial_reading == second_reading:
        second_reading = hall_sensor.get_reading()
    logging.info(f"Nueva medición: {second_reading}")

    third_reading = hall_sensor.get_reading()
    assert third_reading in (True, False)

    while second_reading == third_reading:
        second_reading = hall_sensor.get_reading()
    logging.info(f"Medición final: {third_reading}")


def test_hall_sensor(hall_sensor, hall_sensor_name, caplog):

    caplog.set_level(logging.INFO)

    get_node_data(hall_sensor, hall_sensor_name)
    get_reading_events(hall_sensor, caplog)
    hall_sensor.deactivate()
    try:
        hall_sensor.get_reading()
        inactive_node = False
    except:
        inactive_node = True
    assert inactive_node == True
