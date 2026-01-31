"""Dependency injection for API endpoints."""

from functools import lru_cache
from typing import Optional

from app.classifier import EmailClassifier
from app.file_processor import FileProcessor
from app.rag_retriever import RAGRetriever
from app.response_generator import ResponseGenerator


@lru_cache()
def get_classifier() -> EmailClassifier:
    """Get or create EmailClassifier instance (singleton)."""
    return EmailClassifier()


@lru_cache()
def get_response_generator() -> ResponseGenerator:
    """Get or create ResponseGenerator instance (singleton)."""
    return ResponseGenerator()


@lru_cache()
def get_file_processor() -> FileProcessor:
    """Get or create FileProcessor instance (singleton)."""
    return FileProcessor()


def get_rag_retriever() -> Optional[RAGRetriever]:
    """Get RAG retriever from response generator if available."""
    response_generator = get_response_generator()
    if response_generator.use_rag and response_generator.rag_retriever:
        return response_generator.rag_retriever
    return None

