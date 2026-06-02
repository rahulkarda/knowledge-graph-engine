from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "sqlite+aiosqlite:///./knowledge_graph.db"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "knowledge_nodes"

    # Supabase (for file storage)
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_bucket: str = "uploads"

    # Auth
    api_key: str = ""  # empty = auth disabled (local dev). Set in production env.

    # CORS
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Environment
    environment: str = "development"
    secret_key: str = "change-me-in-production"

    # NLP
    spacy_model: str = "en_core_web_sm"
    embedding_model: str = "all-MiniLM-L6-v2"
    whisper_model: str = "base"
    qa_model: str = "google/flan-t5-base"

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Connection discovery
    semantic_similarity_threshold: float = 0.75
    discovery_similarity_threshold: float = 0.65
    jaccard_threshold: float = 0.15


settings = Settings()
