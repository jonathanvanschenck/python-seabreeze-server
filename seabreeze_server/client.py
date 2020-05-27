"""
:Author: Jonathan D. B. Van Schenck
"""
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
