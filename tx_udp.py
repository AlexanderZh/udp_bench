import socket
from struct import pack
from time import perf_counter

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = bytearray([48]*64)

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
#print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
i = 0
while True:
    sock.sendto(pack("IF",i) + MESSAGE, (UDP_IP, UDP_PORT))
    i += 1

