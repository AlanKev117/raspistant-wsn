import pytest
import rpyc
from rpyc.utils.registry import UDPRegistryClient

def discover_devices(service_name: str="SENSORNODE"):
    rc = UDPRegistryClient()
    devices = rc.discover(service_name)
    return devices

def get_data_from_device(ip="localhost", port=18861):
    conn = rpyc.connect(ip, port)
    r = conn.root.get_sensor_reading()
    n = conn.root.get_sensor_name()
    conn.close()
    return r, n

def test_whole_service():
    devices = discover_devices("SENSORNODE")
    if len(devices) == 0:
        pytest.fail(
            "Sensors weren't found. Make sure rpyc_registry.py is running and devices are available."
        )
    else:
        for device in devices:
            ip, port = device
            reading, name = get_data_from_device(ip, port)
            assert reading in (True, False), "Measurement corrupted"
            assert type(name) == str, "Corrupted sensor name"


