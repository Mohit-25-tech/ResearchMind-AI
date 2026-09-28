from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.auth.dependencies import get_current_user
from app.chains.rag_chain import stream_rag
from app.agent.graph import stream_agent
from app.config.settings import settings
from app.services.database import get_connection

stream_router = APIRouter()

import json
from typing import List, Optional

@stream_router.post("/stream-chat")
def stream_chat(
    question: str,
    session_id: str | None = Query(None),
    document_id: str | None = Query(None),
    document_ids: list[str] | None = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Handle streaming user chat queries. Scopes session_id to conversation_id.
    Uses LangGraph agent streaming when USE_AGENT is enabled.
    Supports multi-document scoping via document_ids.
    """
    user_id = current_user["id"]
    conversation_id = None
    
    if session_id and session_id.strip():
        try:
            conversation_id = int(session_id)
        except ValueError:
            conversation_id = None

    # Parse requested document IDs from query params
    requested_doc_ids: Optional[List[str]] = None
    if document_ids is not None:
        requested_doc_ids = []
        for item in document_ids:
            if "," in item:
                requested_doc_ids.extend([x.strip() for x in item.split(",") if x.strip()])
            elif item.strip():
                requested_doc_ids.append(item.strip())
    elif document_id is not None:
        requested_doc_ids = [x.strip() for x in document_id.split(",") if x.strip()]

    conn = get_connection()
    cursor = conn.cursor()

    if not conversation_id:
        initial_docs_json = json.dumps(requested_doc_ids) if requested_doc_ids is not None else None
        cursor.execute(
            "INSERT INTO conversations (user_id, title, selected_document_ids) VALUES (?, ?, ?)",
            (user_id, "New Chat", initial_docs_json)
        )
        conversation_id = cursor.lastrowid
        conn.commit()
    else:
        cursor.execute(
            "SELECT id, selected_document_ids FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id)
        )
        conv_row = cursor.fetchone()
        if not conv_row:
            conn.close()
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

        if requested_doc_ids is not None:
            # Update persisted document scope for this conversation
            cursor.execute(
                "UPDATE conversations SET selected_document_ids = ? WHERE id = ?",
                (json.dumps(requested_doc_ids), conversation_id)
            )
            conn.commit()
        elif conv_row["selected_document_ids"]:
            try:
                requested_doc_ids = json.loads(conv_row["selected_document_ids"])
            except Exception:
                requested_doc_ids = None
            
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

    if settings.use_agent:
        generator = stream_agent(
            question=question,
            conversation_id=conversation_id,
            user_id=user_id,
            document_ids=requested_doc_ids,
        )
    else:
        generator = stream_rag(
            question=question,
            conversation_id=conversation_id,
            user_id=user_id,
            document_ids=requested_doc_ids,
        )

    return StreamingResponse(
        generator,
        media_type="text/plain",
    )