from langchain_chroma import Chroma

from app.rag.embeddings import get_embedding_function

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "research_documents"


def get_vector_store():
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_PATH,
    )


def create_vector_store(chunks):
    vector_store = get_vector_store()

    if chunks:
        vector_store.add_documents(chunks)

    return vector_store


def delete_document_vectors(document_id: str):
    """
    Delete all chunks belonging to a document.
    """

    vector_store = get_vector_store()

    vector_store.delete(
        where={
            "document_id": document_id
        }
    )