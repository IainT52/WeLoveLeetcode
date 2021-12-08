import mysql.connector
from auth import encrypt

tokens = set()

database = mysql.connector.connect(
    # host="mysql",
    user="root",
    password="cse312homework",
    database="canvas"
)
# iain db 312db pass 1F900b8b3d52;
# nick pass cse312homework
mycursor = database.cursor(prepared=True)

mycursor.execute("CREATE TABLE IF NOT EXISTS registration (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, UNIQUE (username))")
mycursor.execute("CREATE TABLE IF NOT EXISTS cookie_jar (id INT AUTO_INCREMENT PRIMARY KEY, token VARCHAR(255) NOT NULL, username VARCHAR(255) NOT NULL, UNIQUE (username))")
mycursor.execute("CREATE TABLE IF NOT EXISTS gallery (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, image BLOB)")

def paint(username, image):
    command = "SELECT * FROM registration WHERE username = (?)"
    mycursor.execute(command, (username,))
    fetch = mycursor.fetchall()
    if fetch == []:
        return False
    command = "INSERT INTO gallery (username, image) VALUES (?,?)"
    value = (username, image, )
    mycursor.execute(command, value)
    database.commit()
    return True

#Register function returns a boolean - if true, username registered, if false, username not registered.
def register(username, password):
    hashed = encrypt.encrypt(password)
    if hashed:
        command = "SELECT * FROM registration WHERE username = (?)"
        mycursor.execute(command, (username,))
        fetch = mycursor.fetchall()
        if fetch == []:
            command = "INSERT INTO registration (username, password) VALUES (?, ?)"
            value = (username, hashed, )
            mycursor.execute(command, value)
            database.commit()
            return True
    return False
    
def login(username, password):
    command = "SELECT * FROM registration WHERE username = (?)"
    mycursor.execute(command, (username,))
    fetch = mycursor.fetchall()
    if fetch == []:
        return False
    hashed = fetch[0][2]
    return encrypt.verify(password, hashed)

def tokenize(token, username):
    command = "SELECT * FROM cookie_jar WHERE username = (?)"
    mycursor.execute(command, (username,))
    fetch = mycursor.fetchall()
    if fetch == []:
        command = "INSERT INTO cookie_jar (token, username) VALUES (?,?)"
        value = (token, username, )
        mycursor.execute(command, value)
        database.commit()
        print("Token created!")
    else:
        command = "UPDATE cookie_jar SET token = (?) WHERE username = (?)"
        values = (token, username, )
        mycursor.execute(command, values)
        database.commit()
        print("Token updated!")

def get_token(username):
    command = "SELECT * FROM cookie_jar WHERE username = (?)"
    mycursor.execute(command, (username,))
    fetch = mycursor.fetchall()
    if fetch == []:
        return ''
    return fetch[0][1]

def get_user(token):
    command = "SELECT * FROM cookie_jar WHERE token = (?)"
    mycursor.execute(command, (token,))
    fetch = mycursor.fetchall()
    if fetch == []:
        return ''
    return fetch[0][2]