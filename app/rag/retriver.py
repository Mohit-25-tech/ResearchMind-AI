from app.rag.vector_store import get_vector_store
from app.services.database import get_connection

def retrieve_chunks(
    query: str,
    user_id: int,
    k: int = 5,
    document_id: str | None = None,
):
    """
    Retrieve relevant chunks for the user.
    Strictly filters results to match the user_id and valid documents in SQLite.
    """
    # Fetch valid document IDs for the user from SQLite
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT document_id FROM documents WHERE user_id = ?", (user_id,))
    valid_doc_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not valid_doc_ids:
        return []

    vector_store = get_vector_store()

    if document_id is not None:
        if document_id not in valid_doc_ids:
            return []
        filters = {
            "$and": [
                {"user_id": user_id},
                {"document_id": document_id}
            ]
        }
    else:
        filters = {
            "$and": [
                {"user_id": user_id},
                {"document_id": {"$in": valid_doc_ids}}
            ]
        }

    search_kwargs = {
        "k": k,
        "fetch_k": 20,
        "lambda_mult": 0.5,
        "filter": filters,
    }

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs=search_kwargs,
    )

    return retriever.invoke(query)