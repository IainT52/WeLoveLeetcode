import re, secrets


def parseHtml(file, data):
    file = open(file, "r").read()
    file = file.split("\n")
    file = replaceTemplate(file, 0, len(file), data)
    return f"HTTP/1.1 200\r\nContent-Type: text/html\r\nContent-Length: {len(file)}\r\nX-Content-Type-Options: nosniff\r\n\r\n{file}".encode()


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
    if len(variable) > 1:
        return data[variable[0]][0][variable[1]]
    return data[variable[0]][0]


def generateXSRFToken():
    token = secrets.token_hex(16)
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