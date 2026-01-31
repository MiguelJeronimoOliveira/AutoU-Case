"""Tests for email analysis endpoints."""

import pytest


def test_analyze_email_endpoint(client, test_email_content):
    """Test email analysis endpoint with content."""
    response = client.post(
        "/api/v1/analyze",
        json={"email_content": test_email_content}
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "analysis" in data
    if data["success"]:
        assert "category" in data["analysis"]
        assert "confidence" in data["analysis"]


def test_analyze_email_missing_fields(client):
    """Test email analysis endpoint without required fields."""
    response = client.post("/api/v1/analyze", json={})
    assert response.status_code == 422  # Validation error


def test_analyze_email_empty_content(client):
    """Test email analysis endpoint with empty content."""
    response = client.post(
        "/api/v1/analyze",
        json={"email_content": ""}
    )
    # Should still return 200 but with unproductive classification
    assert response.status_code == 200

