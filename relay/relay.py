# relay.py — LEO Satellite Relay
# Contributor: Yash Chhillar
#
# Sits between Turbine and Space Station.
# Applies realistic channel conditions:
#   - Propagation delay (DELAY_MS)
#   - Random packet loss (LOSS_RATE)
#   - Periodic blackout windows (BLACKOUT_EVERY / BLACKOUT_DURATION)
#
# Port routing:
#   Port 5001-5004 → receives from Turbine, forwards to Station
#   Port 5101-5104 → receives from Station, forwards to Turbine
import socket, threading, time, random
from config import *
from protocol import unpack_message

in_blackout = False

# Tracks how many commands have been forwarded to the turbine.
# Every 20th command has its payload corrupted so the checksum
# fails at the turbine and a NACK is returned to the station.
command_counter = 0
command_counter_lock = threading.Lock()

HEADER_SIZE = 9   # must match protocol.py


def blackout_scheduler():
    global in_blackout
    while True:
        time.sleep(BLACKOUT_EVERY)
        in_blackout = True
        print(f'\n** BLACKOUT STARTED — link down for {BLACKOUT_DURATION}s **')
        time.sleep(BLACKOUT_DURATION)
        in_blackout = False
        print('* BLACKOUT ENDED — link restored *\n')


def forward(data, dest_ip, dest_port, label, is_command=False):
    global in_blackout, command_counter

    if in_blackout:
        print(f'[BLACKOUT]  Dropped: {label}')
        return

    if random.random() < LOSS_RATE:
        print(f'[DROPPED]   {label}')
        return

    # On command packets only, corrupt every 20th one
    if is_command:
        with command_counter_lock:
            command_counter += 1
            count = command_counter

        if count % 20 == 0:
            # Flip the first byte of the payload to break the checksum
            corrupted = bytearray(data)
            if len(corrupted) > HEADER_SIZE:
                corrupted[HEADER_SIZE] ^= 0xFF
                data = bytes(corrupted)
                print(f'[CORRUPTED] Payload mangled on command #{count} — turbine will send NACK: {label}')

    time.sleep(DELAY_MS / 1000.0)
    fwd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    fwd_sock.sendto(data, (dest_ip, dest_port))
    print(f'[FORWARDED] {label} to {dest_ip}:{dest_port}')


def listen_and_relay(bind_port, dest_ip, dest_port, direction, is_command=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', bind_port))
    print(f'Listening on :{bind_port}  ({direction})')
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            _, seq, _, _, _, payload = unpack_message(data)
            label = f'port={bind_port} seq={seq} | {payload[:25]}'
            threading.Thread(
                target=forward,
                args=(data, dest_ip, dest_port, label, is_command),
                daemon=True
            ).start()
        except Exception as e:
            print(f'[ERROR on port {bind_port}] {e}')


# Start blackout scheduler
threading.Thread(target=blackout_scheduler, daemon=True).start()

# Start relay threads for all 4 ports in both directions
for port in [5001, 5002, 5003, 5004]:
    # Turbine → Station (no corruption applied)
    threading.Thread(
        target=listen_and_relay,
        args=(port, STATION_IP, port, f'Turbine→Station (port {port})', False),
        daemon=True
    ).start()
    # Station → Turbine (corruption applied only on CMD ports 5101 and 5102)
    is_cmd_port = port in [5001, 5002]
    threading.Thread(
        target=listen_and_relay,
        args=(port + 100, TURBINE_IP, port, f'Station→Turbine (port {port})', is_cmd_port),
        daemon=True
    ).start()

print('Relay running. Press Ctrl+C to stop.\n')
while True:
    time.sleep(1)
