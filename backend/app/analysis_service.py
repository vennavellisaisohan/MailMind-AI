from sqlalchemy.orm import Session

from app.email_service import get_user_emails
from app.ollama_service import analyze_email


def build_email_prompt(email: dict) -> str:
    """Build an analysis prompt from email metadata."""

    return f"""
Analyze the following email.

Subject: {email.get("subject", "")}
Sender: {email.get("sender", "")}
Date: {email.get("date", "")}
Snippet: {email.get("snippet", "")}

Provide:
1. A concise summary.
2. Actionable tasks, if any.
3. Explicit deadlines, if mentioned.

Do not invent information that is not present in the email.
"""


def analyze_user_emails(
    db: Session,
    user_id: int,
    max_results: int = 5,
    query: str | None = None,
) -> list[dict]:
    """Retrieve and analyze emails for a connected user."""

    emails = get_user_emails(
        db=db,
        user_id=user_id,
        max_results=max_results,
        query=query,
    )

    results = []

    for email in emails:
        prompt = build_email_prompt(email)
        analysis = analyze_email(prompt)

        results.append(
            {
                "email_id": email.get("id"),
                "subject": email.get("subject", ""),
                "sender": email.get("sender", ""),
                "date": email.get("date", ""),
                "analysis": analysis,
            }
        )

    return results
