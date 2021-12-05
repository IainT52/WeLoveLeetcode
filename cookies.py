import hashlib
import secrets
from auth import encrypt

def cookie_tokenizer(username):
    secret_token = secrets.token_hex(16)
    token = hashlib.md5(secret_token.encode().hexdigest())
    encrypt.tokenize(token, username)
    return token