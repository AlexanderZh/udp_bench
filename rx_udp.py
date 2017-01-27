import socket
from struct import unpack

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

#recieve first packet
data, addr = sock.recvfrom(1024)
cur_packet = unpack('I',data[:4])[0]
print "Starting from packet: " + str(cur_packet) + "\n"
n_packets = 0
n_bad_packets = 0
distro = {}
while True:
    data, addr = sock.recvfrom(10240) # buffer size is 1024 bytes
    next_packet = unpack('I',data[:4])[0]
    #while next_packet <= cur_packet:
    data, addr = sock.recvfrom(10240) # buffer size is 1024 bytes
    next_packet = unpack('I',data[:4])[0]
    delta = next_packet - cur_packet
    if distro.has_key(delta):
        distro[delta] += 1
    else:
        distro[delta] = 0
    #if next_packet - cur_packet > 1:
    #    n_bad_packets += 1
    n_packets += 1
    if n_packets%1000 == 0:
        for key in distro.keys():
            print "distro: " + str(key) + ':' + str(distro[key]) + "%\t"
        print "\n"
    cur_packet = next_packet
