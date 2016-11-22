import socket
import util
import sys
import array
debugMode = False
def log(s):
    if debugMode:
        print s

if len(sys.argv) < 3:
    print 'Too little arguments! Must input FTA-Server.py, port, and IP version (optional: \'-d\' for debug mode)'
    sys.exit()
elif len(sys.argv) > 3:
    if len(sys.argv) == 4 and sys.argv[3] == "-d":
        debugMode = True
        log("Entering debug mode...")
    else:
        print 'Too many arguments! Must input FTA-Server.py, port, and IP version (optional: \'-d\' for debug mode)'
        sys.exit()
TIMEOUT_SECONDS = 20
window = 5
putwindow = 5
window_pointer = 0
SOURCE_PORT = int(sys.argv[1])
seq = 0
acknum = 0
ipv4 = True
if (sys.argv[2] == "-v6"):
	ipv4 = False
elif (sys.argv[2] == "-v4"):
	ipv4 = True
else:
	print "-v4 or -v6 required"
if(ipv4):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
else:
	s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
s.bind(('', SOURCE_PORT))
print 'Listening on port', SOURCE_PORT, '...'
not_connected = True
established = False
while (True):
	if (not_connected):
		packet, addr = s.recvfrom(4096)
		header, data, checksum = util.unpack_packet(packet)
		log('Received packet. SYN = ' +  header[4] + '. . .')
		if (header[4].strip() == "True"): #Receive SYN
			packet = util.make_packet("", SOURCE_PORT, seq, acknum, True, True, False, window, "") #Send SYNACK
			s.sendto(packet, addr)
			log('Sent SYN ACK . . .')
			packet, addr = s.recvfrom(4096)
			header, data, checksum = util.unpack_packet(packet)
			log('Received packet. ACK = ' + header[5])
			if (header[5].strip() == "True"):
				not_connected = False
				established = True
				print 'Connection is Established'

	if (established):
		packet, addr = s.recvfrom(4096)
		header, data, checksum = util.unpack_packet(packet)
		cmd = data.split(" ")[0]
		print 'cmd =', cmd
		if cmd == 'window':
			window = int(data.split(" ")[1])
			log('New window size: ' + str(window))
		elif cmd == 'terminate':
			print 'Client disconnected'
			established = False
			not_connected = True
		elif cmd == "get":
			seq = 0
			filename = data.split(" ")[1]
			log('Requesting filename: ' + filename)
			##TO-DO
			##Received filename from client. Now must send the file over to client
			data = util.request_file(filename)
			packets = []
			x = 0
			window_pointer = 0
			while x < len(data):
				if x == len(data) - 1:
					packet = util.make_packet("", SOURCE_PORT, x, acknum, True, False, True, window, data[x])
				else:
					packet = util.make_packet("", SOURCE_PORT, x, acknum, True, False, False, window, data[x])
				packets.append(packet)
				x += 1
			
			#first [window] packets sent
			while window_pointer < window:
				s.sendto(packets[window_pointer], addr)
				window_pointer+=1
			#s.settimeout(TIMEOUT_SECONDS)
			packet, addr = s.recvfrom(4096)
			print packet
			header, data, checksum = util.unpack_packet(packet)
			seq = int(header[3])
			end = "False"
			while end != "True": 
				window_pointer = 0
				while window_pointer < window:
					s.sendto(packets[window_pointer + seq], addr)
					if(seq+window_pointer == len(packets) - 1):
						window_pointer = window
					else:
						window_pointer+=1
				#s.settimeout(TIMEOUT_SECONDS)
				packet, addr = s.recvfrom(4096)
				print packet
				header, data, checksum = util.unpack_packet(packet)
				seq = int(header[3])
				end = header[6]
			packet, addr = s.recvfrom(4096)
			print "File transfer complete"

	##This method of getting user input cannot work; can have a diff thread for listening to user input instead
	#word = str(raw_input(''))
	#if (word[0] == "window"):
	#	window = word[1]
	#if (word[0] == "terminate"):
	#	s.close()