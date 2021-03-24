import rpyc


lista=rpyc.discover("SENSORNODE")
print(lista[0])
c=rpyc.connect_by_service("SENSORNODE")
print(c.root.get_Name())
print(c.root.get_IP_address())
#c=rpyc.connect("192.168.1.70",18861)
#print(c.root.get_Name())
