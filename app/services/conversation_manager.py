from app.services.database import get_connection

def save_conversation(
    conversation_id: int,
    question: str,
    answer: str,
):
    """
    Save one conversation turn to the messages table and update conversation time.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, 'user', ?)",
        (conversation_id, question)
    )
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, 'assistant', ?)",
        (conversation_id, answer)
    )
    cursor.execute(
        "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (conversation_id,)
    )
    
    conn.commit()
    conn.close()

def get_conversation_history(
    conversation_id: int,
    limit: int = 5,
):
    """
    Get the most recent conversation history as dictionary pairs.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (conversation_id, limit * 2)
    )
    rows = cursor.fetchall()
    conn.close()
    
    rows.reverse()
    
    history = []
    i = 0
    while i < len(rows):
        if i + 1 < len(rows) and rows[i]["role"] == "user" and rows[i+1]["role"] == "assistant":
            history.append({
                "question": rows[i]["content"],
                "answer": rows[i+1]["content"]
            })
            i += 2
        else:
            i += 1
            
    return history

def delete_conversation(
    conversation_id: int,
):
    """
    Delete an entire conversation.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()