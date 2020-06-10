"""
Underlying Singleton dictionary collecting permission information on all active
connections. Transmitter and Reciever Threads have direct access to the object
and will make their additions at the completion of the handshake process. All
other aspects of SEND will access this via the pointer stored in manager.

TODO:
    Instead of relying on atomicity of python built-ins create a proper
    Lock and Queue system.
"""
from collections import UserDict

class Permissions(UserDict):
    """
    Overridden instance of dictionary with some functions to simplify access and
    searching through data.

    Attributes:
        data: Underlying dictionary containing hierarchical data.

    """
    def __init__(self):
        self.data = {}

_permissions = Permissions()
