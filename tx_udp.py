import socket
from struct import pack

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = ["a"]*10 

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
#print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
#MESSAGE = pack("I",i) + MESSAGE
for i in range(0,10000000):
    sock.sendto(pack("I",i) + str(MESSAGE), (UDP_IP, UDP_PORT))
    #sock.sendto(pack("I",i) + str(MESSAGE), (UDP_IP, UDP_PORT))
