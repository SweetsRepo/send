"""
Transmitter thread which will handle requests for a file and send it out to the
requestor.

Notes:
    Use of Router-Dealer instead of Pub-Sub (this is a better choice though)

"""
import os
import datetime as dt
from datetime import datetime

import zmq

from permissions import _permissions
from zmqhelpers import socket_set_hwm
from constants import PacketIdentifiers, updates

PIPELINE = 10

def transmitter_thread(sys_id, router, port, dname):
    """
    Creates a new thread for transmitting files from the specified directory
    using the router and port number given. Updates can be configured to be
    continuous over time, keeping the thread alive, or a one time transfer.

    Arguments:
        sys_id: System Univerally Unique ID
        router: Socket configured to transmit data to remote entity
        port: Port number to transmit out via (assigned by system Manager)
        dname: Directory of files to transmit

    Notes:
        Directory structure should be sent ahead of file transmission so that
        the remote entity can maintain an accurate representation of the folder
        hierarchy within their machine.

    """
    # Control variables for FSM
    handshake = False
    update_in_progress = False
    remote_id = None

    if not os.path.exists(dname):
        raise ValueError(f"Directory ({dname}) does not exist")

    socket_set_hwm(router, PIPELINE)
    router.bind(f"tcp://*:{port}")
    router.setsockopt(zmq.RCVTIMEO, 1000)

    # Run until transfer is complete - Retries connection for 5 minutes
    timeout = datetime.now() + dt.timedelta(minutes=30)
    ## TODO: Continuous update mode should not break this loop
    while True:
        if not handshake:
            try:
                remote_id, msg, remote_uuid = router.recv_multipart()
                if msg == PacketIdentifiers.WELCOME:
                    router.send_multipart([
                        remote_id,
                        PacketIdentifiers.ACK,
                        sys_id.bytes
                    ])
                    handshake = True
                    print("TX: Welcomed - Starting Transfer")
                    _permissions[dname] = {
                        remote_uuid:{
                            "permission": "wo",
                            "status": PacketIdentifiers.WELCOME
                        }
                    }
            except zmq.ZMQError as e:
                if datetime.now() > timeout or e.errno == zmq.ETERM:
                    # print("TX: Startup Failed")
                    break

        else:
            # Emulate that there were updates detected on the system and resend
            # everything (for now). Need to keep track of if UPDATES has already
            # been sent previously and not resend
            if updates(True) and not update_in_progress:
                router.send_multipart([remote_id, PacketIdentifiers.UPDATES])
                # Get all the files to transfer into a single list and then iterate
                # as the receiver indicates it's ready for a new file
                basedir = []
                dirnames = []
                fnames = []
                # If it's a single file name instead of a directory, separate
                # directory name from file name to reuse directory transfer code
                if os.path.isfile(dname):
                    dname, fname = os.path.split(dname)
                    fnames.append(fname)
                else:
                    for a,b,c in os.walk(dname):
                        for fname in c:
                            rel_dir = os.path.relpath(a, dname)
                            fnames.append(os.path.join(rel_dir, fname))
                i = 0
                update_in_progress = True
                # print("TX: Update In Progress")

            if update_in_progress:
                try:
                    fname = fnames[i]
                    abs_fname = os.path.join(dname, fname)
                except IndexError as e:
                    # Finished all possible updates. Break to cancel cleanly
                    print("TX: Transfer Complete")
                    update_in_progress = False
                    router.send_multipart([remote_id, PacketIdentifiers.DONE])
                    break

                with open(abs_fname, "rb") as f:
                    try:
                        # print("TX: Waiting on RX Commands")
                        msg = router.recv_multipart()
                    except zmq.ZMQError as e:
                        if e.errno == zmq.ETERM:
                            # Termination request
                            # print("Term Request Issued: TX")
                            return
                        else:
                            raise
                    if msg[1] == PacketIdentifiers.DONE:
                        i += 1
                    elif msg[1] == PacketIdentifiers.NAME:
                        # print("TX: Name Request")
                        router.send_multipart([
                            remote_id,
                            PacketIdentifiers.NAME,
                            bytes(fname, encoding="utf-8")
                        ])
                    elif msg[1] == PacketIdentifiers.FETCH:
                        # print("TX: Data Request")
                        identity, command, offset_str, chunksz_str = msg
                        assert command == PacketIdentifiers.FETCH

                        offset = int(offset_str)
                        chunksz = int(chunksz_str)

                        f.seek(offset, os.SEEK_SET)
                        data = f.read(chunksz)

                        router.send_multipart([remote_id, PacketIdentifiers.FETCH, data])
                    else:
                        pass
