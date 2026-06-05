# protocol.py — Shared message format for all 3 laptops
# Group 3: Suhail Jameel, Yash Chhillar, Kanishk Daga
# CSU33D03 Computer Networks 2025/26
import struct

HEADER_FORMAT = '!B H H H H'   # Type, SeqNum, AckNum, Checksum, Length
HEADER_SIZE   = 9

MSG_CMD  = 0x01   # Command  (Station to Turbine)
MSG_ACK  = 0x02   # Acknowledge
MSG_DATA = 0x03   # Sensor Data (Turbine to Station)
MSG_HB   = 0x04   # Heartbeat
MSG_NACK = 0x05   # Bad checksum, please resend

def checksum(payload: str) -> int:
    return sum(payload.encode()) & 0xFFFF

def pack_message(msg_type, seq, ack, payload=''):
    payload_bytes = payload.encode()
    chk = checksum(payload)
    length = len(payload_bytes)
    header = struct.pack(HEADER_FORMAT, msg_type, seq, ack, chk, length)
    return header + payload_bytes

def unpack_message(data):
    header = data[:HEADER_SIZE]
    msg_type, seq, ack, chk, length = struct.unpack(HEADER_FORMAT, header)
    payload = data[HEADER_SIZE:HEADER_SIZE + length].decode('utf-8', errors='replace')
    return msg_type, seq, ack, chk, length, payload

def verify_checksum(payload, received_chk):
    return checksum(payload) == received_chk
