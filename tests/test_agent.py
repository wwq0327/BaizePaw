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


def test_tool_result_uses_tool_role():
    """工具结果用 tool role 发送，不混在 user 里"""
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            '【tool】calculator【/tool】{"expr": "2+2"}',
            "4",
        ]
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        agent.run("calc")

        # 验证历史中有 tool role 消息
        tool_msgs = [
            m for m in agent.history.messages if m.get("role") == "tool"
        ]
        assert len(tool_msgs) == 1
        assert tool_msgs[0]["name"] == "calculator"
        assert "4" in str(tool_msgs[0]["content"])

        # 验证没有 user role 的消息以"工具「"开头（旧格式）
        user_msgs = [m for m in agent.history.messages if m.get("role") == "user"]
        assert not any(
            m.get("content", "").startswith("工具「") for m in user_msgs
        )


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
