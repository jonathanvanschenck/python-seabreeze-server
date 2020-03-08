import numpy as np

class APIArgEncoding:
    pass

class Integer(APIArgEncoding):
    @staticmethod
    def encode(value):
        return bytes(str(int(value)),'ascii')
    @staticmethod
    def decode(data):
        return int(data)
    
class String(APIArgEncoding):
    @staticmethod
    def encode(value):
        return bytes(str(value),'ascii')
    @staticmethod
    def decode(data):
        return data.decode()
    
class Array(APIArgEncoding):
    @staticmethod
    def encode(value):
        return np.array(value,dtype=float).tobytes()
    @staticmethod
    def decode(data):
        return np.frombuffer(data)

class NoArgs(APIArgEncoding):
    @staticmethod
    def encode(value):
        return b''
    @staticmethod
    def decode(data):
        return None   

seabreezeAPI = [
    # stc       fname               get call,  get return,  set call, set return
    [b'0','integration_time_micros',NoArgs,     Integer,    Integer,  Integer],
    #[b'1','boxcar_width',  Integer,      Integer],
    #[b'2','scans_to_average',  Integer,      Integer],
    [b'a','intensities',NoArgs, Array],
    [b'b','wavelengths',NoArgs, Array],
    [b'c','serial_number',NoArgs, String]
]

seabreezeErrors = [
    # finish this
    [b'z','']
]


class Event:
    APIdecoder = {i[0]:i[1:] for i in seabreezeAPI}
    APIencoder = {i[1]:i[0] for i in seabreezeAPI}
    getset = {b'1':'get_',b'2':'set_'}
    
    def __init__(self,typecode,stypecode,data):
        self.tc = typecode
        self.stc = stypecode
        self.data = data
        
    def __repr__(self):
        return "<Event: {0}|{1}>".format((self.tc+self.stc).decode(),self.data[:10].decode())
    
    def encode(self):
        return self.tc+self.stc+self.data+b'\n'
    
    @classmethod
    def from_msg(cls,msg):
        nmsg = msg.strip()
        return cls(nmsg[:1],nmsg[1:2],nmsg[2:])
        

class Request(Event):
    def action(self):
        decode = self.APIdecoder[self.stc]
        fname = self.getset[self.tc] + decode[0]
        value = decode[1+2*int(self.tc == b'2')].decode(self.data)
        if value is None:
            args = []
        else:
            args = [value]
        return fname,args
    
    def __repr__(self):
        return "<Request: {0}({1})>".format(*self.action())
    
    @classmethod
    def get_from_set(cls,set_cls):
        newcls = cls(b'1',b'0',b'')
        newcls.stc = 1*set_cls.stc
        return newcls
    @classmethod
    def from_function_call(cls,fname,value=None):
        newcls = cls(b'1',b'0',b'')
        if 'set_' in fname:
            newcls.tc = b'2'
        fnamebase = "_".join(fname.split("_")[1:])
        newcls.stc = cls.APIencoder[fnamebase]
        if not value is None:
            newcls.data = cls.APIdecoder[newcls.stc][1+2*int(newcls.tc == b'2')].encode(value)
        return newcls

    
class Response(Event):
    def _return(self):
        if self.tc == b'0':
            raise Exception("Something is amiss...")
        decode = self.APIdecoder[self.stc]
        fname = self.getset[self.tc] + decode[0]
        rvalue = decode[2+2*int(self.tc==b'2')].decode(self.data)
        return fname,rvalue
    
    def __repr__(self):
        if self.tc == b'0':
            return "<Error>"
        return "<Response: {0}() = {1}>".format(*self._return())
        
    @classmethod
    def from_function_return(cls,fname,rvalue):
        newcls = cls(b'1',b'0',b'')
        if 'set_' in fname:
            newcls.tc = b'2'
        fnamebase = "_".join(fname.split("_")[1:])
        newcls.stc = cls.APIencoder[fnamebase]
        if not rvalue is None:
            newcls.data = cls.APIdecoder[newcls.stc][2+2*int(newcls.tc == b'2')].encode(rvalue)
        return newcls

    @classmethod
    def from_error(cls,error):
        return cls(b'0',b'0',b'')
    