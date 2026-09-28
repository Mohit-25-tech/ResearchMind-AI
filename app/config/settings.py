import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration and feature flags.
    """
    # Feature flags for retrieval and agent evaluation
    use_agent: bool = os.getenv("USE_AGENT", "true").lower() in ("true", "1", "yes")
    use_hybrid: bool = os.getenv("USE_HYBRID", "true").lower() in ("true", "1", "yes")
    use_reranker: bool = os.getenv("USE_RERANKER", "true").lower() in ("true", "1", "yes")

    # Reranker settings
    reranker_model: str = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")

    # Ollama settings
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "all-minilm:l6")

    # Groq settings
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    # Database & Storage
    database_path: str = os.getenv("DATABASE_PATH", "database/research.db")
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "chroma_db")
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")

settings = Settings()
