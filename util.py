import binascii
import array

def make_packet(source_port, dest_port, seq, acknum, syn, ack, end, window, data):
	#flags = 0 | (SYN << 2) | (ACK << 1) | END 
	header = "%s|%i|%i|%i|%r|%r|%r|%i" % (str(source_port), int(dest_port), int(seq), int(acknum), syn, ack, end, int(window)) 
	headerPart = str(header.split('|'))
	checksum = create_checksum(headerPart + data)
	packet = "%s|%s|%s" % (header, data, checksum)
	#SYN, ACK, END = 0, 1, 1
	#00000000 | (SYN << 2) | (ACK << 1) | END 
	return packet

def unpack_packet(packet):
	parts = packet.split('|')
	header = parts[0:8]
	data = parts[8]
	checksum = parts[-1]
	return header, data, checksum

def create_checksum(packet):
	return str(binascii.crc32(packet) & 0xffffffff)

def check_checksum(packet):
	header, data, checksum = unpack_packet(packet)
	return create_checksum(str(header) + str(data)) == str(checksum)

def request_file(filename):

	try:
		f = open(filename, 'r')
	except:
		print "file not found"
		return None
	x = True
	l = []
	while(x):
		div = f.read(512)
		if (div != ""):
			l.append(div)
		else:
			x = False

	return l