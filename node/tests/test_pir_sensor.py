import logging

import pytest

from node.src.sensor import PIRSensor


@pytest.fixture
def pir_sensor_name():
    return "pir"


@pytest.fixture
def pir_sensor(pir_sensor_name):
    return PIRSensor(pir_sensor_name)


def get_node_data(pir_sensor, pir_sensor_name):
    """Prueba que se puedan obtener metadatos del sensor: nombre y tipo.

    Args:
        pir_sensor: objeto que representa al sensor.
        pir_sensor_name: nombre a comparar el que se obtenga en la prueba.
    """

    name = pir_sensor.get_name()
    stype = pir_sensor.get_type()
    assert name == pir_sensor_name
    assert stype == "PIRSensor"


def get_reading_events(pir_sensor):
    """Detecta un par transiciones de estado del sensor. La prueba es exitosa
    si esta función logra retornar.

    Args:
        pir_sensor: objeto que representa al sensor.
    """

    initial_reading = pir_sensor.get_reading()
    assert initial_reading in (True, False)
    logging.info(f"Medición inicial: {initial_reading}")

    second_reading = pir_sensor.get_reading()
    assert second_reading in (True, False)

    while initial_reading == second_reading:
        second_reading = pir_sensor.get_reading()
    logging.info(f"Nueva medición: {second_reading}")

    third_reading = pir_sensor.get_reading()
    assert third_reading in (True, False)

    while second_reading == third_reading:
        third_reading = pir_sensor.get_reading()
    logging.info(f"Medición final: {third_reading}")


def test_hall_sensor(pir_sensor, pir_sensor_name, caplog):
    """Prueba el funcionamiento de medición del sensor PIR conectado
    a la tarjeta de desarrollo.

    Args:
        pir_sensor: objeto que representa al sensor.
        pir_sensor_name: nombre del sensor.
        caplog: fixture de configuración de logs durante la prueba.
    """

    caplog.set_level(logging.INFO)

    get_node_data(pir_sensor, pir_sensor_name)
    get_reading_events(pir_sensor)
    pir_sensor.deactivate()
    try:
        pir_sensor.get_reading()
        inactive_node = False
    except:
        inactive_node = True
    assert inactive_node == True
