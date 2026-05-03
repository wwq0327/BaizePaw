from unittest.mock import MagicMock, patch

from src.core import Core
from src.event import DoneEvent, ErrorEvent, ToolEvent


def _make_core(mock_client):
    with patch("src.core.LLMClient", return_value=mock_client):
        return Core()


def test_no_tool_yields_done():
    mock_client = MagicMock()
    mock_client.chat.return_value = "Hello!"
    core = _make_core(mock_client)

    events = list(core.run_iter("Hi"))
    assert len(events) == 1
    assert isinstance(events[0], DoneEvent)
    assert events[0].content == "Hello!"


def test_tool_then_done():
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        '【tool】calculator【/tool】{"expr": "2+2"}',
        "The answer is 4",
    ]
    core = _make_core(mock_client)

    events = list(core.run_iter("calc 2+2"))
    assert len(events) == 2
    assert isinstance(events[0], ToolEvent)
    assert events[0].tool_name == "calculator"
    assert isinstance(events[1], DoneEvent)
    assert "4" in events[1].content


def test_raw_tool_text_not_in_events():
    """LLM 原始含【tool】的文本不出现在 Event 中"""
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        '【tool】calculator【/tool】{"expr": "1+1"}',
        "Done",
    ]
    core = _make_core(mock_client)

    events = list(core.run_iter("test"))
    for ev in events:
        if isinstance(ev, DoneEvent):
            assert "【tool】" not in ev.content
        if isinstance(ev, ToolEvent):
            assert "【tool】" not in ev.tool_name


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
        mock_client.chat.return_value = "OK"
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
    mock_client.chat.return_value = "OK"
    with patch("src.core.LLMClient", return_value=mock_client):
        core = Core(tools=[custom])
    assert "custom" in core.dispatcher.tools
    assert "calculator" not in core.dispatcher.tools


def test_tool_xml_format_fallback():
    """LLM 输出 XML 格式工具调用时也能解析"""
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        '<tool_call>\n<invoke name="calculator">\n<parameter name="expr">2+2</parameter>\n</invoke>\n</tool_call>',
        "The answer is 4",
    ]
    core = _make_core(mock_client)

    events = list(core.run_iter("calc 2+2"))
    assert len(events) == 2
    assert isinstance(events[0], ToolEvent)
    assert events[0].tool_name == "calculator"
    assert isinstance(events[1], DoneEvent)


def test_filters_dsml_markup():
    """过滤 content 中的 <| | DSML |> 等内部标记"""
    mock_client = MagicMock()
    mock_client.chat.return_value = "Hello <| | DSML | | tool_calls> world"
    core = _make_core(mock_client)

    events = list(core.run_iter("Hi"))
    assert len(events) == 1
    assert isinstance(events[0], DoneEvent)
    assert "<<|" not in events[0].content
    assert "DSML" not in events[0].content
