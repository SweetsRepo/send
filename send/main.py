"""
Test for file transmission
"""
import os
import sys
import shutil
import argparse

import zmq
import zmq.auth as auth
from zmq.auth.thread import ThreadAuthenticator

from manager import manager
from manager import BASEDIR, KEYSDIR, PUBKEYS, PRIVKEYS

def _generate_security_keys():
    """
    Checks if the directory for security keys already exists. If not, create
    them, generate keys, and organize into public-private directories.
    """
    gen_keys = False
    if not os.path.exists(KEYSDIR):
        os.mkdir(KEYSDIR)
        gen_keys = True
    if not os.path.exists(PUBKEYS):
        os.mkdir(PUBKEYS)
        gen_keys = True
    if not os.path.exists(PRIVKEYS):
        os.mkdir(PRIVKEYS)
        gen_keys = True

    if gen_keys:
        tx_public_file, tx_private_file = auth.create_certificates(
            KEYSDIR,
            "tx"
        )
        rx_public_file, rx_private_file = auth.create_certificates(
            KEYSDIR,
            "rx"
        )
        # Move keys around to the appropriate directories
        for key_file in os.listdir(KEYSDIR):
            if key_file.endswith(".key"):
                shutil.move(
                    os.path.join(KEYSDIR, key_file),
                    os.path.join(PUBKEYS, ".")
                )
            elif key_file.endswith(".key_secret"):
                shutil.move(
                    os.path.join(KEYSDIR, key_file),
                    os.path.join(PRIVKEYS, ".")
                )

def main():
    """
    Runs SEND either in transmitter or receiver mode

    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--transmit",
        action="store_true",
        help="Flag indicating that user will be transmitting files"
    )
    parser.add_argument(
        "-r",
        "--receive",
        action="store_true",
        help="Flag indicating that user will be receiving files"
    )
    parser.add_argument(
        "--location",
        help="Location of files to send/receive. Can be a specific file if tx."
    )
    parser.add_argument(
        "--ip",
        help="IP Address to form connection with"
    )
    parser.add_argument(
        "--port",
        nargs='?',
        const=6000,
        default=6000,
        type=int,
        help="Port to form connection with (only needed if using non-default)"
    )
    parser.add_argument(
        "--public_key",
        nargs='?',
        help="Public Key of transmitter in plain-text (only needed if receiver)"
    )
    args=parser.parse_args()

    # Security Authentication Thread
    _generate_security_keys()
    authenticator = ThreadAuthenticator(manager.ctx)
    authenticator.start()
    whitelist = [
        "127.0.0.1",
        args.ip
    ]
    authenticator.allow(*whitelist)
    authenticator.configure_curve(domain="*", location=PUBKEYS)

    try:
        if args.transmit:
            thread = manager.publish_folder(
                args.port,
                args.location
            )

        elif args.receive:
            thread = manager.subscribe_folder(
                args.ip,
                args.port,
                args.location,
                args.public_key
            )
        else:
            raise ValueError(f"User did not specify transmit/receive")

    except (OSError, ValueError):
        raise

    except KeyboardInterrupt:
        pass

    finally:
        # Keep things rolling until the transfer is done or the thread dies from
        # timing out
        while thread.isAlive():
            pass
        thread.join()
        # Clean up and close everything out
        authenticator.stop()
        # Use destroy versus term: https://github.com/zeromq/pyzmq/issues/991
        manager.ctx.destroy()

if __name__ == '__main__':
    main()
