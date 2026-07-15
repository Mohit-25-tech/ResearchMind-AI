from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="all-minilm:l6"
)

def get_embedding_function():
    return embeddings