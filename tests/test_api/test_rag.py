"""Tests for RAG endpoints."""

import pytest


def test_rag_stats_endpoint(client):
    """Test RAG stats endpoint."""
    response = client.get("/api/v1/rag/stats")
    # May return 503 if RAG is not available, or 200 if available
    assert response.status_code in [200, 503]


def test_rag_documents_endpoint(client):
    """Test RAG documents endpoint."""
    response = client.get("/api/v1/rag/documents?limit=10")
    # May return 503 if RAG is not available, or 200 if available
    assert response.status_code in [200, 503]


def test_rag_documents_with_category(client):
    """Test RAG documents endpoint with category filter."""
    response = client.get("/api/v1/rag/documents?limit=10&category=productive")
    assert response.status_code in [200, 503]


def test_rag_clear_endpoint(client):
    """Test RAG clear endpoint."""
    response = client.delete("/api/v1/rag/clear")
    # May return 503 if RAG is not available, or 200 if available
    assert response.status_code in [200, 503]

