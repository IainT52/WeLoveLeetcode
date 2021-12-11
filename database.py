import mysql.connector, random, os
from auth import encrypt


tokens = set()
default_images = ["static/images/deer.jpg", "static/images/eagle.jpg", "static/images/whale.jpg"]

username = os.getenv("312_USERNAME", "root")
password = os.getenv("312_PASSWORD", "1F900b8b3d52;")

database = mysql.connector.connect(
    host="mysql",
    user=username,
    password=password,
    database="312db"
)

mycursor = database.cursor(prepared=True)
mycursor.execute("CREATE TABLE IF NOT EXISTS registration (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, image TEXT, UNIQUE (username))")
mycursor.execute("CREATE TABLE IF NOT EXISTS cookie_jar (id INT AUTO_INCREMENT PRIMARY KEY, token VARCHAR(255) NOT NULL, username VARCHAR(255) NOT NULL, UNIQUE (username))")
mycursor.execute("CREATE TABLE IF NOT EXISTS gallery (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, image MEDIUMBLOB)")

def get_profile_photo(username):
    command = "SELECT image FROM registration WHERE username = (?)"
    mycursor.execute(command, (username,))
    fetch = mycursor.fetchall()
    return fetch[0][0]

def upload_profile_photo(username, image):
    # command = "SELECT * FROM gallery WHERE username = (?)"
    # mycursor.execute(command, (username,))
    # fetch = mycursor.fetchall()
    # if fetch == []:
    #     command = "INSERT INTO gallery (username, image) VALUES (?, ?)"
    #     mycursor.execute(command, (username, image))
    # else:
    #     command = "UPDATE gallery SET image = (?) WHERE username = (?)"
    #     mycursor.execute(command, (image, username))

    command = "UPDATE registration SET image = (?) WHERE username = (?)"
    mycursor.execute(command, ("custom-" + username, username))
    return

def get_custom_profile_picture(username):
    command = "SELECT image FROM gallery WHERE username = (?)"
    mycursor.execute(command, (username,))
    fetch = mycursor.fetchall()
    if fetch == []:
        return ""
    return fetch[0][0]

#Register function returns a boolean - if true, username registered, if false, username not registered.
def register(username, password):
    hashed = encrypt.encrypt(password)
    if hashed:
        command = "SELECT * FROM registration WHERE username = (?)"
        mycursor.execute(command, (username,))
        fetch = mycursor.fetchall()
        if fetch == []:
            command = "INSERT INTO registration (username, password, image) VALUES (?, ?, ?)"
            photo = default_images[random.randint(0,2)]
            value = (username, hashed, photo)
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
    return

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

def hasValidAuthToken(headers):
    if 'Cookie' not in headers:
        return False, ""
    
    if 'auth' not in headers['Cookie'].extra:
        return False, ""
    
    user = get_user(headers['Cookie'].extra['auth'])
    if user == "":
        return False, ""
    return True, user