from app.rag.vector_store import get_vector_store


def get_relevant_chunks(query: str, k: int = 4):

    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 8,
            "fetch_k": 20,
        },
    )

    return retriever.invoke(query)