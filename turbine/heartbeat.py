# heartbeat.py — Turbine: Heartbeat Beacon (Port 5004)
# Contributor: Suhail Jameel
# Sends an ALIVE signal every 5 seconds so the Space Station
# knows the turbine is still reachable.
import socket, time
from protocol import *

RELAY_IP   = '<<YASH_IP>>'   # Replace before running
RELAY_PORT = 5004
seq = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Heartbeat beacon running — sending every 5 seconds')
print(f'Target: relay at {RELAY_IP}:{RELAY_PORT}')
print('-' * 40)

while True:
    pkt = pack_message(MSG_HB, seq, 0, 'ALIVE')
    sock.sendto(pkt, (RELAY_IP, RELAY_PORT))
    print(f'[HEARTBEAT] seq={seq} | ALIVE')
    seq += 1
    time.sleep(5)
