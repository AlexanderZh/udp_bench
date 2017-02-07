import socket
import time
import sys

#UDP_DEST_IP = '10.10.10.10'
UDP_DEST_IP = '127.0.0.1'
UDP_DEST_PORT = 7777
#UDP_RCV_IP = '192.168.0.102'
UDP_RCV_IP = '127.0.0.1'
UDP_RCV_PORT = 7778
NR_OF_PACKETS = 10
PACKETS_PER_SEC = 1
BUFFER = 4096


addr_rx = (UDP_RCV_IP, UDP_RCV_PORT)
sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_snd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data = []
outfile = open("udp_results.csv", "a")
inter_departure_time = 1./PACKETS_PER_SEC

time.perf_counter()

try:
    sock_rcv.bind(addr_rx)
    print('bind ok on ', addr_rx)
except Exception:
    print('bind failed on ', addr_rx)

outfile.write('\n' + 'New start at ' + str(time.ctime() + '\n') + '\n')

for i in range(1, NR_OF_PACKETS+1):
    time.sleep(inter_departure_time)
    sock_snd.sendto(str((round(time.perf_counter(), 6), str('%08d' % i))).encode(), (UDP_DEST_IP, UDP_DEST_PORT))
    data_rcv, addr_rcv = sock_rcv.recvfrom(BUFFER)
    time_rcv = round(time.perf_counter(), 6)
    splitdata = data_rcv.decode().split(',')
    time_snd = splitdata[0].strip("('")
    one_way_delay = round(time_rcv - float(time_snd), 6)
    data.append(one_way_delay)
    outfile.write(str(time.ctime() + ' ; ' + str(i) + ' ; ' + str(one_way_delay) + '\n'))
    print(time.ctime() + ' ; ' + str(i) + ' ; ' + str(one_way_delay))

export_data = 'min: ' + str(min(data)) + ' | max: ' + str(max(data)) + ' | middle: ' + str(round((sum(data)/float(i)), 6)) + ' | jitter: ' + str(round(max(data)-min(data), 6))
outfile.write('\n' + export_data)
print(export_data)
outfile.write('\n' + 'Measure finished at ' + str(time.ctime() + '\n'))
print()
