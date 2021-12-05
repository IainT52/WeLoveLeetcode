import mysql.connector
from auth import encrypt

database = mysql.connector.connect(
    # host="mysql",
    user="root",
    password="cse312homework",
    database="canvas"
)

mycursor = database.cursor(prepared=True)

mycursor.execute("CREATE TABLE IF NOT EXISTS registration (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, UNIQUE (username))")

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
            print("Registration complete!")
            return True
        else: 
            print("Username already exists")
            return False
    else: return False
    
def login(username, password):
    command = "SELECT * FROM registration WHERE username = (?)"
    mycursor.execute(command, (username,))
    fetch = mycursor.fetchall()
    if fetch == []:
        return False
    hashed = fetch[0][2]
    return encrypt.verify(password, hashed)