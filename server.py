import paths, socketserver, json
from websockets import openSocketConnection
from database import *

class Header:
    def __init__(self, type, value, extra):
        self.type = type
        self.value = value
        self.extra = extra


def parseHeader(header_data, hasRequestLine):
    extra_types = {"Content-Disposition", "Content-Type"}
    headers = {}
    start = 0
    header_data = header_data.decode("utf-8").split("\r\n")
    
    # Parse request line
    if hasRequestLine:
        start = 1
        request_type, path, version = header_data[0].split(" ")
        headers = {"Request-Type": Header("Request-Type", request_type, {}), "Path": Header("Path", path, {}), "Version": Header("Version", version, {}), "Content-Length": Header("Content-Length", 0, {})}

    # Parse headers and build key value mapping
    for i in range(start, len(header_data)):
        cur_header = header_data[i]
        if cur_header == "":
            continue
        header_type, value = cur_header.split(": ")
        values = value.split("; ")
        extras = {}
        for j in range(1, len(values)):
            if header_type in extra_types:
                key, val = values[j].split("=")
                extras[key] = val
        headers[header_type] = Header(header_type, values[0], extras)

    return headers


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(2048)
        print(f"\n-------------- Request recieved from {self.client_address} -----------------\n")
        
        header_data, body = self.data.split("\r\n\r\n".encode('utf-8'), 1)
        headers = parseHeader(header_data, True)

        # Check content length for buffered data
        content_length = int(headers["Content-Length"].value) - len(body)
        while content_length != 0:
            self.data = self.request.recv(2048)
            body += self.data
            content_length -= len(self.data)
        
        if headers["Request-Type"].value == "POST":
            if headers["Path"].value == "/account":
                account_info = json.loads(body.decode())
                username = account_info['username']
                password = account_info['password']
                print(register(username, password))
        elif headers["Request-Type"].value == "PUT":
            pass
        elif headers["Request-Type"].value == "DELETE":
            pass
        else:
            response = paths.handlePath(headers["Path"].value, headers)

        self.request.sendall(response)
        
        if headers["Path"].value == "/websocket":
            openSocketConnection(self)  # handshake is complete before this function call
            
        self.request.close()
        return


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8000
    
    # Server instance
    server = socketserver.ThreadingTCPServer((HOST, PORT), RequestHandler)
    server.serve_forever()