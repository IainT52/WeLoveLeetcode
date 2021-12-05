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
    "/account": "",
    "/templates/canvas.html": responses.handleFileResponse(getRelativePath("templates/canvas.html"), "200 OK", "text/html"),
}


def handlePath( path, headers):
    if path not in paths:
        return responses.handleTextResponse("The resource requested cannot be found in this server!", "404 Not Found")
    
    if path == "/":
        return responses.parseHtml(getRelativePath("templates\index.html"), {})
    elif path == "/websocket":
        return responses.handleSocketHandshake(path, headers)
    
    return paths[path]



def handleForms(parsed_body):
    token = (parsed_body["xsrf_token"][0].decode()).strip('\r\n')
    if token not in tokens:
        return responses.handleTextResponse("Forbidden", "403 Forbidden")
    
    if "register-username" in parsed_body:
        username = parsed_body["register-username"][0].decode().strip("\r\n")
        password = parsed_body["register-password"][0].decode().strip("\r\n")
        if register(username, password):
            return responses.parseHtml(getRelativePath("templates/index.html"), {"register_success": ["Success! Please Log in"]})
        else:
            return responses.parseHtml(getRelativePath("templates/index.html"), {"register_success": ["Registration failed, please check password requirements!"]})
    
    if "login-username" in parsed_body:
        username = parsed_body["login-username"][0].decode().strip("\r\n")
        password = parsed_body["login-password"][0].decode().strip("\r\n")

        if login(username, password):
            return responses.parseHtml(getRelativePath("templates/canvas.html"), {})
        else:
            return responses.parseHtml(getRelativePath("templates/index.html"), {"login_success": ["Invalid"]})
    
    return responses.handleRedirect("/")
