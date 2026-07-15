from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="all-minilm:l6")

def get_embedding_function():
    """Local, free embedding model — runs on CPU, no API key needed."""
    return embeddings

    