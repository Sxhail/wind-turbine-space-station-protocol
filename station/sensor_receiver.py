# sensor_receiver.py — Space Station: Sensor Data Receiver
# Contributor: Kanishk Daga
# Listens on port 5003 for sensor readings from the turbine.
# Checks sequence numbers to detect dropped packets.
import socket
from protocol import *

PORT        = 5003
BUFFER_SIZE = 4096

def main():
    expected_seq = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))
    print(f'Sensor receiver listening on UDP port {PORT}')
    print('-' * 40)

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            if len(data) < HEADER_SIZE:
                print('Packet too small - discarding')
                continue
            msg_type, seq, _, chk, length, payload = unpack_message(data)
            if msg_type != MSG_DATA:
                continue
            if not verify_checksum(payload, chk):
                print(f'[BAD CHECKSUM] seq={seq} - discarding')
                continue
            if seq > expected_seq:
                print(f'[MISSING PKT]  Expected seq={expected_seq}, got seq={seq}')
                expected_seq = seq + 1
            elif seq == expected_seq:
                expected_seq += 1
            print(f'[SENSOR DATA]  seq={seq} | {payload}')
        except (OSError, ValueError) as e:
            print(f'[ERROR] {e}')

if __name__ == '__main__':
    main()
