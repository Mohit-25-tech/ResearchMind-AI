from pathlib import Path
import sqlite3

#create database folder if it doesn't exist

DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

#database file

DATABASE_PATH = DATABASE_DIR / "research.db"

def get_connection():
    """
    Returs a sqlite connection"""

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """
    Creates required tables if they don't exist.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            document_id TEXT UNIQUE NOT NULL,

            filename TEXT NOT NULL,

            file_hash TEXT UNIQUE NOT NULL,

            pages INTEGER,

            chunks INTEGER,

            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT NOT NULL,

            question TEXT NOT NULL,

            answer TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

    conn.commit()
    conn.close()