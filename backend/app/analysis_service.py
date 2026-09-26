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

Return ONLY valid JSON using exactly this structure:

{{
  "category": "Academic",
  "priority": "High",
  "summary": "Brief summary of the email.",
  "tasks": [],
  "deadline": null
}}

Rules:
- category must be one of: Academic, Internship, Job, Placement, Examination, Event, Personal, Finance, Promotional, Other.
- priority must be High, Medium, or Low.
- summary must be concise and factual.
- tasks must be a JSON array of actionable tasks.
- deadline must contain an explicitly mentioned deadline or null.
- Do not invent information.
- Do not return Markdown.
- Do not add any text outside the JSON object.
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