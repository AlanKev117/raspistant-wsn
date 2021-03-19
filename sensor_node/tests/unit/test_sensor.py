from src.sensor import DummySensor

# Remove _ from hidden functions to be included in pytest test

def test_dummy_sensor_measurement():
    s = DummySensor("dummy")
    measurement = s.get_measurement()
    name = s.get_name()
    assert measurement in (True, False)
    assert name == "dummy"

# def _test_pir_sensor_measurement():
#     s = PIRSensor()
#     measurement = s.get_measurement()
#     assert measurement in (True, False)
