from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.models import OAuthToken
from app.token_security import decrypt_token, encrypt_token


def get_gmail_service(
    db: Session,
    user_id: int,
):
    """Create an authenticated Gmail API service for a user."""

    token_record = (
        db.query(OAuthToken)
        .filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "google",
        )
        .first()
    )

    if token_record is None:
        raise ValueError("Google account is not connected.")

    access_token = decrypt_token(token_record.access_token)

    refresh_token = None

    if token_record.refresh_token:
        refresh_token = decrypt_token(token_record.refresh_token)

    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
        ],
    )

    # Refresh the access token if it has expired.
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        token_record.access_token = encrypt_token(
            credentials.token
        )

        token_record.token_expiry = credentials.expiry

        db.commit()

    if not credentials.valid:
        raise ValueError(
            "Google credentials are invalid or expired."
        )

    gmail_service = build(
        "gmail",
        "v1",
        credentials=credentials,
    )

    return gmail_service