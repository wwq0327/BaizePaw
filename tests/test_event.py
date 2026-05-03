from src.event import DoneEvent, ErrorEvent, ToolEvent


def test_tool_event():
    ev = ToolEvent(tool_name="calculator", params={"expr": "1+1"}, result="2", command="calc 1+1")
    assert ev.tool_name == "calculator"
    assert ev.params == {"expr": "1+1"}
    assert ev.result == "2"
    assert ev.command == "calc 1+1"


def test_done_event():
    ev = DoneEvent(content="hello world")
    assert ev.content == "hello world"


def test_error_event():
    ev = ErrorEvent(message="something broke")
    assert ev.message == "something broke"
