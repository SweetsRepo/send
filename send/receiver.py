"""
Reciever thread which makes request for files in chunks from the transmitter.

"""
import os
import datetime as dt
from datetime import datetime

import zmq

from permissions import _permissions
from zmqhelpers import socket_set_hwm
from constants import PacketIdentifiers, PIPELINE, CHUNK_SIZE


def receiver_thread(sys_id, dealer, ip, port, dname):
    """
    Creates a thread to recieve files from a remote entity specified by ip and
    port and will store them in the local directory given.

    Arguments:
        sys_id: System Univerally Unique ID
        dealer: Socket configured to receive files from remote entity
        ip: IP address of remote entity to connect to
        port: Port of remote entity to connect to
        dname: Local directory to store recieved files from.

    Notes:
        Files will be sent over with proper folder hierarchy maintained.

    """
    # Control variables for FSM
    handshake = False
    ready_next_file = False
    rx_control = False

    if not os.path.exists(dname):
        os.mkdir(dname)

    socket_set_hwm(dealer, PIPELINE)
    dealer.connect(f"tcp://{ip}:{port}")
    dealer.setsockopt(zmq.RCVTIMEO, 1000)

    credit = PIPELINE
    total = 0
    chunks = 0
    offset = 0

    # Run until transfer is complete - Retries connection for 5 minutes
    timeout = datetime.now() + dt.timedelta(minutes=30)
    while True:
        if not handshake:
            # print("RX: Welcome Sent")
            try:
                dealer.send_multipart([PacketIdentifiers.WELCOME, sys_id.bytes])
                chunk, remote_uuid = dealer.recv_multipart()
                if chunk == PacketIdentifiers.ACK:
                    handshake = True
                    print("RX: Welcome Accepted - Starting Transfer")
                    _permissions[dname] = {
                        remote_uuid:{
                            "permission": "ro",
                            "status": PacketIdentifiers.WELCOME
                        }
                    }
            except zmq.ZMQError as e:
                if datetime.now() > timeout or e.errno == zmq.ETERM:
                    # print("RX: Startup Failed")
                    break
        else:
            if not rx_control:
                try:
                    chunk = dealer.recv()
                except zmq.ZMQError as e:
                    if e.errno == zmq.ETERM:
                        # print("Term Request Issued: RX")
                        return
                    else:
                        raise

                # Trigger for file transfer can come from either the transmitter
                # or if it's mid transfer the reciever identifies that it needs the
                # next filename. At this point control flow is determined by RX not
                # TX
                if chunk == PacketIdentifiers.UPDATES:
                    # print("RX: Get Updates")
                    ready_next_file = True
                    rx_control = True

            else:
                if ready_next_file:
                    # Request filename from transmitter
                    dealer.send_multipart([PacketIdentifiers.NAME])
                    try:
                        msg = dealer.recv_multipart()
                    except zmq.ZMQError as e:
                        if e.errno == zmq.ETERM:
                            # print("1 Term Request Issued: RX")
                            return
                        else:
                            raise

                    if msg[0] == PacketIdentifiers.DONE:
                        print("RX: Transfer Complete")
                        break

                    if msg[0] == PacketIdentifiers.NAME:
                        fname = msg[-1].decode("ascii")

                        if fname != "":
                            local_fname = os.path.join(dname, fname)
                            local_dir = os.path.split(local_fname)[0]
                            if not os.path.isdir(local_dir):
                                os.makedirs(local_dir)
                            f = open(local_fname, "wb")
                            # TODO: New File, Reset Async Parameters
                            credit = PIPELINE
                            chunks = 0
                            offset = 0
                            ready_next_file = False

                else:
                    # print("RX: Request Data")
                    while credit:
                        dealer.send_multipart([
                            PacketIdentifiers.FETCH,
                            b"%i" % offset,
                            b"%i" % CHUNK_SIZE
                        ])
                        offset += CHUNK_SIZE
                        credit -= 1
                    try:
                        msg = dealer.recv_multipart()
                    except zmq.ZMQError as e:
                        if e.errno == zmq.ETERM:
                            # print("Term Request Issued: RX")
                            return
                        else:
                            raise
                    if msg[0] == PacketIdentifiers.FETCH:
                        chunk = msg[-1]
                        chunks += 1
                        credit += 1
                        size = len(chunk)
                        total += size
                        f.write(chunk)
                        if size < CHUNK_SIZE:
                            dealer.send_multipart([PacketIdentifiers.DONE])
                            ready_next_file = True
                            # print("RX: Done Sent")
