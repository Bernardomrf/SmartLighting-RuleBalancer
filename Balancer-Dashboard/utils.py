
from os import urandom
from base64 import b32encode

def generate_id():
    random_bytes = urandom(10)
    token = b32encode(random_bytes).decode('utf-8')
    return token[:-1]