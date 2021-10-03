import socket
import time
import sys

#UDP_RCV_IP = '10.10.10.10'
UDP_RCV_IP = '127.0.0.1'
UDP_RCV_PORT = 7777
#UDP_SND_IP = '192.168.0.102'
UDP_SND_IP = '127.0.0.1'
UDP_SND_PORT = 7778


sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_snd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    sock_rcv.bind((UDP_RCV_IP, UDP_RCV_PORT))
    print('bind ok on ', UDP_RCV_IP, UDP_RCV_PORT)
except Exception:
    print('binding failed on ' + UDP_RCV_IP, UDP_RCV_PORT)

while True:
    data, addr = sock_rcv.recvfrom(4096)

    sock_snd.sendto(data, (UDP_SND_IP, UDP_SND_PORT))
    print(time.ctime() + data.decode())

