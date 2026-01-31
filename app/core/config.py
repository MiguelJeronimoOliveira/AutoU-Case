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
    
    # Email Configuration
    email_address: str = Field(
        default="",
        description="Email address for receiving and sending emails"
    )
    email_password: str = Field(
        default="",
        description="Email password or app password"
    )
    email_imap_server: str = Field(
        default="imap.gmail.com",
        description="IMAP server address"
    )
    email_imap_port: int = Field(
        default=993,
        description="IMAP server port"
    )
    email_smtp_server: str = Field(
        default="smtp.gmail.com",
        description="SMTP server address"
    )
    email_smtp_port: int = Field(
        default=465,
        description="SMTP server port"
    )
    email_use_ssl: bool = Field(
        default=True,
        description="Whether to use SSL for email connections"
    )
    email_check_interval: int = Field(
        default=60,
        description="Interval in seconds to check for new emails"
    )
    email_auto_reply_enabled: bool = Field(
        default=False,
        description="Enable automatic email replies with suggestions"
    )
    email_auto_reply_only_productive: bool = Field(
        default=True,
        description="Only auto-reply to productive emails (if False, replies to all)"
    )
    email_auto_reply_min_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score required for auto-reply"
    )
    
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

