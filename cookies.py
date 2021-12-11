import hashlib
import secrets
import database

def cookie_tokenizer(username):
    secret_token = secrets.token_hex(16)
    token = hashlib.md5(secret_token.encode()).hexdigest()
    database.tokenize(token, username)
    return token