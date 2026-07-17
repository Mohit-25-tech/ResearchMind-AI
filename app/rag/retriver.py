from app.rag.vector_store import get_vector_store

def retrieve_chunks(
    query: str,
    user_id: int,
    k: int = 5,
    document_id: str | None = None,
):
    """
    Retrieve relevant chunks for the user.
    Strictly filters results to match the user_id.
    """
    vector_store = get_vector_store()

    filters = {"user_id": user_id}
    if document_id is not None:
        filters = {
            "$and": [
                {"user_id": user_id},
                {"document_id": document_id}
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