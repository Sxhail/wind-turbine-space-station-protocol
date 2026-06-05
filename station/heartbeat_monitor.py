# heartbeat_monitor.py — Space Station: Heartbeat Monitor
# Contributor: Kanishk Daga
# Listens on port 5004 for heartbeat signals from the turbine.
# Warns if no heartbeat arrives within 15 seconds (blackout).
import socket, threading, time
from protocol import *

PORT               = 5004
BUFFER_SIZE        = 4096
CHECK_INTERVAL     = 5
HEARTBEAT_TIMEOUT  = 15

last_heartbeat = None
lock = threading.Lock()

def monitor():
    while True:
        time.sleep(CHECK_INTERVAL)
        with lock:
            if last_heartbeat is None:
                print('[HB MONITOR] No heartbeat received yet')
            elif (time.time() - last_heartbeat) > HEARTBEAT_TIMEOUT:
                print('[WARNING]    No heartbeat - turbine may be unreachable (blackout?)')
            else:
                elapsed = round(time.time() - last_heartbeat, 1)
                print(f'[HB MONITOR] Turbine reachable - last heartbeat {elapsed}s ago')

threading.Thread(target=monitor, daemon=True).start()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))
print(f'Heartbeat monitor listening on UDP port {PORT}')
print('-' * 40)

while True:
    try:
        data, _ = sock.recvfrom(BUFFER_SIZE)
        msg_type, seq, _, chk, _, payload = unpack_message(data)
        if msg_type != MSG_HB:
            continue
        if not verify_checksum(payload, chk):
            continue
        with lock:
            last_heartbeat = time.time()
        print(f'[HEARTBEAT]  seq={seq} | {payload}')
    except (OSError, ValueError) as e:
        print(f'[ERROR] {e}')
