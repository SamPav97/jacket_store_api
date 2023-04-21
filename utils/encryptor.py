import base64
import hashlib

from cryptography.fernet import Fernet
from decouple import config


class CryptoHelper:
    def __init__(self):
        self.key = config("DECRYPT_KEY").encode()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        encrypted_data = self.cipher.encrypt(data.encode())
        return encrypted_data.decode()

    def decrypt(self, encrypted_data: str) -> str:
        decrypted_data = self.cipher.decrypt(encrypted_data.encode())
        return decrypted_data.decode()


def decode_file(path, encoded_file):
    with open(path, "wb") as f:
        f.write(base64.b64decode(encoded_file.encode("utf-8")))


def generate_image_hash(file_path):
    hasher = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            data = file.read(8192)
            if not data:
                break
            hasher.update(data)

    return hasher.hexdigest()
