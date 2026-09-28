import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.services.database import get_connection

conversations_router = APIRouter(prefix="/conversations", tags=["conversations"])

def _parse_doc_ids(val: Optional[str]) -> List[str]:
    if not val:
        return []
    try:
        data = json.loads(val)
        return data if isinstance(data, list) else [str(data)]
    except Exception:
        return [x.strip() for x in val.split(",") if x.strip()]

@conversations_router.get("")
def list_conversations(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, selected_document_ids, created_at, updated_at 
        FROM conversations 
        WHERE user_id = ? 
        ORDER BY updated_at DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        d = dict(row)
        d["selected_document_ids"] = _parse_doc_ids(d.get("selected_document_ids"))
        result.append(d)
        
    return {"conversations": result}

@conversations_router.delete("")
def clear_all_conversations(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "All conversations cleared successfully"}

@conversations_router.get("/{conversation_id}")
def get_conversation_messages(conversation_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute(
        "SELECT id, selected_document_ids FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, user_id)
    )
    conv = cursor.fetchone()
    if not conv:
        conn.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    cursor.execute(
        """
        SELECT role, content, created_at 
        FROM messages 
        WHERE conversation_id = ? 
        ORDER BY id ASC
        """,
        (conversation_id,)
    )
    rows = cursor.fetchall()
    selected_ids = _parse_doc_ids(conv["selected_document_ids"] if "selected_document_ids" in conv.keys() else None)
    conn.close()
    return {
        "messages": [dict(row) for row in rows],
        "selected_document_ids": selected_ids,
    }

@conversations_router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute(
        "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, user_id)
    )
    conv = cursor.fetchone()
    if not conv:
        conn.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()
    return {"message": "Conversation deleted successfully"}

class RenameRequest(BaseModel):
    title: str

@conversations_router.patch("/{conversation_id}")
def rename_conversation(
    conversation_id: int, 
    request: RenameRequest, 
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute(
        "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, user_id)
    )
    conv = cursor.fetchone()
    if not conv:
        conn.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    cursor.execute(
        "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (request.title, conversation_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Conversation renamed successfully"}

class UpdateDocumentsRequest(BaseModel):
    document_ids: List[str]

@conversations_router.patch("/{conversation_id}/documents")
def update_conversation_documents(
    conversation_id: int,
    request: UpdateDocumentsRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, user_id)
    )
    conv = cursor.fetchone()
    if not conv:
        conn.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    docs_json = json.dumps(request.document_ids)
    cursor.execute(
        "UPDATE conversations SET selected_document_ids = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (docs_json, conversation_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Scoped documents updated", "document_ids": request.document_ids}
