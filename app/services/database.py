from pathlib import Path
import sqlite3

DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "research.db"

def get_connection():
    """
    Returns a SQLite connection.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """
    Creates/migrates required tables and indices.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Check if documents has user_id
    cursor.execute("PRAGMA table_info(documents)")
    doc_columns = [col[1] for col in cursor.fetchall()]
    
    # Create documents if it doesn't exist
    if not doc_columns:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                pages INTEGER,
                chunks INTEGER,
                user_id INTEGER REFERENCES users(id),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    else:
        if "user_id" not in doc_columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER REFERENCES users(id)")

    # 3. Migrate old conversations table structure if needed
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        cursor.execute("PRAGMA table_info(conversations)")
        conv_columns = [col[1] for col in cursor.fetchall()]
        if "session_id" in conv_columns:
            # Rename it so we don't lose the old conversation memory
            cursor.execute("ALTER TABLE conversations RENAME TO conversations_old")

    # 4. Create new conversations and messages tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 5. Create Performance Indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);")

    # 6. Run conversation migration
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations_old'")
    old_table_exists = cursor.fetchone()
    if old_table_exists:
        # Load unique session ids
        cursor.execute("SELECT DISTINCT session_id FROM conversations_old")
        sessions = [row[0] for row in cursor.fetchall()]
        
        for sess in sessions:
            # Create a placeholder new conversation
            cursor.execute(
                "INSERT INTO conversations (user_id, title) VALUES (NULL, ?)",
                (f"Imported Session: {sess[:8]}",)
            )
            conv_id = cursor.lastrowid
            
            # Fetch message sequences
            cursor.execute(
                "SELECT question, answer, created_at FROM conversations_old WHERE session_id = ? ORDER BY id ASC",
                (sess,)
            )
            for msg_row in cursor.fetchall():
                question, answer, created_at = msg_row
                cursor.execute(
                    "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, 'user', ?, ?)",
                    (conv_id, question, created_at)
                )
                cursor.execute(
                    "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, 'assistant', ?, ?)",
                    (conv_id, answer, created_at)
                )
        
        # Drop the old table now that it's migrated
        cursor.execute("DROP TABLE conversations_old")

    conn.commit()
    conn.close()