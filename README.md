# Wind Turbine to Space Station — Network Protocol

A custom UDP-based network protocol that simulates a real-time control and monitoring link between an offshore wind turbine and a space station, routed through a LEO (Low-Earth Orbit) satellite relay. Built and demonstrated across three physical laptops on a local network.

---

## Architecture

```
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│   Wind Turbine  │◄──────►│  LEO Sat Relay  │◄──────►│  Space Station  │
│  (Suhail)       │  UDP   │  (Yash)         │  UDP   │  (Kanishk)      │
│                 │        │                 │        │                 │
│ pitch_listener  │        │ relay.py        │        │ command_sender  │
│ yaw_listener    │        │ config.py       │        │ sensor_receiver │
│ sensor_sender   │        │                 │        │ heartbeat_mon.  │
│ heartbeat.py    │        │                 │        │                 │
└─────────────────┘        └─────────────────┘        └─────────────────┘
```

**Data flows:**

| Direction | Content | Port |
|-----------|---------|------|
| Turbine → Station | Pitch/Yaw ACKs | 5001, 5002 |
| Station → Turbine | PITCH / YAW commands | 5101, 5102 |
| Turbine → Station | Sensor data (WIND, TEMP, RPM) | 5003 |
| Turbine → Station | Heartbeat (ALIVE) | 5004 |

---

## Protocol

All messages share a 9-byte binary header, packed big-endian:

```
 0       1       3       5       7       9
 ┌───────┬───────┬───────┬───────┬───────┐
 │ Type  │SeqNum │AckNum │Chksum │Length │  + UTF-8 payload
 │ 1 B   │ 2 B   │ 2 B   │ 2 B   │ 2 B   │
 └───────┴───────┴───────┴───────┴───────┘
```

| Type | Value | Direction |
|------|-------|-----------|
| `MSG_CMD`  | `0x01` | Station → Turbine |
| `MSG_ACK`  | `0x02` | Turbine → Station |
| `MSG_DATA` | `0x03` | Turbine → Station |
| `MSG_HB`   | `0x04` | Turbine → Station |
| `MSG_NACK` | `0x05` | Turbine → Station |

**Checksum:** 16-bit sum of UTF-8 payload bytes, masked to `0xFFFF`.

**Reliability:** Stop-and-wait ARQ with up to 5 retries and a 2-second timeout per command.

---

## Channel Simulation (Relay)

The relay deliberately degrades the link to mimic real satellite conditions:

| Parameter | Value |
|-----------|-------|
| Propagation delay | 200 ms |
| Packet loss rate | 10% |
| Blackout duration | 15 s |
| Blackout interval | every 90 s |
| Payload corruption | every 20th command (triggers NACK) |

---

## Repository Structure

```
├── turbine/
│   ├── protocol.py          # Shared message format
│   ├── pitch_listener.py    # Receives PITCH commands, sends ACK (port 5001)
│   ├── yaw_listener.py      # Receives YAW commands, sends ACK (port 5002)
│   ├── sensor_sender.py     # Streams WIND/TEMP/RPM every 2 s (port 5003)
│   ├── heartbeat.py         # Sends ALIVE beacon every 5 s (port 5004)
│   └── launch.bat           # Launches all 4 turbine processes
│
├── relay/
│   ├── protocol.py          # Shared message format
│   ├── relay.py             # LEO satellite relay with channel simulation
│   ├── config.py            # Delay, loss, blackout parameters + IPs
│   └── launch.bat           # Launches relay
│
└── station/
    ├── protocol.py          # Shared message format
    ├── command_sender.py    # Manual command control (PITCH/YAW)
    ├── command_sender_auto.py  # Auto test loop
    ├── sensor_receiver.py   # Receives and validates sensor data
    ├── heartbeat_monitor.py # Monitors turbine reachability
    └── launch.bat           # Launches station processes
```

---

## Setup & Running

### Prerequisites

- Python 3.8+ on each laptop
- All three machines on the same local network

### Configuration

Before running, replace the placeholder IPs in the source files:

**`relay/config.py`**
```python
TURBINE_IP = '<Suhail machine IP>'
STATION_IP = '<Kanishk machine IP>'
```

**`turbine/*.py`** and **`station/*.py`** — replace `<<YASH_IP>>` with the relay machine's IP.

### Launch Order

Start in this order to avoid missed packets:

1. **Relay** (Yash's machine)
   ```
   cd relay
   launch.bat        # or: python relay.py
   ```

2. **Turbine** (Suhail's machine)
   ```
   cd turbine
   launch.bat        # opens 4 terminal windows
   ```

3. **Station** (Kanishk's machine) — open each in its own terminal:
   ```
   cd station
   python sensor_receiver.py
   python heartbeat_monitor.py
   python command_sender.py     # for live demo commands
   ```

### Sending Commands

In `command_sender.py`, type commands at the prompt:

```
Enter command: PITCH:30
Enter command: YAW:45
Enter command: quit
```

---

## Key Features

- **Custom binary protocol** — compact 9-byte header with sequence numbers, ACK/NACK, and checksum
- **Reliable delivery** — stop-and-wait ARQ with retry on timeout or NACK
- **Missing packet detection** — station tracks sequence numbers and reports gaps
- **Heartbeat monitoring** — station raises alert if no heartbeat for 15 seconds
- **Realistic satellite channel** — configurable delay, loss, blackouts, and corruption injected by the relay
- **Concurrent processes** — turbine runs 4 independent threads/processes in parallel

---

## License

MIT — see [LICENSE](LICENSE).
