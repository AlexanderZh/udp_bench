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


INPUT PARAMETERS:
- packet_size
- delay between packets (no jitter) - results in bandwidth output
- number of concurrent connections (sockets) - limited by portrange

MEASUREMENT PARAMETERS:
- packet_size range ans step
- delay range and step
- connections number (range)
- numer of packets for each measurement

MEASURABLE VALUES:
- delay for packets (time sync required or use reflector script)
- amount of losses
- jitter
- bandwidth
"""

import socket
from struct import pack,unpack
from time import perf_counter, sleep, time
import argparse
from multiprocessing import Pool
from functools import partial

def sender_thrd(UDP_IP, packet_size_range, delay_range, N, UDP_PORT):

    sock = socket.socket(socket.AF_INET, #
                     socket.SOCK_DGRAM) # UDP
    for size in packet_size_range:
      for delay in delay_range:
          MESSAGE = bytearray([48]*(size-12))
          #send actual params
          sock.sendto(pack("IIf",N,size,delay), (UDP_IP, UDP_PORT))
          sleep(0.1)
          t1 = time()
          for i in range(0,N):
          #begin measurement
              sock.sendto(pack("Id",i,time()) + MESSAGE, (UDP_IP, UDP_PORT))
              if i%1000 == 0:
                  sleep(1*delay)
          #end measurement
          t2 = time()
          dt = t2 -t1
          rate_pkt = 0.000001*N/dt
          rate_bts = 8*rate_pkt*size          
          sleep(0.1) #wait 0.1s for processing on receiver side
          sock.sendto(bytearray([0]*1), (UDP_IP, UDP_PORT))
          sleep(0.1) #wait 0.1s for processing on receiver side
          print(UDP_PORT,"\t\t",size,"\t\t",round(delay,4),"\t\t",round(rate_pkt,5),"\t\t",round(rate_bts,3))
        

def sender(UDP_IP="127.0.0.1", UDP_PORT=5000, packet_size_range = [1500], delay_range = [0], port_range = [6000], N = 1000000):
    print("Starting sender (receiver should be already running)")
    print("target ip:",UDP_IP)
    print("target port (manage):",UDP_PORT)
    print("N packets:",N)
    print("packet sizes:",packet_size_range)
    print("delay (us):", delay_range)
    print("port range:", port_range)

    #Send measurement params to receiver:
    sock = socket.socket(socket.AF_INET, #
                     socket.SOCK_DGRAM) # UDP
    sock.sendto(b"START",(UDP_IP, UDP_PORT))
    
    # tell how many ports to open
    sock.sendto(pack("II",len(port_range),port_range[0]), (UDP_IP, UDP_PORT))
    sleep(0.1)

    pool = Pool(len(port_range))
    func_sender = partial(sender_thrd, UDP_IP, packet_size_range, delay_range, N)
    print("PORT\t\tSIZE (B)\tDELAY (us)\t\tRATE (Mpps)\t\tRATE(Mbps)")
    results = pool.map(func_sender, port_range)
    #close the pool and wait for the work to finish 
    pool.close()
    pool.join()
    # tell to complete measurement
    sock.sendto(b"COMPLETE",(UDP_IP, UDP_PORT))
    print("Complete")

def receiver_thrd(UDP_IP,UDP_PORT):
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    
    while True:      
      data = [] #received data
      n_packets = 0
      #get starting packet with params
      _data, addr = sock.recvfrom(10000) # buffer size is 1024 bytes
      print(_data, addr)
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
            data.append(_data[:16] + pack('d', time()))
        else:
            break
      dt = perf_counter() - t0
      
      distro = {}
      cur_packet = 0
      n_bad_packets = 0
      mean_latency = 0
      for i in range(0,n_packets-1):
        next_packet, time1, time2 = unpack('Idd',data[i])
        #print(time1, time2)
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
      #with open('results.txt', 'a+') as f:
      #    f.write('{0};{1};{2};{3};{4};{5};{6}\n'.format(size,N_packets_sent,delay,(N_packets_sent - n_packets + 1)/N_packets_sent, mean_latency/n_packets, n_packets/dt/1000, n_packets*size*8/dt/1000000) )  

#      for key in distro.keys():
#        print("distro: ", key, ':', distro[key],"\t")

def receiver(UDP_IP="0.0.0.0", UDP_PORT=5000, file_out="results.csv"):
    print("UDP server IP:", UDP_IP)
    print("UDP server management port:", UDP_PORT)
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    while True:
      _data, addr = sock.recvfrom(10000) # buffer size is 10KB
      print(_data, addr)
      if len(_data) == 5 and _data == b"START":
          print("Received START command")
          break
      else:
          print('Receiver should be started before sender!')
          return
    _data, addr = sock.recvfrom(10000) # buffer size is 10KB
    if len(_data) != 8:
      print("Somehow invalid parameters received")
      return
    port_number, port_first = unpack('II',_data)
    port_range = range(port_first, port_first+port_number)
    print("Setting port_range: ", port_range)
    func_receiver = partial(receiver_thrd, UDP_IP)
    pool = Pool(len(port_range))
    print("PORT\t\tSIZE (B)\tDELAY (us)\t\tRATE (Mpckts/s)\t\tRATE(Mbit/s)")
    
    results = pool.map(func_receiver, port_range)

    #close the pool and wait for the work to finish 
    pool.close()
    pool.join()
    # tell to complete measurement
    while True:
      _data, addr = sock.recvfrom(10000) # buffer size is 10KB
      print(_data, addr)
      if len(_data) == 7 and _data == "COMPLETE":
          print("Received COMPLETE command")
          break
      else:
          print('Receiver got shit instead of complete!')
          return
    print("Successfully completed, savine to file")
    with open("file_out", "w+") as f:
      f.write(results)
    

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
    port_range = []
    for port in range(6000,7000):
      port_range.append(port)

    if args.SENDER:
        sender(UDP_IP="127.0.0.1", UDP_PORT=5000, packet_size_range = [1500], delay_range = [0.1], port_range = port_range, N = 1000)
    else:
        receiver(UDP_IP="0.0.0.0",UDP_PORT=5000)