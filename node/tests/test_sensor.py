from src.sensor import DummySensor, PIRSensor, HallSensor

# Remove _ from hidden functions to be included during pytest run

def test_dummy_sensor_measurement():
    s = DummySensor("dummy")
    measurement = s.get_measurement()
    name = s.get_name()
    assert measurement in (True, False)
    print("Medición: " + measurement)
    assert name == "dummy"

def _test_pir_sensor_measurement():
    s = PIRSensor("pir")
    measurement = s.get_measurement()
    name = s.get_name()
    assert measurement in (True, False)
    print("Medición: " + measurement)
    assert name == "pir"

def _test_hall_sensor_measurement():
    s = HallSensor("hall")
    measurement = s.get_measurement()
    name = s.get_name()
    assert measurement in (True, False)
    print("Medición: " + measurement)
    assert name == "hall"
