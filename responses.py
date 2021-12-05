import hashlib, base64, re, secrets
from database import tokens


def handleFileResponse(file, status, content_type):
    file = open(file, "r").read()
    return f"HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {len(file)}\r\nX-Content-Type-Options: nosniff\r\n\r\n{file}".encode()


def handleTextResponse(text, status):
    return f"HTTP/1.1 {status}\r\nContent-Type: text/plain\r\nConent-Length: {len(text)}\r\nX-Content-Type-Options: nosniff\r\n\r\n{text}".encode()


def handleRedirect(path):
    return f"HTTP/1.1 301 Moved Permanently\r\nLocation: {path}".encode()


def handleSocketHandshake(path, headers):
    socket_key = (headers["Sec-WebSocket-Key"].value + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
    hash_object = hashlib.sha1()
    hash_object.update(socket_key)
    accept_response = base64.b64encode(bytes.fromhex(hash_object.hexdigest())).decode()
    
    return f"HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept: {accept_response}\r\nX-Content-Type-Options: nosniff\r\n\r\n".encode()


def parseHtml(file, data):
    file = open(file, "r").read()
    file = file.split("\n")
    file = replaceTemplate(file, 0, len(file), data)
    return f"HTTP/1.1 200\r\nContent-Type: text/html\r\nContent-Length: {len(file)}\r\nX-Content-Type-Options: nosniff\r\n\r\n{file}".encode()



# Templating

def replaceTemplate(file, idx, endIdx, data):
    if idx == endIdx:
        return ""
    templates = re.findall('{{(.*?)}}', file[idx])

    # Plain HTML
    if len(templates) == 0:
        return file[idx] + replaceTemplate(file, idx+1, endIdx, data)

    # For loop
    elif templates[0][:4] == "for ":
        endforIdx = findStatementEnd(file, idx+1, "for ", "endfor", 4)
        _, variable, _, data_structure = templates[0].split(" ")

        inner_data = ""
        if data_structure in data:
            for i in range(len(data[data_structure])):
                data[variable] = [data[data_structure][i]]
                inner_data += replaceTemplate(file, idx+1, endforIdx, data)
        
        return inner_data + replaceTemplate(file, endforIdx+1, endIdx, data)

    # If statement
    elif templates[0][:3] == "if ":
        endifIdx = findStatementEnd(file, idx+1, "if ", "endif", 3)
        _, variable, operator, value = templates[0].split(" ")
        
        variable = parseVariableTemplates(variable, data)
        inner_data = ""
        if operator == "==":
            value = value.strip('"')
            if variable == value:
                inner_data = replaceTemplate(file, idx+1, endifIdx, data)

        return inner_data + replaceTemplate(file, endifIdx+1, endIdx, data)

    # Variable
    else:
        return re.sub('{{(.*?)}}', lambda var: parseVariableTemplates(var.group(1), data), file[idx]) + replaceTemplate(file, idx+1, endIdx, data)
    

def parseVariableTemplates(variable, data):
    if variable == "xsrf_token":
        return generateXSRFToken()
    variable = variable.split('.')
    if variable[0] not in data:
        return ''
    if len(variable) > 1:
        return data[variable[0]][0][variable[1]]
    return data[variable[0]][0]


def generateXSRFToken():
    token = secrets.token_hex(16)
    tokens.add(token)
    return token


def findStatementEnd(file, idx, syntaxBegin, syntaxEnd, length):
    nestedCount = 0
    while idx < len(file):
        templates = re.findall('{{(.*?)}}', file[idx])
        if len(templates) == 0:
            idx += 1
            continue
        if templates[0][:length] == syntaxBegin:
            nestedCount += 1
        elif templates[0] == syntaxEnd and nestedCount == 0:
            return idx
        elif templates[0] == syntaxEnd:
            nestedCount -= 1
        idx += 1
    return idx