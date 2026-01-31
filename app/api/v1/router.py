"""API v1 router combining all endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import email, email_flow, health, rag

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(email.router)
api_router.include_router(email_flow.router)
api_router.include_router(rag.router)

