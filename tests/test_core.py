from unittest.mock import MagicMock, patch

from src.core import Core
from src.event import DoneEvent, ErrorEvent, ToolEvent
from src.llm_client import ChatResponse


def _tool_call(name, arguments, call_id=None):
    """构造 OpenAI tool_calls 条目。"""
    return {
        "id": call_id or f"call_{name}",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def _make_core(mock_client):
    with patch("src.core.LLMClient", return_value=mock_client):
        return Core()


def test_no_tool_yields_done():
    mock_client = MagicMock()
    mock_client.chat.return_value = ChatResponse(content="Hello!")
    core = _make_core(mock_client)

    events = list(core.run_iter("Hi"))
    assert len(events) == 1
    assert isinstance(events[0], DoneEvent)
    assert events[0].content == "Hello!"


def test_tool_then_done():
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        ChatResponse(
            content=None,
            tool_calls=[_tool_call("calculator", '{"expr": "2+2"}')],
        ),
        ChatResponse(content="The answer is 4"),
    ]
    core = _make_core(mock_client)

    events = list(core.run_iter("calc 2+2"))
    assert len(events) == 2
    assert isinstance(events[0], ToolEvent)
    assert events[0].tool_name == "calculator"
    assert events[0].params == {"expr": "2+2"}
    assert isinstance(events[1], DoneEvent)
    assert "4" in events[1].content


def test_multiple_tool_calls_in_one_response():
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        ChatResponse(
            content=None,
            tool_calls=[
                _tool_call("calculator", '{"expr": "1+1"}'),
                _tool_call("calculator", '{"expr": "2+2"}'),
            ],
        ),
        ChatResponse(content="Done"),
    ]
    core = _make_core(mock_client)

    events = list(core.run_iter("calc"))
    assert len(events) == 3
    assert isinstance(events[0], ToolEvent)
    assert events[0].tool_name == "calculator"
    assert events[0].params == {"expr": "1+1"}
    assert isinstance(events[1], ToolEvent)
    assert events[1].tool_name == "calculator"
    assert events[1].params == {"expr": "2+2"}
    assert isinstance(events[2], DoneEvent)


def test_error_yields_error_event():
    mock_client = MagicMock()
    mock_client.chat.side_effect = Exception("boom")
    core = _make_core(mock_client)

    events = list(core.run_iter("Hi"))
    assert len(events) == 1
    assert isinstance(events[0], ErrorEvent)
    assert "boom" in events[0].message


def test_core_with_custom_role_path():
    import tempfile, os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Custom Role\nBe helpful.")
        role_path = f.name

    try:
        mock_client = MagicMock()
        mock_client.chat.return_value = ChatResponse(content="OK")
        with patch("src.core.LLMClient", return_value=mock_client):
            core = Core(role_path=role_path)
        assert "Custom Role" in core.role_prompt
    finally:
        os.unlink(role_path)


def test_core_with_custom_tools():
    from src.tools.tool_base import Tool

    custom = Tool(
        name="custom",
        description="test",
        parameters={"type": "object", "properties": {}, "required": []},
        fn=lambda: "custom",
    )
    mock_client = MagicMock()
    mock_client.chat.return_value = ChatResponse(content="OK")
    with patch("src.core.LLMClient", return_value=mock_client):
        core = Core(tools=[custom])
    assert "custom" in core.dispatcher.tools
    assert "calculator" not in core.dispatcher.tools


def test_tool_call_id_preserved_in_history():
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        ChatResponse(
            content=None,
            tool_calls=[_tool_call("calculator", '{"expr": "2+2"}', "call_abc")],
        ),
        ChatResponse(content="Done"),
    ]
    core = _make_core(mock_client)

    list(core.run_iter("calc"))
    from src.message import ToolCallMessage

    tc_msgs = [m for m in core.history.messages if isinstance(m, ToolCallMessage)]
    assert len(tc_msgs) == 1
    assert tc_msgs[0].tool_call_id == "call_abc"


def test_chat_response_with_tool_calls():
    tc = {
        "id": "call_1",
        "type": "function",
        "function": {"name": "calculator", "arguments": '{"expr": "2+2"}'},
    }
    resp = ChatResponse(content=None, tool_calls=[tc])
    assert resp.content is None
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0]["function"]["name"] == "calculator"
    assert str(resp) == ""


def test_chat_response_without_tool_calls():
    resp = ChatResponse(content="Hello!", tool_calls=None)
    assert resp.content == "Hello!"
    assert resp.tool_calls is None
    assert str(resp) == "Hello!"
