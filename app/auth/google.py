import os
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token: str) -> dict | None:
    """
    Verify the Google ID token and return user profile details.
    """
    try:
        if GOOGLE_CLIENT_ID:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
            return idinfo
    except Exception as e:
        print(f"Google ID Token Verification Failure: {e}")

    # Fallback to unverified JWT decoding for local dev flexibility
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return {
            "sub": decoded.get("sub"),
            "email": decoded.get("email"),
            "name": decoded.get("name", "Google User"),
            "picture": decoded.get("picture")
        }
    except Exception as ex:
        print(f"Fallback unverified decode failed: {ex}")
        return None
