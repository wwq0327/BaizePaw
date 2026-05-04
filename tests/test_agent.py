import pytest
from unittest.mock import patch, MagicMock
from src.agent import AgentRunner
from src.llm_client import ChatResponse


def _tool_call(name, arguments, call_id=None):
    return {
        "id": call_id or f"call_{name}",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def test_single_turn():
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.return_value = ChatResponse(content="Hello, I'm BaizePaw!")
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("Hi")
        assert "BaizePaw" in result


def test_tool_call_with_json_params():
    """LLM 返回标准 function calling 工具调用"""
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            ChatResponse(
                content=None,
                tool_calls=[_tool_call("calculator", '{"expr": "2+2"}')],
            ),
            ChatResponse(content="2 + 2 = 4"),
        ]
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("What's 2+2?")
        assert "4" in result


def test_tool_result_uses_tool_role():
    """工具结果用 tool role 发送，不混在 user 里"""
    from src.message import ToolResultMessage, UserMessage

    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            ChatResponse(
                content=None,
                tool_calls=[_tool_call("calculator", '{"expr": "2+2"}')],
            ),
            ChatResponse(content="4"),
        ]
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        agent.run("calc")

        tool_msgs = [
            m for m in agent.history.messages if isinstance(m, ToolResultMessage)
        ]
        assert len(tool_msgs) == 1
        assert tool_msgs[0].name == "calculator"

        user_msgs = [m for m in agent.history.messages if isinstance(m, UserMessage)]
        assert not any(m.content.startswith("工具「") for m in user_msgs)
