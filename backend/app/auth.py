from google_auth_oauthlib.flow import Flow

from app import config


GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]


def create_google_oauth_flow() -> Flow:
    client_config = {
        "web": {
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                config.GOOGLE_REDIRECT_URI,
            ],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=GOOGLE_SCOPES,
        redirect_uri=config.GOOGLE_REDIRECT_URI,
    )

    return flow


def get_google_authorization_url() -> tuple[str, str, str]:
    flow = create_google_oauth_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    code_verifier = flow.code_verifier

    return authorization_url, state, code_verifier