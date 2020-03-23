from remote_object.client import Client

class SeaBreezeClient(Client):
    """The SeaBreezeClient class
    
    A thin wrapper of the `remote_object.client.Client`
    class
    
    :param HOST: str
        A string for the host address of the server
        
    :param PORT: int
        An integer for the port of the 
    """
    def __init__(self,HOST,PORT):
        Client.__init__(self,HOST,PORT)


# Testing
if __name__ == "__main__":
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
    #client.serial_number() # Raise SeaTeaseError