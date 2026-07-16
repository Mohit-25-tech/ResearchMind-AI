from app.services.database import get_connection


def save_conversation(
    session_id: str,
    question: str,
    answer: str,
):
    """
    Save one conversation turn.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations
        (
            session_id,
            question,
            answer
        )

        VALUES (?, ?, ?)
        """,
        (
            session_id,
            question,
            answer,
        ),
    )

    conn.commit()

    conn.close()

def get_conversation_history(
    session_id: str,
    limit: int = 5,
):
    """
    Get the most recent conversation history.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            question,
            answer

        FROM conversations

        WHERE session_id = ?

        ORDER BY id DESC

        LIMIT ?
        """,
        (
            session_id,
            limit,
        ),
    )

    rows = cursor.fetchall()

    conn.close()

    rows.reverse()

    return rows

def delete_conversation(
    session_id: str,
):
    """
    Delete an entire chat session.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM conversations
        WHERE session_id = ?
        """,
        (session_id,),
    )

    conn.commit()

    conn.close()