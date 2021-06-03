# Copyright 2021 Alan Fuentes
# Copyright 2021 Yael Estrada
# Copyright 2021 Noé Acosta

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    """Prueba que se puedan obtener metadatos del sensor: nombre y tipo.

    Args:
        hall_sensor: objeto que representa al sensor.
        hall_sensor_name: nombre a comparar el que se obtenga en la prueba.
    """

    name = hall_sensor.get_name()
    stype = hall_sensor.get_type()
    assert name == hall_sensor_name
    assert stype == "HallSensor"


def get_reading_events(hall_sensor):
    """Detecta un par transiciones de estado del sensor. La prueba es exitosa
    si esta función logra retornar.

    Args:
        hall_sensor: objeto que representa al sensor.
    """

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
        third_reading = hall_sensor.get_reading()
    logging.info(f"Medición final: {third_reading}")


def test_hall_sensor(hall_sensor, hall_sensor_name, caplog):
    """Prueba el funcionamiento de medición del sensor de efecto Hall
    conectado a la tarjeta de desarrollo.

    Args:
        hall_sensor: objeto que representa al sensor.
        hall_sensor_name: nombre del sensor.
        caplog: fixture de configuración de logs durante la prueba.
    """
    caplog.set_level(logging.INFO)

    get_node_data(hall_sensor, hall_sensor_name)
    get_reading_events(hall_sensor)
    hall_sensor.deactivate()
    try:
        hall_sensor.get_reading()
        inactive_node = False
    except:
        inactive_node = True
    assert inactive_node == True
