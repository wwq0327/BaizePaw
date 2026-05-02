import pytest
from unittest.mock import patch, MagicMock
from src.agent import AgentRunner
from src.chat_history import ChatHistory

def test_single_turn():
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.return_value = "Hello, I'm BaizePaw!"
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("Hi")
        assert "BaizePaw" in result

def test_tool_call_loop():
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        # 第一次返回工具调用，第二次返回最终结果
        mock_client.chat.side_effect = [
            "【tool】calculator【/tool】2+2",
            "2 + 2 = 4"
        ]
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("What's 2+2?")
        assert "4" in result