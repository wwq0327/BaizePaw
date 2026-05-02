import pytest
from unittest.mock import patch, MagicMock
from src.agent import AgentRunner


def test_single_turn():
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.return_value = "Hello, I'm BaizePaw!"
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("Hi")
        assert "BaizePaw" in result


def test_tool_call_with_json_params():
    """LLM 返回 JSON 格式的参数"""
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            '【tool】calculator【/tool】{"expr": "2+2"}',
            "2 + 2 = 4",
        ]
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("What's 2+2?")
        assert "4" in result


def test_tool_call_with_legacy_params():
    """旧格式参数仍然兼容"""
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            "【tool】calculator【/tool】2+2",
            "2 + 2 = 4",
        ]
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("calc 2+2")
        assert "4" in result
