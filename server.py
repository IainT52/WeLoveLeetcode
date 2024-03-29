import paths, socketserver
from websockets import openSocketConnection  # this is NOT a python library, this is OUR CODE

class Header:
    def __init__(self, type, value, extra):
        self.type = type
        self.value = value
        self.extra = extra


def parseBody(body_data, headers):
    content_type = headers["Content-Type"]
    parsed_body = {}
    isImage = False

    if content_type.value == "multipart/form-data":
        boundary = ("--" + content_type.extra["boundary"] + "\r\n").encode('utf-8')
        body = body_data.split(boundary)
        body[-1] = body[-1][:-1*len(("--" + content_type.extra["boundary"] + "--\r\n").encode('utf-8'))] 
        body.pop(0)
        
        for content in body:
            header_data, data = content.split("\r\n\r\n".encode('utf-8'))
            new_headers = parseHeader(header_data, False)
            isImage = isImage or ("Content-Type" in new_headers and new_headers["Content-Type"].value[:5] == "image")
            name = (new_headers["Content-Disposition"].extra["name"]).strip('"')
            parsed_body[name] = (data, new_headers)
    
    return paths.handleForms(parsed_body, headers, isImage)


def parseHeader(header_data, hasRequestLine):
    extra_types = {"Content-Disposition", "Content-Type", "Cookie"}
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
        for j in range(len(values)):
            if header_type in extra_types and '=' in values[j]:
                key, val = values[j].split("=")
                extras[key] = val
        headers[header_type] = Header(header_type, values[0], extras)
    
    return headers


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(2048)
        print(f"\n-------------- Request recieved from {self.client_address} --------------\n")
        
        header_data, body = self.data.split("\r\n\r\n".encode('utf-8'), 1)
        headers = parseHeader(header_data, True)

        # Check content length for buffered data
        content_length = int(headers["Content-Length"].value) - len(body)
        while content_length != 0:
            self.data = self.request.recv(2048)
            body += self.data
            content_length -= len(self.data)


        if headers["Request-Type"].value == "POST":
            response = parseBody(body, headers)
        elif headers["Request-Type"].value == "PUT":
            pass
        elif headers["Request-Type"].value == "DELETE":
            pass
        else:
            response = paths.handlePath(headers["Path"].value, headers)
        
        self.request.sendall(response)
        
        if headers["Path"].value == "/websocket":
            openSocketConnection(self, headers)  # handshake is complete before this function call
            
        self.request.close()
        return


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8000
    
    # Server instance
    server = socketserver.ThreadingTCPServer((HOST, PORT), RequestHandler)
    server.serve_forever()