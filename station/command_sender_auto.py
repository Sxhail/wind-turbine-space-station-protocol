# command_sender_auto.py — Space Station: Auto Loop (Testing)
# Contributor: Kanishk Daga
#
# For testing only. Loops through preset commands automatically.
# Use command_sender.py for the actual demo.
import socket, time
from protocol import *

RELAY_IP  = '<<YASH_IP>>'   # Replace with actual IP
TIMEOUT   = 2.0
MAX_RETRY = 5

COMMANDS = [
    ('PITCH:30', 5001),
    ('YAW:45',   5002),
    ('PITCH:10', 5001),
    ('YAW:20',   5002),
    ('PITCH:45', 5001),
    ('YAW:90',   5002),
    ('PITCH:0',  5001),
    ('YAW:0',    5002),
]

def send_command(seq, command, turbine_port):
    relay_port  = turbine_port + 100
    listen_port = turbine_port
    packet = pack_message(MSG_CMD, seq, 0, command)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    if hasattr(socket, 'SIO_UDP_CONNRESET'):
        sock.ioctl(socket.SIO_UDP_CONNRESET, False)

    sock.bind(('0.0.0.0', listen_port))

    try:
        for attempt in range(1, MAX_RETRY + 1):
            try:
                sock.sendto(packet, (RELAY_IP, relay_port))
                print(f'  [SENT]    seq={seq} | {command} | attempt {attempt}')

                while True:
                    data, _ = sock.recvfrom(4096)
                    msg_type, _, ack_num, chk, _, payload = unpack_message(data)
                    if not verify_checksum(payload, chk):
                        continue
                    if msg_type == MSG_NACK:
                        break
                    if msg_type == MSG_ACK and ack_num == seq:
                        print(f'  [ACK]     seq={seq} | Turbine confirmed')
                        return True

            except socket.timeout:
                if attempt < MAX_RETRY:
                    print(f'  [TIMEOUT] seq={seq} | Retrying...')
                else:
                    print(f'  [FAILED]  seq={seq} | No ACK after {MAX_RETRY} attempts')

            except OSError as e:
                if getattr(e, 'winerror', None) == 10054:
                    time.sleep(0.2)
                    continue
                return False
    finally:
        sock.close()

    return False

def main():
    print('Auto Command Sender (Testing Mode)')
    print(f'Relay: {RELAY_IP}  |  Press Ctrl+C to stop')
    print('=' * 50)
    seq = 1
    while True:
        for command, port in COMMANDS:
            print(f'\n[SEQ {seq}] {command}')
            send_command(seq, command, port)
            seq += 1
            time.sleep(2)

if __name__ == '__main__':
    main()
