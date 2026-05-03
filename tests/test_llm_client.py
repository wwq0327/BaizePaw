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
        assert str(result) == "Hello!"


def test_chat_with_tools(client):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Searching..."}}]
        }
        mock_post.return_value = mock_response

        result = client.chat([{"role": "user", "content": "search"}])
        assert "Searching" in str(result)


def test_chat_with_custom_system_prompt():
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Custom!"}}]
        }
        mock_post.return_value = mock_response

        client = LLMClient(
            api_key="test-key",
            model="test-model",
            system_prompt="Custom system prompt",
        )
        result = client.chat([{"role": "user", "content": "hi"}])
        call_kwargs = mock_post.call_args[1]
        sent_messages = call_kwargs["json"]["messages"]
        assert sent_messages[0]["content"] == "Custom system prompt"
        assert str(result) == "Custom!"
