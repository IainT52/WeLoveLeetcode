import responses, os
from database import *

cur_dir = os.path.dirname(__file__)
def getRelativePath(path):
    return os.path.abspath(os.path.realpath(os.path.join(cur_dir, path)))

paths = {
    "/": "",
    "/websocket": "",
    "/static/css/canvas.css": responses.handleFileResponse(getRelativePath("static/css/canvas.css"), "200 OK", "text/css"),
    "/static/js/canvas.js": responses.handleFileResponse(getRelativePath("static/js/canvas.js"), "200 OK", "text/javascript"),
    "/static/js/reglog.js": responses.handleFileResponse(getRelativePath("static/js/reglog.js"), "200 OK", "text/javascript"),
    "/account": ""
}


def handlePath( path, headers):
    global num_visits
    print("test", path)
    if path not in paths:
        return responses.handleTextResponse("The resource requested cannot be found in this server!", "404 Not Found")


    if path == "/":
        return responses.parseHtml(getRelativePath("templates\index.html"), {})
    elif path == "/websocket":
        return responses.handleSocketHandshake(path, headers)
    
    return paths[path]


def handleForms(parsed_body):
    form = {}
    token = (parsed_body["xsrf_token"][0].decode()).strip('\r\n')
    if token not in tokens:
        return responses.handleTextResponse("Forbidden", "403 Forbidden")

    
    if "register-username" in parsed_body:
        username = parsed_body["register-username"][0].decode().strip("\r\n")
        password = parsed_body["register-password"][0].decode().strip("\r\n")

        if verifyPassword(password):
            password, salt = hashPassword(password)
            register(username, password.decode(), salt.decode())
        else:
            return responses.parseHtml("index.html", {"register_success": ["Invalid Password"], "visits": [str(num_visits)]}, num_visits)
    
    if "login-username" in parsed_body:
        username = parsed_body["login-username"][0].decode().strip("\r\n")
        password = parsed_body["login-password"][0].decode().strip("\r\n")

        if login(username, password):
            return responses.parseHtml("index.html", {"login_success": ["Valid"], "visits": [str(num_visits)]}, num_visits)
        else:
            return responses.parseHtml("index.html", {"login_success": ["Invalid"], "visits": [str(num_visits)]}, num_visits)
    
    database["forms"].append(form)
    return responses.handleRedirect("/")
