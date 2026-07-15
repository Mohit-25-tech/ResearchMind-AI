from pathlib import Path
import hashlib

from app.services.database import get_connection


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


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


def document_exists(file_hash: str) -> bool:
    """
    Check whether a document with the given hash
    already exists in SQLite.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM documents
        WHERE file_hash = ?
        """,
        (file_hash,)
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
            chunks
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            document_id,
            filename,
            file_hash,
            pages,
            chunks,
        ),
    )

    conn.commit()
    conn.close()


def get_all_documents():
    """
    Returns every uploaded document.
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
        ORDER BY uploaded_at DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]