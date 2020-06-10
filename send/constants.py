from types import SimpleNamespace

# Binary Packet IDs
_ids = dict(
    ERR = b'-1',
    ACK = b'0',
    WELCOME = b'1',
    UPDATES = b'2',
    NAME = b'3',
    DONE = b'4',
    FETCH = b'5'
)

PacketIdentifiers = SimpleNamespace(**_ids)
CHUNK_SIZE = 250000
PIPELINE = 10

def updates(flag):
    """
    Dummy function for testing
    """
    return flag
