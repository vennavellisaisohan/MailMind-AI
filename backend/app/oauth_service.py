from datetime import datetime

from sqlalchemy.orm import Session

from app.google_identity import verify_google_identity
from app.models import OAuthToken, User
from app.token_security import encrypt_token


def save_google_credentials(
    db: Session,
    credentials,
) -> User:
    """Create or update a user and save encrypted Google credentials."""

    if not credentials.id_token:
        raise ValueError("Google ID token is missing.")

    identity = verify_google_identity(credentials.id_token)

    user = (
        db.query(User)
        .filter(User.google_id == identity["google_id"])
        .first()
    )

    if user is None:
        user = User(
            google_id=identity["google_id"],
            email=identity["email"],
            name=identity.get("name"),
        )
        db.add(user)
        db.flush()
    else:
        user.email = identity["email"]
        user.name = identity.get("name")

    encrypted_access_token = encrypt_token(credentials.token)

    encrypted_refresh_token = None

    if credentials.refresh_token:
        encrypted_refresh_token = encrypt_token(
            credentials.refresh_token
        )

    existing_token = (
        db.query(OAuthToken)
        .filter(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "google",
        )
        .first()
    )

    if existing_token:
        existing_token.access_token = encrypted_access_token

        if encrypted_refresh_token:
            existing_token.refresh_token = encrypted_refresh_token

        existing_token.token_expiry = credentials.expiry

    else:
        token_record = OAuthToken(
            user_id=user.id,
            provider="google",
            access_token=encrypted_access_token,
            refresh_token=encrypted_refresh_token,
            token_expiry=credentials.expiry,
        )
        db.add(token_record)

    db.commit()
    db.refresh(user)

    return user