"""
Prototype Broadcaster which holds a collection of folders that are available
to send and graphs of subscribers.

"""
import os
import socket
from uuid import uuid4
from threading import Thread

import zmq
import zmq.auth as auth

from permissions import _permissions
from receiver import receiver_thread
from transmitter import transmitter_thread
from zmqhelpers import *

# Directories used by authentication
BASEDIR = os.path.dirname(__file__)
KEYSDIR = os.path.join(BASEDIR, "certs")
PUBKEYS = os.path.join(BASEDIR, "public_keys")
PRIVKEYS = os.path.join(BASEDIR, "private_keys")

class Manager:
    """
    The manager class holds all information about folders which are being
    shared, systems that they are shared with, and the permissions of those
    systems. A single instance is created at program start time and then
    imported as a module

    (e.g.)
    ```python
    from manager import manager
    ```

    Attributes:
        uuid: Universally Unique Identifier specified by RFC 4122
        permissions: Dictonary mapping directories/files to mappings of GUIDs
                     and metadata (status, permission levels, etc)
        ip: IP Address of local system
        ctx: Singleton ZMQ.Context to manage connections

    """
    def __init__(self, permissions):
        self.uuid = uuid4()
        self.permissions = permissions

        # Get the correct IP address for broadcasting
        ip = socket.gethostbyname(socket.gethostname())
        if ip[:3] == "127":
            ip = socket.gethostbyname(socket.gethostname()+".local")
        self.ip = ip
        self.ctx = zmq.Context()

    def configure_socket(
            self,
            socket,
            keyfile:str,
            keypath:str=PRIVKEYS,
            public_key_path:str=None
        ):
        """
        Takes the given socket and configures it to use the public-private
        keypair defined in the key_file

        Arguments:
            socket: ZMQ Socket Object to configure
            keyfile: Key file to load public-private keypair for
            keypath: Path to Key File. If not specified a default is used
            public_key (optional): Public key for receivers connecting to remote
                                   systems

        Returns:
            socket: Configured socket with end to end elliptic curve encryption

        """
        private_file = os.path.join(keypath, keyfile)
        public_key, private_key = auth.load_certificate(private_file)
        socket.curve_secretkey = private_key
        socket.curve_publickey = public_key

        if socket.socket_type in [zmq.DEALER, zmq.SUB]:
            # Checks if key path is actually a path. Otherwise assume a string
            # representation of the key was given and needs to be encoded
            if os.path.exists(public_key_path):
                tx_public, _ = auth.load_certificate(public_key_path)
            else:
                tx_public = bytes(public_key_path, "UTF-8")
            socket.curve_serverkey = tx_public
        elif socket.socket_type in [zmq.ROUTER, zmq.PUB]:
            socket.curve_server = True
        else:
            raise TypeError(f"Socket type {socket_type} is not supported")
        return socket


    def publish_folder(self, port:str, dname:str):
        """
        Creates a socket to share the specified directory over. Stores a copy of
        the transmission socket in the folders dictionary. Will eventually store
        a collection of reciever nodes and their folder permissions (R,RW, Pull)

        Arguments:
            dname: Directory name of the folder being published for sharing.

        Returns:
            transmitter: Handle the transmitter thread, automatically running
        Notes:
            The dictionary will maintain a list of tuples where each tuple is
            comprised of the the remote entity's IP and it's permissions.
        """
        socket = self.ctx.socket(zmq.ROUTER)
        socket = self.configure_socket(
            socket,
            "tx.key_secret",
            PRIVKEYS
        )
        transmitter = Thread(
            target = transmitter_thread,
            args=(
                self.uuid,
                socket,
                port,
                dname
            )
        )
        # Perform some record keeping, then start the transmitter
        # if os.path.abspath(dname) not in self.permissions:
        #     self.permissions[os.path.abspath(dname)] = {}
        # self.permissions[os.path.abspath(dname)].append(transmitter)
        transmitter.start()
        return transmitter


    def subscribe_folder(
            self,
            ip:str,
            port:str,
            dname:str,
            pubkey:str
        ):
        """
        Creates a subscription to the remote ip and stores results in directory

        Arguments:
            ip: Remote IP and port number to connect to as a string
            dname: Directory name of the location to store updates from remote

        Returns:
            receiver: Handle to the receiver thread, automatically running

        """
        if pubkey is None:
            pubkey = os.path.join(PUBKEYS, "tx.key")
        socket = self.ctx.socket(zmq.DEALER)
        socket = self.configure_socket(
            socket,
            "rx.key_secret",
            PRIVKEYS,
            pubkey
        )
        receiver = Thread(
            target=receiver_thread,
            args=(
                self.uuid,
                socket,
                ip,
                port,
                dname
            )
        )
        receiver.start()
        return receiver

    def get_public_key(self):
        """
        Gets the public key for this machine. Meant to transfer to remote user
        to initiate transfer
        """
        public_key_path = os.path.join(PUBKEYS, "tx.key")
        if os.path.exists(public_key_path):
            tx_public, _ = auth.load_certificate(public_key_path)
            return tx_public
        else:
            raise FileNotFoundError("Failed to find public key for this system. Consider running main._generate_security_keys( )")

    def map_network(self):
        """
        Sends a pulse out to each synchronized folders connections to map
        network connectivity.

        NotImplemented: This is a stub for what will be a part of ARGS

        """
        pass

manager = Manager(_permissions)
