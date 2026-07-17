from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.auth.dependencies import get_current_user
from app.chains.rag_chain import stream_rag
from app.services.database import get_connection

stream_router = APIRouter()

@stream_router.post("/stream-chat")
def stream_chat(
    question: str,
    session_id: str | None = Query(None),
    document_id: str | None = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Handle streaming user chat queries. Scopes session_id to conversation_id.
    """
    user_id = current_user["id"]
    conversation_id = None
    
    if session_id and session_id.strip():
        try:
            conversation_id = int(session_id)
        except ValueError:
            conversation_id = None

    conn = get_connection()
    cursor = conn.cursor()

    if not conversation_id:
        cursor.execute(
            "INSERT INTO conversations (user_id, title) VALUES (?, ?)",
            (user_id, "New Chat")
        )
        conversation_id = cursor.lastrowid
        conn.commit()
    else:
        cursor.execute(
            "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id)
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    conn.close()

    return StreamingResponse(
        stream_rag(
            question=question,
            conversation_id=conversation_id,
            user_id=user_id,
            document_id=document_id,
        ),
        media_type="text/plain",
    )