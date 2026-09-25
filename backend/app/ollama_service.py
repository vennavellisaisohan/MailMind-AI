import requests


MODEL_NAME = "mailmind-ai"
OLLAMA_URL = "http://localhost:11434/api/generate"


def analyze_email(
    email_content: str,
) -> str:
    """Analyze an email using the local MailMind AI model."""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": email_content,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["response"]
