from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.auth.google import verify_google_token
from app.auth.jwt import create_access_token
from app.services.database import get_connection

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    credential: str

@router.post("/google")
def google_auth(request: LoginRequest):
    """
    Verify Google ID credential, create/update the SQLite user profile, and issue a signed JWT.
    """
    idinfo = verify_google_token(request.credential)
    if not idinfo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google credentials or token expired."
        )

    google_id = idinfo.get("sub")
    email = idinfo.get("email")
    name = idinfo.get("name", "Google User")
    picture = idinfo.get("picture")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID token missing mandatory profile parameters."
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE google_id = ?", (google_id,))
    row = cursor.fetchone()

    now = datetime.utcnow().isoformat()
    if row:
        user_id = row[0]
        cursor.execute(
            """
            UPDATE users
            SET name = ?, email = ?, picture = ?, last_login = ?
            WHERE id = ?
            """,
            (name, email, picture, now, user_id)
        )
    else:
        cursor.execute(
            """
            INSERT INTO users (google_id, name, email, picture, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (google_id, name, email, picture, now, now)
        )
        user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    # Issue access token
    token_data = {"user_id": user_id, "email": email}
    access_token = create_access_token(token_data)

    return {
        "token": access_token,
        "access_token": access_token,
        "token_type": "bearer",
        "is_new_user": not bool(row),
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
            "picture": picture
        }
    }
