# yaw_listener.py — Turbine: Blade Yaw Control (Port 5002)
# Contributor: Suhail Jameel
# Receives YAW commands from Space Station via relay.
# Sends ACK back through the relay on the same port.
import socket
from protocol import *

RELAY_IP   = '<<YASH_IP>>'   # Replace before running
RELAY_PORT = 5002

current_yaw = 0.0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if hasattr(socket, 'SIO_UDP_CONNRESET'):
    sock.ioctl(socket.SIO_UDP_CONNRESET, False)

sock.bind(('0.0.0.0', 5002))
print('Yaw listener running on port 5002')
print(f'Sending ACKs back to relay at {RELAY_IP}:{RELAY_PORT}')
print('-' * 40)

while True:
    try:
        data, addr = sock.recvfrom(1024)
        msg_type, seq, ack, chk, length, payload = unpack_message(data)
        if msg_type == MSG_CMD and verify_checksum(payload, chk):
            try:
                value = float(payload.split(':')[1])
                current_yaw = value
                print(f'[YAW CMD]   seq={seq} | Setting yaw to {current_yaw} degrees')
            except (IndexError, ValueError):
                print(f'[YAW CMD]   seq={seq} | Payload: {payload}')
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
