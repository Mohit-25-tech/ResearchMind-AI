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
    # Generate title if this is the first turn
    cursor.execute(
        """
        SELECT title, (SELECT COUNT(*) FROM messages WHERE conversation_id = ?) as msg_count 
        FROM conversations WHERE id = ?
        """,
        (conversation_id, conversation_id)
    )
    conv_row = cursor.fetchone()
    if conv_row and (conv_row["title"] == "New Chat" or conv_row["msg_count"] == 0):
        from app.services.title_generator import generate_title_from_query
        title = generate_title_from_query(question)
        cursor.execute("UPDATE conversations SET title = ? WHERE id = ?", (title, conversation_id))
        conn.commit()

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