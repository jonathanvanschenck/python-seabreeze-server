import socket
from utils import Request, Response

__all__ = ['MessageSocket','Client']

BUFFER_SIZE = 1024

class Client:
    def __init__(self,ip,port):
        self.ip,self.port = ip,port
        
    def send_request(self,request):
        socket = MessageSocket(self.ip,self.port)
        rmsg = socket.send_message(request.encode())
        socket.close()
        return Response.from_msg(rmsg)

class MessageSocket(socket.socket):
    def __init__(self,ip,port):
        socket.socket.__init__(self,socket.AF_INET,socket.SOCK_STREAM)
        self.connect((ip,port))
        
    def send_message(self,msg):
        self.sendall(msg)
        self.buffer = b''
        while True:
            rmsg = self.recv(BUFFER_SIZE)
            if rmsg == b'':
                break
            self.buffer = self.buffer + rmsg
        return self.buffer
        

if __name__ == "__main__":
    HOST, PORT = 'localhost', 9999
    client = Client(HOST, PORT)
    print(client.send_request(Request.from_function_call("get_integration_time_micros")))
    print(client.send_request(Request.from_function_call("set_integration_time_micros",100)))
    print(client.send_request(Request.from_function_call("get_intensities")))