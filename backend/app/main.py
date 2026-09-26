
import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app import auth
from app.analysis_service import analyze_user_emails
from app.schemas import EmailAnalysisRequest, EmailAnalysisResponse
from app.database import get_db
from app.oauth_service import save_google_credentials


app = FastAPI(
    title="MailMind AI API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Temporary OAuth state storage for local development.
# Replace with secure session/database storage before production.
pending_oauth_states: dict[str, str] = {}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MailMind AI API",
    }


@app.get("/auth/google/login")
def google_login():
    try:
        authorization_url, state, code_verifier = (
            auth.get_google_authorization_url()
        )

        # Store the PKCE code verifier against the OAuth state.
        pending_oauth_states[state] = code_verifier

        return {
            "authorization_url": authorization_url,
            "state": state,
        }

    except Exception as error:
        logging.exception("Google login URL creation failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to create Google authorization URL.",
        ) from error


@app.get("/auth/google/callback")
def google_callback(
    request: Request,
    db=Depends(get_db),
):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    # Handle an authorization error returned by Google.
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Google authorization failed: {error}",
        )

    # Validate required callback parameters.
    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code or state.",
        )

    # Validate the OAuth state.
    if state not in pending_oauth_states:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state.",
        )

    # Retrieve and remove the code verifier.
    code_verifier = pending_oauth_states.pop(state)

    try:
        flow = auth.create_google_oauth_flow()

        # Restore the PKCE verifier created during login.
        flow.code_verifier = code_verifier

        # Exchange the authorization code for Google credentials.
        flow.fetch_token(
            authorization_response=str(request.url),
        )

        credentials = flow.credentials

        # Save the user and encrypted OAuth credentials.
        user = save_google_credentials(
            db=db,
            credentials=credentials,
        )

        return {
            "status": "success",
            "message": "Google account connected successfully.",
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "scopes": credentials.scopes,
            "has_refresh_token": bool(credentials.refresh_token),
        }

    except ValueError as error:
        logging.exception(
            "Google identity verification or credential validation failed"
        )

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logging.exception("Google OAuth callback failed")

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to complete Google OAuth callback. "
                "Check backend logs."
            ),
        ) from error


@app.post(
    "/emails/analyze",
    response_model=EmailAnalysisResponse,
)
def analyze_emails(
    request_data: EmailAnalysisRequest,
    db=Depends(get_db),
):
    try:
        results = analyze_user_emails(
            db=db,
            user_id=request_data.user_id,
            max_results=request_data.max_results,
            query=request_data.query,
        )

        return {
            "results": results,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logging.exception("Email analysis failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to analyze emails.",
        ) from error
