import json
from database import hasValidAuthToken

client_to_name = {}  # tcp connection objects connected to the site are stored here
name_to_client = {}


# returns a string with html characters encoded
def htmlSafe(string):
    string = string.replace('&', '&amp;').replace(
        '<', '&lt;').replace('>', '&gt;')
    return string


# removes client object from clients list
def closeWebSocketConnection(self):
    username = client_to_name[self]
    del client_to_name[self]
    del name_to_client[username]
    return


# decodes websocket frame (input is bytearray) with len < 126
def decodeFrame(self, frame):
    fin_opcode = bin(frame[0])[2:]  # 0b01000010 (splice from 2 to skip '0b')
    fin, rsv, opcode = fin_opcode[0], fin_opcode[1:4], fin_opcode[4:8]

    if opcode == '1000':
        closeWebSocketConnection(self)
        return bytearray("CONNECTION CLOSED".encode())

    # we can assume mask bit is 1, so subtract it off
    payload_len = frame[1] - 128
    if payload_len == 126:  # 126 bytes <= len < 65536 bytes
        # next 16 bits (2 bytes) represents payload len
        payload_len = int.from_bytes(frame[2:4], 'big')
        return decodeLargeFrame(frame, payload_len)

    mask = frame[2:6]
    encrypted_payload = frame[6:(6 + payload_len)]
    payload = bytearray([encrypted_payload[i] ^ mask[i % 4]
                        for i in range(payload_len)])
    return payload


# decoded websocket frame with 126 <= len < 65636
def decodeLargeFrame(frame, payload_len):
    mask = frame[4:8]
    encrypted_payload = frame[8:(8 + payload_len)]
    payload = bytearray([encrypted_payload[i] ^ mask[i % 4]
                        for i in range(payload_len)])
    return payload


# sends message to all clients, clients are added to this list on connection
def broadcast(sender, message):
    for client in client_to_name.keys():
        try:
            if client == sender:
                continue
            sendFrame(client, message)
        except Exception as e:
            # if client disconnects, we still try sending msg (causing an error)
            pass
    return


# sends websocket frame containing payload of len < 126
def sendFrame(self, payload):
    if len(payload) > 125:
        frame_to_send = self.sendLargeFrame(payload)
        self.request.sendall(frame_to_send)
        return

    frame = [129]  # fin: 1, opcode: 0x1 (10000001)
    frame += [len(payload)]
    frame_to_send = bytearray(frame) + payload
    self.request.sendall(frame_to_send)
    return


# sends websocket frame containing payload of 126 <= len < 65536
def sendLargeFrame(self, payload):
    frame = [129]  # fin: 1, opcode: 0x1 (10000001)
    frame += [126]  # mask bit: 0, len: 126 (01111110)
    # right shift to fill bits 8-15 (ext. payload is 16 bits)
    frame += [(len(payload) >> 8) & 255]
    frame += [len(payload) & 255]  # now fill first 8 bits (255 -> 11111111)
    frame_to_send = bytearray(frame) + payload
    return frame_to_send


def openSocketConnection(self, headers):
    validAuthToken, username = hasValidAuthToken(headers)
    
    client_to_name[self] = username
    name_to_client[username] = self
    # SEND CURRENT CANVAS TO NEWLY CONNECTED CLIENT

    while True:
        frame = bytearray(self.request.recv(1024))
        payload = decodeFrame(self, frame)
        if payload.decode() == "CONNECTION CLOSED":
            break
        decoded_payload = json.loads(payload.decode())  # 'utf-8'
        if 'recipient' and 'message' in decoded_payload:
            recipient_name = decoded_payload['recipient']
            if recipient_name in name_to_client:
                recipient = name_to_client[recipient_name]
            else:  # send error message to sender, recipient doesn't exist
                recipient = self
                # set recipient name to self, actual recipient DNE
                decoded_payload['recipient'] = username
            
            decoded_payload['sender'] = username
            safe_payload = {htmlSafe(k): htmlSafe(v)
                            for k, v in decoded_payload.items()}
            sendFrame(recipient, bytearray(
                json.dumps(safe_payload).encode()))
            continue  # not a coordinate, dont execute rest of while loop

        message = bytearray(json.dumps(decoded_payload).encode())
        broadcast(self, message)

    return
