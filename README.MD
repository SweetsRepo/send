# SEND:
-------
SEND is a decentralized, end to end encrypted, direct file transfer system. No
middlemen, no accounts being data-mined, and no confusing setup process.
*Don't be silly; just send it!*

Built on top of zmq, SEND implements an asynchronous file transfer system that
will allow users to setup one time transfers between systems, continuous
updates over time for cross-platform file synchronization, and use simple
permission controls mirroring other commercially available systems.

## Security:
------------
Currently, SEND implements an elliptic curve encryption scheme. One common
misconception about elliptic curve encryption is that it has a backdoor.
However, elliptic curves are part of a family of functions, with most curves
still providing high fidelity security. For SEND, we make use of Curve \#25519.

## Reliability:
---------------
Beyond wanting to mine user data, other file transfer systems require log in
credentials because it greatly reduces the complexity of tracking metadata, such
as IP addresses. In order to remain completely decentralized SEND implements a
automatic reconnection gossip schema (ARGS). This protocol involves assigning
universally unique identifiers (RFC 4122 Compliant) to each system within the
SEND network, and then sharing with other's what that identifier is. Over time,
all computers within a graph build a shared routing table. When a computer
disconnects and reconnects it's IP may change. But as it broadcasts what it's
new IP is, other computers in the network will gossip about the change in that
systems IP. For more information on this reconnection protocol, read white paper
titled ARGS under the docs section.

## Current Status: Alpha-V1
----------------------------
Currently the following features are implemented in SEND:
* End to End Encryption of all File Transfers
* One-time transfer of file or entire directories
* Basic SMTP Email System for sharing connection details

## Bugs, Docs, Misc
-------------------
For status on current bugs being tracked, please see the project issue tracker.
For documentation regarding the technical details of how SEND works feel free to
read the white papers included in the docs folder. For how-to guides on usage
go to docs and view the README located there.

## Upcoming Status: Alpha-V2
----------------------------
* Proper GMail API Sign in
* System Logging
* User Configurable Timeouts
* C Implementation
* Whatever Bugs Come Along From Testing
