#!/usr/bin/python3
"""
Author:ZAG
A pair of scripts for unidirectional UDP benchmarks:
- receiver is run in while-true loop
- sender send N packets (1M by default) of SIZE (64 bytes by default) with DELAY (0) between packets
- Each udp packet is enumerated
- Missed and disordered packets are treated like errors
- Errors are counted on receiver side
- each packet also contains timestamp to measure latency (receiver should be running on the same host)
"""

import socket
from struct import pack,unpack
from time import perf_counter, sleep
import argparse


def sender(UDP_IP="127.0.0.1", UDP_PORT=5555, N=1000000, size=64, delay=0):
    print("Starting sender (receiver should be already running)")
    print("target ip:",UDP_IP)
    print("target port:",UDP_PORT)
    print("N packets:",N)
    print("packet size:",size)
    print("delay between packets:", delay)
    MESSAGE = bytearray([48]*size)

    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    while True:
      for i in range(0, N):
        sock.sendto(pack("I",i) + MESSAGE, (UDP_IP, UDP_PORT))
        sleep(delay)
      #death packet
      print("sending death packet")
      sock.sendto(bytearray([0]*1), (UDP_IP, UDP_PORT))
        
    print("Complete")

def receiver(UDP_IP="0.0.0.0", UDP_PORT=5555):
    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    
    while True:      
      data = [] #received data
    #for i in range(0,1000000):
      n_packets = 0
      while True:
        _data, addr = sock.recvfrom(10000) # buffer size is 1024 bytes
        n_packets += 1
        
        if len(_data) > 1:
            data.append(_data[:4])
        else:
            print("got death packet, analyzing...")
            break
      #end for was here

      distro = {}
      cur_packet = 0
      n_bad_packets = 0
      for i in range(0,n_packets-1):
        next_packet = unpack('I',data[i])[0]
        if cur_packet != 0:
            delta = next_packet - cur_packet
        else:
            delta = 1
        if delta in distro:
            distro[delta] += 1
        else:
            distro[delta] = 1
        cur_packet = next_packet

      print("total: ", n_packets, "\n")
      for key in distro.keys():
        print("distro: ", key, ':', distro[key],"\t")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A pair of scripts for unidirectional UDP benchmarks:\
- receiver is run in while-true loop\
- sender send N packets (1M by default) of SIZE (64 bytes by default, 9K max) with DELAY (0) between packets\
- Each udp packet is enumerated\
- Missed and disordered packets are treated like errors\
- Errors are counted on receiver side\
- each packet also contains timestamp to measure latency (receiver should be running on the same host)')
    parser.add_argument("-S", "--SENDER", dest="SENDER", default=False, help="is sender (receiver by default)", metavar="SENDER")
    parser.add_argument("-i", "--ipaddress", dest="ipaddress", default="127.0.0.1", help="ip address")
    parser.add_argument("-p", "--udpport", dest="udpport", default=5555, help="udp-ip port")
    
    parser.add_argument("-n", "--N", dest="N", default=1000000, help="number of generated packets (SENDER only)")
    parser.add_argument("-s", "--size", dest="size", default=64, help="default packet size in bytes, min - 10B, max - 9KB (SENDER only)")
    parser.add_argument("-d", "--delay", dest="delay", default=0, help="delay between packets in us, default 0 (SENDER only)")
   
    
    args = parser.parse_args()
    #TODO: validate args and pass to functions
    #TODO: add min-max-step for packet size and delay
    #TODO: substract 
    if args.SENDER:
        sender(N=int(args.N), delay=float (args.delay), size = int(args.size))
    else:
        receiver()



