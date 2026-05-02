import pytest
from unittest.mock import patch, MagicMock
from src.llm_client import LLMClient

@pytest.fixture
def client():
    return LLMClient(api_key="test-key", model="test-model")

def test_chat_returns_string(client):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello!"}}]
        }
        mock_post.return_value = mock_response

        result = client.chat([{"role": "user", "content": "hi"}])
        assert result == "Hello!"

def test_chat_with_tools(client):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Searching..."}}]
        }
        mock_post.return_value = mock_response

        result = client.chat([{"role": "user", "content": "search"}])
        assert "Searching" in result