from roverMotorInterface import RoverMotorInterface
from roverServer import RoverServer
from device_utilities import simple_connect


print("Initializing Rover")
print("Building Moter Interface")
roverMotorInterface = RoverMotorInterface()
rmi = roverMotorInterface

print("Building Server")
rs = RoverServer(rmi)

print("Connecting to noobiemcfoob")
wlan = simple_connect("noobiemcfoob", "n00biemcfoob")
print("Connected!")

print("Starting Server!")
rs.openServer()
