import os
from langchain_ollama import OllamaEmbeddings

OLLAMA_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "all-minilm:l6")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def get_embedding_function(model_name: str | None = None) -> OllamaEmbeddings:
    """
    Get Ollama embeddings using local Ollama (default: all-minilm:l6).
    """
    selected_model = model_name or OLLAMA_MODEL
    return OllamaEmbeddings(
        model=selected_model,
        base_url=OLLAMA_BASE_URL,
    )