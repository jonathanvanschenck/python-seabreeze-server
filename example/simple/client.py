from seabreeze_server.client import SeaBreezeClient
from seabreeze_server.errors import SeaBreezeServerError, CallMethodError
# Testing
HOST, PORT = 'localhost', 9999
client = SeaBreezeClient(HOST, PORT)
print("repr:",client)
print("dev_list:",client.list_devices())
client.select_spectrometer(0)
print("serial num:",client.serial_number())
print("Setting Integration Time : 10 ms")
client.set_integration_time_micros(10*1000)
print("intensities: ",client.get_intensities())
client.deselect_spectrometer()
try:
    client.serial_number() # Raise SeaBreezeServerError
except SeaBreezeServerError as e:
    print("Caught the following error as SeaBreezeServerError:",e)
try:
    client.serial_number() # Raise SeaBreezeServerError
except CallMethodError as e:
    print("Caught the following error as CallMethodError:",e)
