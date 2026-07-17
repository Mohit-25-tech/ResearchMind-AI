from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth.dependencies import get_current_user
from app.chains.rag_chain import ask_rag
from app.services.database import get_connection

chat_router = APIRouter()

@chat_router.post("/chat")
def chat(
    question: str,
    session_id: str | None = Query(None),
    document_id: str | None = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Handle user chat queries. Scopes session_id to conversation_id.
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

    response = ask_rag(
        question=question,
        conversation_id=conversation_id,
        user_id=user_id,
        document_id=document_id,
    )

    # Automatically generate title if it was New Chat or first query turn
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT title, (SELECT COUNT(*) FROM messages WHERE conversation_id = ?) as msg_count 
        FROM conversations WHERE id = ?
        """,
        (conversation_id, conversation_id)
    )
    conv_row = cursor.fetchone()
    
    if conv_row and (conv_row["title"] == "New Chat" or conv_row["msg_count"] <= 2):
        words = question.split()
        title = " ".join(words[:4])
        if len(title) > 30:
            title = title[:27] + "..."
        cursor.execute("UPDATE conversations SET title = ? WHERE id = ?", (title, conversation_id))
        conn.commit()
    
    conn.close()

    return {
        "session_id": str(conversation_id),
        **response,
    }