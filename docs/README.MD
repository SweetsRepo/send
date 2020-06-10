# How-To: Alpha State
---------------------
This guide will walk through a few quick examples of how to use SEND while in
alpha state. There are currently two entry-points for the user to consider:
invitation.py and main.py

Note that in order to use the invitation.py functions for inviting others to
share and confirming invitations you must allow external connections in gmail:
https://myaccount.google.com/lesssecureapps

## Getting Started
------------------
1. Clone the Repository
```
git clone https://github.com/send-dev/send.git
```
2. Ensure Python 3.6+ and PyZMQ 18.1.1+ are installed
3. And you should now be able to send invitations and transfer files as shown
   below
   
## Invite User to Share - Email
-------------------------------
```
python invitation.py -i <user-email> <user-email-password> <target-email>
```

## Confirm Share from User - Email
-------------------------------
```
python invitation.py -c <user-email> <user-email-password> <target-email>
```

## Transmit File/Directory to User
----------------------------------
```
python main.py -t --location <file/directory> --ip <remote-ip> --port <port>
```
Note that in this example port is an optional argument

## Receive File/Directory from User
-----------------------------------
```
python main.py -r --location <file/directory> --ip <remote-ip> --port <port> --public_key "<key-plaintext>"
```
Note that in this example port is an optional argument. The public_key argument
requires " " around it if given. If not given, then tx.key must exist in the
public keys directory (would need to have been sent from the transmitter)
