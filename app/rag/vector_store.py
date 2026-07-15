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

    vector_store.add_documents(chunks)

    return vector_store

