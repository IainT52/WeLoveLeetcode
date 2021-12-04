import responses, os

cur_dir = os.path.dirname(__file__)
def getRelativePath(path):
    return os.path.abspath(os.path.realpath(os.path.join(cur_dir, path)))

paths = {
    "/": "",
    "/websocket": "",
    "/static/css/canvas.css": responses.handleFileResponse(getRelativePath("static/css/canvas.css"), "200 OK", "text/css"),
    "/static/js/canvas.js": responses.handleFileResponse(getRelativePath("static/js/canvas.js"), "200 OK", "text/javascript")
}


def handlePath(path, headers):
    global num_visits
    print(path)
    if path not in paths:
        return responses.handleTextResponse("The resource requested cannot be found in this server!", "404 Not Found")

    if path == "/":
        return responses.parseHtml(getRelativePath("templates\index.html"), {})
    elif path == "/websocket":
        return responses.handleSocketHandshake(path, headers)
    
    return paths[path]