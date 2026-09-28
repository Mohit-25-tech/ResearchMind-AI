from app.rag.vector_store import get_vector_store
from app.services.database import get_connection

def retrieve_chunks(
    query: str,
    user_id: int,
    k: int = 5,
    document_id: str | list[str] | None = None,
    document_ids: list[str] | str | None = None,
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

    target_input = document_ids if document_ids is not None else document_id
    if target_input:
        if isinstance(target_input, str):
            requested = [d.strip() for d in target_input.split(",") if d.strip()]
        else:
            requested = [str(d).strip() for d in target_input if str(d).strip()]
        target_ids = [d for d in requested if d in valid_doc_ids]
        if not target_ids:
            return []
    else:
        target_ids = valid_doc_ids

    vector_store = get_vector_store()

    if len(target_ids) == 1:
        filters = {
            "$and": [
                {"user_id": user_id},
                {"document_id": target_ids[0]}
            ]
        }
    else:
        filters = {
            "$and": [
                {"user_id": user_id},
                {"document_id": {"$in": target_ids}}
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