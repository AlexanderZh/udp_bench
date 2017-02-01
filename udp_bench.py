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


def sender(UDP_IP="127.0.0.1", UDP_PORT=5555, N=100000, size_min = 9000, size_max = 9192, size_N = 100, delay_min = 0, delay_max = 0, delay_N = 1):
    print("Starting sender (receiver should be already running)")
    print("target ip:",UDP_IP)
    print("target port:",UDP_PORT)
    print("N packets:",N)
    #print("packet size:",size)
    #print("delay between packets:", delay)
    
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    
    for dly in range(0, delay_N):
      for sz in range(0, size_N):
        size = int(size_min + (size_max - size_min)*sz/size_N)
        delay = delay_min + (delay_max - delay_min)*dly/delay_N 
        MESSAGE = bytearray([48]*(size-8))
        #send actual params
        sock.sendto(pack("IIf",N,size,delay), (UDP_IP, UDP_PORT))
        sleep(0.1)
        #begin measurement
        for i in range(0, N):
          sock.sendto(pack("If",i,perf_counter()) + MESSAGE, (UDP_IP, UDP_PORT))
          sleep(delay)
        #end measurement
        sleep(0.1) #wait 0.1s for processing on receiver side
        sock.sendto(bytearray([0]*1), (UDP_IP, UDP_PORT))
        sleep(0.1) #wait 0.1s for processing on receiver side
        
    print("Complete")

def receiver(UDP_IP="0.0.0.0", UDP_PORT=5555):
    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    
    while True:      
      data = [] #received data
      n_packets = 0
      #get starting packet with params
      _data, addr = sock.recvfrom(10000) # buffer size is 1024 bytes
      if len(_data) == 12:
          N_packets_sent, size, delay = unpack('IIf',_data)
      else:
          print('Start receiver before sender!')
          break
      #start benchmarking
      t0 = perf_counter()
      while True:
        _data, addr = sock.recvfrom(10000) # buffer size is 1024 bytes
        n_packets += 1
        
        if len(_data) > 1:
            data.append(_data[:8] + pack('f', perf_counter()))
        else:
            break
      dt = perf_counter() - t0
      
      distro = {}
      cur_packet = 0
      n_bad_packets = 0
      mean_latency = 0
      for i in range(0,n_packets-1):
        next_packet, time1, time2 = unpack('Iff',data[i])
        mean_latency += time2 - time1
        if cur_packet != 0:
            delta = next_packet - cur_packet
        else:
            delta = 1
        if delta in distro:
            distro[delta] += 1
        else:
            distro[delta] = 1
        cur_packet = next_packet

      print("packet size:", size)
      print("packet N:", N_packets_sent)
      print("delay_between packets:", delay)
      print("total losses: ", (N_packets_sent - n_packets + 1)/N_packets_sent)
      print("mean latency:", mean_latency/n_packets)
      print("throupought:", n_packets/dt/1000, " Kpps")
      print("            ", n_packets*size*8/dt/1000000, " Mbps")
      print()

#      for key in distro.keys():
#        print("distro: ", key, ':', distro[key],"\t")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A pair of scripts for unidirectional UDP benchmarks:\
- receiver is run in while-true loop\
- sender sends N packets (1M by default) of SIZE (64 bytes by default, 9K max) with DELAY (0) between packets\
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
        sender()#N=int(args.N), delay=float (args.delay), size = int(args.size))
    else:
        receiver()



