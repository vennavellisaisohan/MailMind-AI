import os

from cryptography.fernet import Fernet

from dotenv import load_dotenv


load_dotenv(override=True)


TOKEN_ENCRYPTION_KEY = os.getenv("TOKEN_ENCRYPTION_KEY")


def get_cipher():
    if not TOKEN_ENCRYPTION_KEY:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY is not configured."
        )

    return Fernet(TOKEN_ENCRYPTION_KEY.encode())


def encrypt_token(token: str) -> str:
    cipher = get_cipher()

    encrypted_token = cipher.encrypt(
        token.encode()
    )

    return encrypted_token.decode()


def decrypt_token(encrypted_token: str) -> str:
    cipher = get_cipher()

    decrypted_token = cipher.decrypt(
        encrypted_token.encode()
    )

    return decrypted_token.decode()