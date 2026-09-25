from google.auth.transport import requests
from google.oauth2 import id_token

from app.config import GOOGLE_CLIENT_ID


def verify_google_identity(id_token_value: str) -> dict:
    user_info = id_token.verify_oauth2_token(
        id_token_value,
        requests.Request(),
        GOOGLE_CLIENT_ID,
    )

    return {
        "google_id": user_info["sub"],
        "email": user_info["email"],
        "name": user_info.get("name"),
    }
