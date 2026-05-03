from unittest.mock import MagicMock, patch

from src.llm_client import LLMClient
from src.message import AssistantMessage


def test_chat_response_has_reasoning_content():
    with patch("src.llm_client.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Hello",
                    "reasoning_content": "Let me think...",
                }
            }]
        }
        mock_post.return_value = mock_resp

        client = LLMClient(api_key="test", base_url="http://test", model="test")
        result = client.chat([{"role": "user", "content": "hi"}])

        assert str(result) == "Hello"
        assert hasattr(result, "reasoning_content")
        assert result.reasoning_content == "Let me think..."


def test_chat_response_without_reasoning_content():
    with patch("src.llm_client.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Hello"}}]
        }
        mock_post.return_value = mock_resp

        client = LLMClient(api_key="test", base_url="http://test", model="test")
        result = client.chat([{"role": "user", "content": "hi"}])

        assert str(result) == "Hello"
        assert result.reasoning_content is None


def test_assistant_message_to_dict_includes_reasoning():
    msg = AssistantMessage(content="hi", reasoning_content="thinking...")
    d = msg.to_dict()
    assert d["role"] == "assistant"
    assert d["content"] == "hi"
    assert d["reasoning_content"] == "thinking..."


def test_assistant_message_to_dict_without_reasoning():
    msg = AssistantMessage(content="hi")
    d = msg.to_dict()
    assert d["role"] == "assistant"
    assert d["content"] == "hi"
    assert "reasoning_content" not in d
