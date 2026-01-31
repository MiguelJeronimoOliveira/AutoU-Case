"""Main FastAPI application for email classification API."""

import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_email_processor, get_email_service
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.email_background_task import EmailBackgroundTask

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app with metadata
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {"name": "email", "description": "Email analysis endpoints"},
        {"name": "rag", "description": "RAG (Retrieval Augmented Generation) endpoints"},
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Global background task instance
background_task: EmailBackgroundTask = None


@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    global background_task
    
    # Only start if email credentials are configured
    if settings.email_address and settings.email_password:
        try:
            email_service = get_email_service()
            email_processor = get_email_processor()
            background_task = EmailBackgroundTask(email_service, email_processor)
            background_task.start()
            logger.info("Background task de verificação de emails iniciada")
        except Exception as e:
            logger.warning(f"Não foi possível iniciar background task de emails: {str(e)}")
    else:
        logger.info("Credenciais de email não configuradas. Background task não iniciada.")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on application shutdown."""
    global background_task
    if background_task:
        background_task.stop()
        logger.info("Background task de verificação de emails parada")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Email Classification API",
        "version": settings.api_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.uvicorn_host,
        port=settings.uvicorn_port
    )
