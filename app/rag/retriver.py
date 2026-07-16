from app.rag.vector_store import get_vector_store


def retrieve_chunks(
    query: str,
    k: int = 5,
    document_id: str | None = None,
):
    """
    Retrieve relevant chunks.
    Optionally restrict retrieval to a single document.
    """

    vector_store = get_vector_store()

    search_kwargs = {
        "k": k,
        "fetch_k": 20,
        "lambda_mult": 0.5,
    }

    if document_id is not None:

        search_kwargs["filter"] = {
            "document_id": document_id
        }

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs=search_kwargs,
    )

    return retriever.invoke(query)