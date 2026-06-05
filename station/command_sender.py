# command_sender.py — Space Station: Manual Command Control
# Contributor: Kanishk Daga
#
# Type commands live during the demo.
# Format: PITCH:30 or YAW:45
# Type 'quit' to exit.
#
# Flow:
#   Station sends CMD to relay port (turbine_port + 100)
#   Relay forwards CMD to Turbine on turbine_port
#   Turbine sends ACK back through relay
#   Station receives ACK and confirms delivery
import socket, time
from protocol import *

RELAY_IP  = '<<YASH_IP>>'   # Replace with actual IP
TIMEOUT   = 2.0
MAX_RETRY = 5

PORT_MAP = {
    'PITCH': 5001,
    'YAW':   5002,
}

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
                        print(f'  [NACK]    seq={seq} | Turbine rejected — retrying')
                        break

                    if msg_type == MSG_ACK and ack_num == seq:
                        print(f'  [ACK]     seq={seq} | Turbine confirmed')
                        return True

            except socket.timeout:
                if attempt < MAX_RETRY:
                    print(f'  [TIMEOUT] seq={seq} | No response — retrying...')
                else:
                    print(f'  [FAILED]  seq={seq} | No ACK after {MAX_RETRY} attempts')

            except OSError as e:
                if getattr(e, 'winerror', None) == 10054:
                    time.sleep(0.2)
                    continue
                print(f'  [ERROR]   {e}')
                return False
    finally:
        sock.close()

    return False

def main():
    print('=' * 50)
    print('Space Station — Manual Command Control')
    print(f'Relay IP : {RELAY_IP}')
    print('Commands : PITCH:<degrees>  or  YAW:<degrees>')
    print('Example  : PITCH:30   or   YAW:45')
    print("Type 'quit' to exit.")
    print('=' * 50)

    seq = 1
    while True:
        try:
            raw = input('\nEnter command: ').strip().upper()
        except KeyboardInterrupt:
            print('\nExiting.')
            break

        if raw == 'QUIT':
            print('Exiting.')
            break

        if ':' not in raw:
            print('  [INVALID] Format must be PITCH:30 or YAW:45')
            continue

        cmd_type = raw.split(':')[0]
        if cmd_type not in PORT_MAP:
            print(f'  [INVALID] Unknown command type. Use PITCH or YAW')
            continue

        try:
            value = float(raw.split(':')[1])
        except ValueError:
            print('  [INVALID] Value must be a number e.g. PITCH:30')
            continue

        port = PORT_MAP[cmd_type]
        print(f'\n[SEQ {seq}] Sending {raw} to turbine...')
        success = send_command(seq, raw, port)

        if success:
            print(f'[SEQ {seq}] Command delivered successfully')
        else:
            print(f'[SEQ {seq}] Command FAILED')

        seq += 1

if __name__ == '__main__':
    main()
