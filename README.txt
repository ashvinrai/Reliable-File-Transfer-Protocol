Vagdevi Kondeti - vkondeti@gatech.edu
Ashvin Rai – ashvinrai@gmail.com 
CS 3251 - A, 11/23/2016
Sockets Programming Assignment 2

-----------------------------------------------------------------------------------------------------------------------------------
FILES SUBMITTED
-----------------------------------------------------------------------------------------------------------------------------------
FTA-server.py - This is the server using  the Reliable File Transfer Protocol
FTA-client.py - This is the client using  the Reliable File Transfer Protocol
utils.py – This contains useful methods that both the client and server calls upon
story.txt - This is an example file used to utilize the protocol
FTA Proposal.doc – This documents in-depth how the protocol works

-----------------------------------------------------------------------------------------------------------------------------------
PROTOCOL
-----------------------------------------------------------------------------------------------------------------------------------
This project implements a protocol similar to TCP built on top of the unreliable UDP protocol. Its main benefits are that it will ensure in-order delivery while also accounting for corrupt or dropped packets.

This uses the sliding-window protocol to transfer a file by sending x number of packets each same time. The default size of the sliding window is 5, but both the client and server can adjust the size.

-----------------------------------------------------------------------------------------------------------------------------------
HOW TO RUN
-----------------------------------------------------------------------------------------------------------------------------------
No compilation is needed! Environment must have installed Python (version 2.7 preferred)
In the command prompt, navigate to the directory where the .py files are located.

Run the server file first by typing:
python FTA-server.py <port> 
(*User can also type ‘-d’ as an added argument at the end for debug mode)

Then run the client by typing:
Python FTA-client.py <IP> <port>
(*User can also type ‘-d’ as an added argument at the end for debug mode)

The client takes in the following commands:
 “connect”
“get <filename>”
“post <filename>”
“window <int>”
“disconnect”

The server takes in the following commands:
“window <int>”
“terminate”

EXAMPLE:
Once the server and client are running, type “connect” and “get story.txt” in the client command line. Watch as the server then sends the file to the client. 

Please note that the client must use “connect” command before being able to get/post a file. 

-----------------------------------------------------------------------------------------------------------------------------------
LIMITATIONS & BUGS
----------------------------------------------------------------------------------------------------------------------------------- 
The protocol does not handle if the filename does not exist. 
It also does not support multiple clients connecting. 

