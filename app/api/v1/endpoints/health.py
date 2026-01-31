"""Health check endpoints."""

from fastapi import APIRouter, Depends

from app.api.deps import get_response_generator, get_rag_retriever
from app.handlers import HealthHandler

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check(
    response_generator=Depends(get_response_generator),
    rag_retriever=Depends(get_rag_retriever)
) -> dict:
    """Health check endpoint."""
    health_handler = HealthHandler(response_generator, rag_retriever)
    return health_handler.get_health_info()

