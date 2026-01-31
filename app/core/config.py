"""Application configuration using Pydantic Settings."""

import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Metadata
    api_title: str = "Email Classification API"
    api_version: str = "1.0.0"
    api_description: str = "API para classificação e análise de emails usando ML"
    
    # Server Configuration
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Gemini API Configuration
    gemini_api_key: str = Field(
        default="",
        description="Gemini API Key - deve ser configurada no arquivo .env como GEMINI_API_KEY"
    )
    gemini_model_name: str = "gemini-2.5-flash"
    
    # Model Configuration
    model_path: str = ""
    default_model_name: str = "distilbert-base-uncased"
    
    # RAG Configuration
    rag_enabled: bool = True
    rag_knowledge_base_path: str = "rag_knowledge_base"
    rag_embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    rag_top_k_results: int = 3
    rag_min_similarity_score: float = 0.5
    rag_max_email_length: int = 50000
    
    # File Processing Configuration
    supported_file_extensions: List[str] = [".txt", ".pdf"]
    default_encoding: str = "utf-8"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    #get the model name, checking if fine-tuned model exists
    #@return: model name
    def get_model_name(self) -> str:
        import os
        if os.path.exists(self.model_path) and os.path.isdir(self.model_path):
            return self.model_path
        return self.default_model_name


# Global settings instance
settings = Settings()

