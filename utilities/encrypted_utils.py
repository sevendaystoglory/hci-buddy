from cryptography.fernet import Fernet, InvalidToken
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# Get the SECRET_KEY from .env
secret_key = os.getenv('SECRET_KEY')

# Convert to bytes
SECRET_KEY = secret_key.encode()

# Generate a valid Fernet key
FERNET_KEY = base64.urlsafe_b64encode(SECRET_KEY)

def encrypt_message(message: str) -> bytes:
    f = Fernet(FERNET_KEY)
    encrypted = f.encrypt(message.encode())
    return encrypted

def decrypt_message(message: str | bytes) -> str:
    if isinstance(message, str):
        return message  # Already a string, no need to decrypt
    f = Fernet(FERNET_KEY)
    try:
        decrypted = f.decrypt(message).decode()
        return decrypted
    except InvalidToken:
        # If decryption fails, assume the message is not encrypted
        try:
            return message.decode()
        except UnicodeDecodeError:
            return f"[UNDECODABLE MESSAGE: {len(message)} bytes]"