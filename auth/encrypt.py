import bcrypt

specialCharacters = ['!', '"', '#', '$', '%', '&',
                     '(', ')', '*', '+', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '{', '|', '}', '~']

requirements = [lambda password: any(key.isupper() for key in password),
                lambda password: any(key.islower() for key in password),
                lambda password: any(key.isdigit() for key in password),
                lambda password: any(
                    key in password for key in specialCharacters),
                lambda password: len(password) >= 8]


def escape(string):
    new_string = string.replace('&', '&amp;')
    new_string = new_string.replace('<', "&lt;")
    new_string = new_string.replace('>', "&gt;")
    return new_string


def isStrong(password):
    if all(requirement(password) for requirement in requirements):
        return True
    else:
        return False


def encrypt(password):
    if isStrong(password):
        passwd = escape(password).encode()
        hashed = bcrypt.hashpw(passwd, bcrypt.gensalt(12))
        return hashed
    else:
        print("Password did not meet at least one of the five requirements.")


def verify(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)
