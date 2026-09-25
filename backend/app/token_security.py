from cryptography.fernet import Fernet

from app.config import TOKEN_ENCRYPTION_KEY


if not TOKEN_ENCRYPTION_KEY:
    raise RuntimeError(
        "TOKEN_ENCRYPTION_KEY is missing from the environment."
    )


fernet = Fernet(TOKEN_ENCRYPTION_KEY.encode())


def encrypt_token(token: str) -> str:
    """Encrypt an OAuth token."""
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted OAuth token."""
    return fernet.decrypt(encrypted_token.encode()).decode()