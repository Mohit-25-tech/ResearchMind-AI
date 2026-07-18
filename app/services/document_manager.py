from pathlib import Path
import hashlib
from app.services.database import get_connection

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def delete_uploaded_pdf(user_id: int, document_id: str):
    """
    Delete uploaded PDF from disk.
    """
    pdf_path = UPLOAD_DIR / str(user_id) / f"{document_id}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()

def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    """
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()

def document_exists(user_id: int, file_hash: str) -> bool:
    """
    Check whether a document with the given hash
    already exists in SQLite for this user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM documents
        WHERE file_hash = ? AND user_id = ?
        """,
        (file_hash, user_id)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def insert_document(
    document_id: str,
    filename: str,
    file_hash: str,
    pages: int,
    chunks: int,
    user_id: int,
):
    """
    Insert a new document into SQLite.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO documents
        (
            document_id,
            filename,
            file_hash,
            pages,
            chunks,
            user_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            document_id,
            filename,
            file_hash,
            pages,
            chunks,
            user_id,
        ),
    )
    conn.commit()
    conn.close()

def get_all_documents(user_id: int):
    """
    Returns every uploaded document belonging to the user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            document_id,
            filename,
            pages,
            chunks,
            uploaded_at
        FROM documents
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_document(document_id: str):
    """
    Returns one document by document_id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            document_id,
            filename,
            file_hash,
            pages,
            chunks,
            user_id,
            uploaded_at
        FROM documents
        WHERE document_id = ?
        """,
        (document_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)

def delete_document_record(document_id: str):
    """
    Deletes a document from SQLite.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM documents
        WHERE document_id = ?
        """,
        (document_id,)
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted > 0
