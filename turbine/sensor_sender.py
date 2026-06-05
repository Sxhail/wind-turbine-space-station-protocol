# sensor_sender.py — Turbine: Sensor Data Stream (Port 5003)
# Contributor: Suhail Jameel
# Sends live sensor readings every 2 seconds via UDP relay.
import socket, time, random
from protocol import *

RELAY_IP   = '<<YASH_IP>>'   # Replace before running
RELAY_PORT = 5003
seq = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Sensor sender running — sending data every 2 seconds')
print(f'Target: relay at {RELAY_IP}:{RELAY_PORT}')
print('-' * 40)

while True:
    wind = round(random.uniform(20, 60), 1)
    temp = round(random.uniform(5, 20), 1)
    rpm  = random.randint(200, 400)
    payload = f'WIND:{wind},TEMP:{temp},RPM:{rpm}'
    pkt = pack_message(MSG_DATA, seq, 0, payload)
    sock.sendto(pkt, (RELAY_IP, RELAY_PORT))
    print(f'[DATA SENT] seq={seq} | {payload}')
    seq += 1
    time.sleep(2)
