from src.chat_history import ChatHistory
from src.message import AssistantMessage, ToolCallMessage, ToolResultMessage, UserMessage


def test_add_user_message():
    history = ChatHistory()
    history.add_user("Hello")
    assert len(history.messages) == 1
    assert isinstance(history.messages[0], UserMessage)
    assert history.messages[0].role == "user"


def test_add_assistant_message():
    history = ChatHistory()
    history.add_assistant("Hi there")
    assert len(history.messages) == 1
    assert isinstance(history.messages[0], AssistantMessage)
    assert history.messages[0].role == "assistant"


def test_add_tool_call_and_result():
    history = ChatHistory()
    tool_call_id = history.add_tool_call(
        None, "calculator", '{"expr": "2+2"}'
    )
    assert len(history.messages) == 1
    assert isinstance(history.messages[0], ToolCallMessage)
    assert history.messages[0].role == "assistant"
    assert history.messages[0].tool_name == "calculator"

    history.add_tool_result(tool_call_id, "calculator", "4")
    assert len(history.messages) == 2
    assert isinstance(history.messages[1], ToolResultMessage)
    assert history.messages[1].role == "tool"
    assert history.messages[1].tool_call_id == tool_call_id


def test_get_context():
    history = ChatHistory()
    history.add_user("Hello")
    history.add_assistant("Hi")
    context = history.get_context()
    assert len(context) == 2
    assert isinstance(context[0], dict)
    assert context[0]["role"] == "user"
    assert context[1]["role"] == "assistant"


def test_tool_call_with_reasoning_content():
    history = ChatHistory()
    history.add_tool_call(
        None,
        "calculator",
        '{"expr": "2+2"}',
        reasoning_content="Let me calculate...",
    )
    context = history.get_context()
    assert len(context) == 1
    assert context[0]["reasoning_content"] == "Let me calculate..."


def test_tool_call_without_reasoning_content():
    history = ChatHistory()
    history.add_tool_call(
        None,
        "calculator",
        '{"expr": "2+2"}',
    )
    context = history.get_context()
    assert "reasoning_content" not in context[0]


def test_add_tool_call_with_api_provided_id():
    history = ChatHistory()
    tool_call_id = history.add_tool_call(
        None, "calculator", '{"expr": "2+2"}', tool_call_id="call_abc123"
    )
    assert tool_call_id == "call_abc123"
    assert isinstance(history.messages[0], ToolCallMessage)
    assert history.messages[0].content is None


def test_tool_call_message_content_none_in_dict():
    history = ChatHistory()
    history.add_tool_call(
        None, "calculator", '{"expr": "2+2"}', tool_call_id="call_1"
    )
    context = history.get_context()
    assert context[0]["content"] is None
    assert context[0]["tool_calls"][0]["id"] == "call_1"
