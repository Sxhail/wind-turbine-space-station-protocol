# pitch_listener.py — Turbine: Blade Pitch Control (Port 5001)
# Contributor: Suhail Jameel
# Receives PITCH commands from Space Station via relay.
# Sends ACK back through the relay on the same port.
import socket
from protocol import *

RELAY_IP   = '<<YASH_IP>>'   # Replace before running
RELAY_PORT = 5001

current_pitch = 0.0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if hasattr(socket, 'SIO_UDP_CONNRESET'):
    sock.ioctl(socket.SIO_UDP_CONNRESET, False)

sock.bind(('0.0.0.0', 5001))
print('Pitch listener running on port 5001')
print(f'Sending ACKs back to relay at {RELAY_IP}:{RELAY_PORT}')
print('-' * 40)

while True:
    try:
        data, addr = sock.recvfrom(1024)
        msg_type, seq, ack, chk, length, payload = unpack_message(data)
        if msg_type == MSG_CMD and verify_checksum(payload, chk):
            try:
                value = float(payload.split(':')[1])
                current_pitch = value
                print(f'[PITCH CMD] seq={seq} | Setting pitch to {current_pitch} degrees')
            except (IndexError, ValueError):
                print(f'[PITCH CMD] seq={seq} | Payload: {payload}')
            ack_pkt = pack_message(MSG_ACK, seq, seq, 'OK')
            sock.sendto(ack_pkt, (RELAY_IP, RELAY_PORT))
            print(f'[ACK SENT]  seq={seq} -> relay:{RELAY_PORT}')
        else:
            print(f'[NACK]      seq={seq} | Bad checksum or wrong type')
            nack = pack_message(MSG_NACK, seq, seq, 'ERR')
            sock.sendto(nack, (RELAY_IP, RELAY_PORT))
    except ConnectionResetError:
        pass
    except Exception as e:
        print(f'[ERROR] {e}')
