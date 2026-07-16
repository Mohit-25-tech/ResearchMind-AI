from app.rag.vector_store import get_vector_store


def retrieve_chunks(query: str, k: int = 4):
    """
    Retrieve the most relevant document chunks.
    """

    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_kwargs={"k": k}
    )

    return retriever.invoke(query)