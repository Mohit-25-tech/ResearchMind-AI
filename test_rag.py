from app.rag.vector_store import get_vector_store

store = get_vector_store()

data = store.get()

print(data["metadatas"][0].keys())