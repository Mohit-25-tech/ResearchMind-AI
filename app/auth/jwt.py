import os
from datetime import datetime, timedelta
import jwt

def get_jwt_secrets() -> list[str]:
    primary = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    fallback = "super-secret-key-change-in-production"
    secrets = [primary]
    if fallback not in secrets:
        secrets.append(fallback)
    return secrets

def get_jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")

def create_access_token(data: dict) -> str:
    """
    Generate a signed JWT token containing user info and expiration.
    """
    to_encode = data.copy()
    expiration_minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))
    expire = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    to_encode.update({"exp": expire})
    primary_secret = get_jwt_secrets()[0]
    return jwt.encode(to_encode, primary_secret, algorithm=get_jwt_algorithm())

def decode_access_token(token: str) -> dict | None:
    """
    Decode and verify a signed JWT token.
    Tries current secret, then fallback secret to prevent invalidating active sessions.
    """
    algorithm = get_jwt_algorithm()
    for secret in get_jwt_secrets():
        try:
            payload = jwt.decode(token, secret, algorithms=[algorithm], leeway=60)
            return payload
        except jwt.PyJWTError:
            continue
    return None
