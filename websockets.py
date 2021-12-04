import json, hashlib  # hashlib (SHA-1) needed for websockets
from base64 import b64encode  # base64 for websockets
clients = []  # tcp connection objects connected to the site are stored here



# decodes websocket frame (input is bytearray) with len < 126
def decodeFrame(frame):
    fin_opcode = bin(frame[0])[2:]  # 0b01000010 (splice from 2 to skip '0b')
    fin, rsv, opcode = fin_opcode[0], fin_opcode[1:4], fin_opcode[4:8]
    payload_len = frame[1] - 128  # we can assume mask bit is 1, so subtract it off
    if payload_len == 126:  # 126 bytes <= len < 65536 bytes
        payload_len = int.from_bytes(frame[2:4], 'big')  # next 16 bits (2 bytes) represents payload len
        return decodeLargeFrame(frame, payload_len)
    mask = frame[2:6]
    encrypted_payload = frame[6:(6 + payload_len)]
    payload = bytearray([encrypted_payload[i] ^ mask[i % 4] for i in range(payload_len)])
    return payload


# decoded websocket frame with 126 <= len < 65636
def decodeLargeFrame(frame, payload_len):
    mask = frame[4:8]
    encrypted_payload = frame[8:(8 + payload_len)]
    payload = bytearray([encrypted_payload[i] ^ mask[i % 4] for i in range(payload_len)])
    return payload


# sends message to all clients, clients are added to this list on connection
def broadcast(message):
    for client in clients:
        try:
            client.sendFrame(message)
        except Exception as e:
            pass  # if client disconnects, we still try sending msg (causing an error)
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
    print("len: ", len(payload))
    frame = [129]  # fin: 1, opcode: 0x1 (10000001)
    frame += [126]  # mask bit: 0, len: 126 (01111110)
    frame += [(len(payload) >> 8) & 255]  # right shift to fill bits 8-15 (ext. payload is 16 bits)
    frame += [len(payload) & 255]  # now fill first 8 bits (255 -> 11111111)
    frame_to_send = bytearray(frame) + payload
    return frame_to_send


def openSocketConnection(self, key):
    clients.append(self)
    # send drawing here? 

    while True:
        frame = bytearray(self.request.recv(1024).strip())
        payload = decodeFrame(frame)
        decoded_payload = json.loads(payload.decode())  # 'utf-8'
        message = bytearray(json.dumps(decoded_payload).encode())
        broadcast(message)

# if request_line[1] == '/websocket':
#     # Perform WebSocket Handshake...
#     key = headers.get('Sec-WebSocket-Key', None)
#     ws_response = webSocketHandshake(key)
#     self.request.send(ws_response.encode())
#     clients.append(self)
#     self.loadChatHistory()  # New connection... send chat history

#     while True:
#         frame = bytearray(self.request.recv(1024).strip())
#         payload = decodeFrame(frame)
#         decoded_payload = json.loads(payload.decode())  # 'utf-8'
#         html_safe_dict = {htmlSafe(k): htmlSafe(v) for k, v in decoded_payload.items()}
#         safe_json = json.dumps(html_safe_dict)
#         message = bytearray(json.dumps(html_safe_dict).encode())
#         if safe_json not in session_messages:
#             saveMessage(safe_json)  # save message to database
#             session_messages.add(safe_json)  # add to the set
#         broadcast(message)  # send message frame to all open websockets