import numpy as np
import time
import socketserver
from utils import Response, Request

__all__ = ['SpectrometerManager','Server']


class Server(socketserver.TCPServer):
    def __init__(self,server_address,emulate=True):
        socketserver.TCPServer.__init__(self, server_address, MessageHandler)
        self.specmanager = SpectrometerManager(emulate=emulate)

class MessageHandler(socketserver.StreamRequestHandler):
    def handle(self):
        msg = self.rfile.readline().strip()
        rmsg = self.server.specmanager.parse_message(msg)
        self.wfile.write(rmsg)
        

# Spectrometer Manager
class SpectrometerManager:
    def __init__(self,emulate=False):
        if emulate:
            sb = FakeSeaBreeze()
        else:
            import seabreeze.spectrometers as sb
        self.sb = sb
        self.attach_spectrometer(self.get_first_spectrometer())
        
    def device_list(self):
        return self.sb.device_list()
    
    def get_first_spectrometer(self):
        return self.sb.Spectrometer.from_first_available()
    
    def attach_spectrometer(self,spectrometer):
        self.sbs = spectrometer
        
    def seabreeze_call(self,fname,*args,**kwargs):
        return self.sbs.__getattr__(fname)(*args,**kwargs)
        
    def parse_message(self,msg):
        #print("got",msg)
        request = Request.from_msg(msg)
        #print(request)
        fname,args = request.action()
        #print(fname,args)
        try:
            rvalue = self.sbs.__getattribute__(fname)(*args)
        except:
            response = Response.from_error("")
        else:
            response = Response.from_function_return(fname,rvalue)
        #print("Created: ",request)
        #print("Created: ",response)
        return response.encode()

# Seabreeze Emulator (for testing)
class FakeSeabreezeSpectrometer:
    def __init__(self,dev):
        self.__w = np.arange(300,1001,0.17)
        self.__it = 100*1000#us
        self.__s = np.exp(-((self.__w - 500)/100)**2)
        self.connected = True
    
    def close(self):
        self.connected = False
    
    def get_wavelengths(self):
        if not self.connected:
            raise Exception("Devcie is disconncted")
        return self.__w
    
    def set_integration_time_micros(self,it):
        if not self.connected:
            raise Exception("Devcie is disconncted")
        self.__it = int(np.clip(it,3*1000,10*1000*1000))
        return self.__it
    
    def get_integration_time_micros(self):
        return self.__it
        
    def get_intensities(self):
        #raise Exception()
        if not self.connected:
            raise Exception("Devcie is disconncted")
        res = 100 + self.__it*self.__s/100 + np.random.normal(scale=20,size=len(self.__s))
        time.sleep(self.__it/10**6)
        return np.clip(res,0,4001)
    
    @classmethod
    def from_first_available(cls):
        return cls(0)
        
    
class FakeSeaBreeze:
    def __init__(self):
        self.Spectrometer = FakeSeabreezeSpectrometer
    
    def device_list(self):
        return ["<Fake Spectrometer>"]
    

    
# Testing
if __name__ == "__main__":
    HOST, PORT = 'localhost', 9999
    with Server((HOST, PORT), emulate=True) as server:
        print("Hosting at:",HOST,"|",PORT)
        server.serve_forever()
