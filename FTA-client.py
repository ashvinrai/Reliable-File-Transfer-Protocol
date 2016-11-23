import util
import sys
import socket

debugMode = False
def log(s):
    if debugMode:
        print s

if len(sys.argv) < 4:
    print 'Too little arguments! Must input FTA-Client.py, server IP and port (optional: \'-d\' for debug mode)'
    sys.exit()
elif len(sys.argv) > 4:
    if len(sys.argv) == 5 and sys.argv[4] == "-d":
        debugMode = True
        log("Entering debug mode...")
    else:
        print 'Too many arguments! Must input FTA-Client.py, server IP and port (optional: \'-d\' for debug mode)'
        sys.exit()
TIMEOUT_SECONDS = 20
SOURCE_IP = sys.argv[1]
SOURCE_PORT = int(sys.argv[2])
window = 5
putwindow = 5
State = "NONE"
seq = 0
acknum = 1
ipv4 = True
if (sys.argv[3] == "-v6"):
  ipv4 = False
elif (sys.argv[3] == "-v4"):
  ipv4 = True
else:
  print "-v4 or -v6 required"
if(ipv4):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
else:
  s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
dest_addr = (SOURCE_IP, int(SOURCE_PORT))
while (True):
   word = str(raw_input('Commands: connect, get <filename>, put <filename>, window <size>, disconnect, server window <size>, server terminate, exit: '))
   word = str.split(word)
   if (word[0] == "connect"):
      if len(word) != 1:
        print "invalid command"
      elif State == "NONE":
        #Three way handshake
        if(ipv4):
          s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
          s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        packet = util.make_packet("", SOURCE_PORT, seq, acknum, True, False, False, window, "SYN") #Send SYN. Flags = SYN, ACK, END
        s.sendto(packet, dest_addr)
        log('Packet sent. SYN = True')
        packet, addr = s.recvfrom(4096)
        header, data, checksum = util.unpack_packet(packet)
        log('Received packet. SYN =' + header[4] + ' ACK = ' + header[5] + '. . .')
        if (header[4].strip() == "True" and header[5].strip() == "True"):
          packet = util.make_packet("", SOURCE_PORT, seq, acknum, False, True, False, window, "ACK")
          s.sendto(packet, dest_addr)
          log('Packet sent. ACK = True')
          print 'Connection is established'
          State = "CONNECTED"
   elif (word[0] == "server"):
      if len(word) < 2 or len(word) > 3:
        print "invalid command; server command required: server window <size> or server terminate"
      elif State != "CONNECTED":
        print 'Cannot communicate with server: You did not create a connection yet!'
      else:
        log("attempting server commands")
        if word[1] == "window" and len(word) == 3:
          windowToSend = word[2]
          packet = util.make_packet("", SOURCE_PORT, seq, acknum, True, False, False, window, "putwindow " + windowToSend) #Send SYN. Flags = SYN, ACK, END
          s.sendto(packet, dest_addr)
          putwindow = int(windowToSend)
          log('New window size: ' + str(putwindow))
        elif word[1] == "terminate" and len(word) == 2:
          packet = util.make_packet("", SOURCE_PORT, seq, acknum, True, False, False, window, "terminate")
          s.sendto(packet, dest_addr)
          print "server shut down"
   elif (word[0] == "get"):
      if len(word) != 2:
        print "invalid command; file name required"
      elif State == "CONNECTED":
        acknum = 0
        filename = word[1]
        log('get command with filename: ' + filename)
        packet = util.make_packet("", SOURCE_PORT, seq, acknum, True, False, False, window, "get " + filename)
        s.sendto(packet, dest_addr)
        ##TO-DO
        ##Sent filename to server. Server must now send the file back
        packets = []
        end = False
        msg = ""
        while end != True:
          x = 0
          while x < window:
            #s.settimeout(TIMEOUT_SECONDS)
            packet, addr = s.recvfrom(4096)
            header, data, checksum = util.unpack_packet(packet)
            if str(acknum) == header[2] and header[4] and util.check_checksum(packet):
              packets.append(packet)
              x += 1
              acknum += 1
              msg += data 
              if header[6] == "True":
                packet = util.make_packet("", SOURCE_PORT, seq, acknum, False, True, True, window, "END")
                s.sendto(packet, dest_addr)
                x = window
                end = True
            else:
              x = window
              print "missing or damaged packet"
          packet = util.make_packet("", SOURCE_PORT, seq, acknum, False, True, False, window, "ACK")
          s.sendto(packet, dest_addr)
        newFile = "GET" + filename
        f = open(newFile, 'w')
        f.write(msg)
        f.close()
      else:
        print 'Cannot get a file: You did not create a connection yet!'
   elif (word[0] == "window"):
      if len(word) != 2:
        print "invalid command"
      elif State != "CONNECTED":
        print 'Cannot change window: You did not create a connection yet!'
      else:
        windowToSend = word[1]
        packet = util.make_packet("", SOURCE_PORT, seq, acknum, True, False, False, window, "window " + windowToSend) #Send SYN. Flags = SYN, ACK, END
        s.sendto(packet, dest_addr)
        window = int(windowToSend)
        log('New window size: ' + str(window))
   elif (word[0] == "disconnect"):
      if len(word) != 1:
        print "invalid command"
      elif State != "CONNECTED":
         print 'Cannot disconnect: You did not create a connection yet!'
      else:
         State = 'NONE'
         packet = util.make_packet("", SOURCE_PORT, seq, acknum, True, False, False, window, "disconnect")
         s.sendto(packet, dest_addr)
         s.shutdown(socket.SHUT_RDWR)
         s.close()
         log('Connection has been disconnected!')
   elif (word[0] == "put"):
      if len(word) != 2:
        print "invalid command; file name required"
      elif (State != "CONNECTED"):
          print 'Cannot post: You did not create a connection yet!'
      else:
          seq = 0
          filename = word[1]
          log('Sending file: ' + filename)
          packet = util.make_packet("", SOURCE_PORT, seq, acknum, True, False, False, putwindow, "put " + filename)
          s.sendto(packet, dest_addr)
          data = util.request_file(filename)
          packets = []
          x = 0
          window_pointer = 0
          while x < len(data):
            if x == len(data) - 1:
              packet = util.make_packet("", SOURCE_PORT, x, acknum, True, False, True, putwindow, data[x])
            else:
              packet = util.make_packet("", SOURCE_PORT, x, acknum, True, False, False, putwindow, data[x])
            packets.append(packet)
            x += 1
          
          if (len(packets) < window):
            while window_pointer < len(packets):
              s.sendto(packets[window_pointer], addr)
              window_pointer+=1
              end = "True"
          else:
            while window_pointer < window:
              s.sendto(packets[window_pointer], addr)
              window_pointer+=1
              end = "False"
          #s.settimeout(TIMEOUT_SECONDS)
          packet, addr = s.recvfrom(4096)
          header, data, checksum = util.unpack_packet(packet)
          seq = int(header[3])
          while end != "True": 
            window_pointer = 0
            while window_pointer < window:
              s.sendto(packets[window_pointer + seq], dest_addr)
              if(seq+window_pointer == len(packets) - 1):
                window_pointer = window
              else:
                window_pointer+=1
            #s.settimeout(TIMEOUT_SECONDS)
            packet, addr = s.recvfrom(4096)
            header, data, checksum = util.unpack_packet(packet)
            seq = int(header[3])
            end = header[6]
          packet, addr = s.recvfrom(4096)
          print "File transfer complete"
   elif (word[0] == "exit"):
      print "goodbye..."
      sys.exit()
   else:
      print "invalid command entered"