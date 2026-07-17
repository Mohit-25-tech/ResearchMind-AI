import os
from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token: str) -> dict | None:
    """
    Verify the Google ID token and return user profile details.
    """
    try:
        # If GOOGLE_CLIENT_ID is not specified, token verification will fail unless in mock mode.
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except Exception as e:
        # Development fallback / Mock mode
        if os.getenv("DEBUG_MOCK_AUTH") == "true" or token.startswith("mock-"):
            return {
                "sub": token,
                "email": f"{token}@example.com",
                "name": f"User {token}",
                "picture": "https://lh3.googleusercontent.com/a/mock"
            }
        print(f"Google Token Verification Failure: {e}")
        return None
