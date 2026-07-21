import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication for testing."""
    with patch("backend.app.services.auth.AuthService.validate_token") as mock:
        mock.return_value = {"sub": "test-user-123", "oid": "test-user-123"}
        yield mock


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestChatEndpoint:
    """Tests for the chat endpoint."""

    @patch("backend.app.services.llm_client.LLMClient.generate_response")
    def test_chat_endpoint_success(self, mock_llm, client, mock_auth):
        """Chat endpoint should return LLM response."""
        mock_llm.return_value = {"response": "Test response", "confidence": 0.95}
        
        headers = {"Authorization": "Bearer test-token"}
        payload = {"query": "Hello, world!"}
        
        response = client.post("/api/chat", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["confidence"] >= 0.0

    def test_chat_endpoint_unauthorized(self, client):
        """Chat endpoint should reject requests without auth."""
        payload = {"query": "Hello, world!"}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 403

    def test_chat_endpoint_empty_query(self, client, mock_auth):
        """Chat endpoint should validate query input."""
        headers = {"Authorization": "Bearer test-token"}
        payload = {"query": ""}
        
        response = client.post("/api/chat", json=payload, headers=headers)
        assert response.status_code == 422