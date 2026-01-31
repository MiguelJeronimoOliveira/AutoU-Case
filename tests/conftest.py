"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_email_content():
    """Sample email content for testing."""
    return "Olá, gostaria de solicitar informações sobre o produto."


@pytest.fixture
def test_productive_email():
    """Sample productive email content."""
    return "Preciso de ajuda urgente com meu pedido #12345. O produto não chegou."


@pytest.fixture
def test_unproductive_email():
    """Sample unproductive email content."""
    return "Obrigado pelo excelente atendimento! Ficamos muito satisfeitos."

