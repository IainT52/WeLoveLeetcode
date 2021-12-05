import responses, os, json
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


def handlePath(client, path, headers, body):
    global num_visits
    print("test", path)
    if path not in paths:
        return responses.handleTextResponse("The resource requested cannot be found in this server!", "404 Not Found")


    if headers["Request-Type"].value == "POST":
        if headers["Path"].value == "/account":
            account_info = json.loads(body.decode())
            username = account_info['username']
            password = account_info['password']
            if account_info['create']:
                success = register(username, password)
                print(success)
                if success:
                    return responses.handleTextResponse("Success", "200 OK")
                else: 
                    return responses.handleTextResponse("Failure", "200 OK")

            else:
                success = login(username, password)
                print(success)
                if success:
                    # client.request.sendall(responses.handleTextResponse("Success", "200 OK"))
                    return responses.handleRedirect("templates\canvas.html")
                else:
                    return responses.handleTextResponse("Failure", "200 OK")
                

        
    elif headers["Request-Type"].value == "PUT":
        pass

    elif headers["Request-Type"].value == "DELETE":
        pass
    

    if path == "/":
        return responses.parseHtml(getRelativePath("templates\index.html"), {})
    elif path == "/websocket":
        return responses.handleSocketHandshake(path, headers)
    
    return paths[path]
