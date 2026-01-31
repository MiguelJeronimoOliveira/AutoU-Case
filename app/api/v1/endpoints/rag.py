"""RAG (Retrieval-Augmented Generation) endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_rag_retriever
from app.handlers import RAGHandler

router = APIRouter()


@router.get("/rag/stats", tags=["rag"])
async def get_rag_stats(
    rag_retriever=Depends(get_rag_retriever)
) -> dict:
    """Get RAG collection statistics."""
    rag_handler = RAGHandler(rag_retriever)
    return rag_handler.get_rag_stats()


@router.get("/rag/documents", tags=["rag"])
async def get_rag_documents(
    limit: int = Query(50, ge=1, le=500),
    category: Optional[str] = Query(None, regex="^(productive|unproductive)$"),
    full: bool = Query(False),
    rag_retriever=Depends(get_rag_retriever)
) -> dict:
    """Get RAG documents with optional filtering."""
    rag_handler = RAGHandler(rag_retriever)
    return rag_handler.get_rag_documents(limit, category, full)


@router.delete("/rag/clear", tags=["rag"])
async def clear_rag_history(
    rag_retriever=Depends(get_rag_retriever)
) -> dict:
    """Clear RAG history."""
    rag_handler = RAGHandler(rag_retriever)
    return rag_handler.clear_rag_history()

