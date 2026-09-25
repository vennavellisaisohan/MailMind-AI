
import re
from sqlalchemy.orm import Session

from app.gmail_service import get_gmail_service

def clean_email_text(text: str) -> str:
    """Remove invisible Unicode formatting characters from email text."""

    if not text:
        return ""

    # Remove common invisible Unicode characters.
    text = text.replace("\u200c", "")
    text = text.replace("\ufeff", "")
    text = text.replace("\u200b", "")
    text = text.replace("\u200d", "")

    # Remove other control characters while preserving
    # normal whitespace such as spaces and newlines.
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def get_header(headers: list[dict], name: str) -> str:
    """Extract a specific header value from Gmail metadata."""

    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]

    return ""


def get_user_emails(
    db: Session,
    user_id: int,
    max_results: int = 10,
    query: str | None = None,
) -> list[dict]:
    """Retrieve recent emails for a connected user.

    Args:
        db: Database session.
        user_id: ID of the connected user.
        max_results: Maximum number of emails to retrieve.
        query: Optional Gmail search query.

    Returns:
        A list of email metadata dictionaries.
    """

    service = get_gmail_service(
        db=db,
        user_id=user_id,
    )

    # Prepare Gmail message list parameters.
    list_request = {
        "userId": "me",
        "maxResults": max_results,
    }

    # Add Gmail search query when provided.
    if query:
        list_request["q"] = query

    response = (
        service.users()
        .messages()
        .list(**list_request)
        .execute()
    )

    messages = response.get("messages", [])

    emails = []

    for message in messages:
        message_id = message["id"]

        email_data = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=[
                    "From",
                    "To",
                    "Subject",
                    "Date",
                ],
            )
            .execute()
        )

        payload = email_data.get("payload", {})
        headers = payload.get("headers", [])

        email = {
            "id": email_data.get("id"),
            "thread_id": email_data.get("threadId"),
            "sender": get_header(headers, "From"),
            "recipient": get_header(headers, "To"),
            "subject": clean_email_text(
                get_header(headers, "Subject")
            ),
            "date": get_header(headers, "Date"),
            "snippet": clean_email_text(
                email_data.get("snippet", "")
            ),
        }

        emails.append(email)

    return emails