from src.chat_history import ChatHistory

def test_add_user_message():
    history = ChatHistory()
    history.add_user("Hello")
    assert len(history.messages) == 1
    assert history.messages[0]["role"] == "user"
    assert history.messages[0]["content"] == "Hello"

def test_add_assistant_message():
    history = ChatHistory()
    history.add_assistant("Hi there")
    assert len(history.messages) == 1
    assert history.messages[0]["role"] == "assistant"

def test_add_tool_call_and_result():
    history = ChatHistory()
    tool_call_id = history.add_tool_call(
        '【tool】calculator【/tool】{"expr": "2+2"}', "calculator", '{"expr": "2+2"}'
    )
    assert len(history.messages) == 1
    assert history.messages[0]["role"] == "assistant"
    assert "tool_calls" in history.messages[0]
    assert history.messages[0]["tool_calls"][0]["function"]["name"] == "calculator"

    history.add_tool_result(tool_call_id, "calculator", "4")
    assert len(history.messages) == 2
    assert history.messages[1]["role"] == "tool"
    assert history.messages[1]["tool_call_id"] == tool_call_id


def test_get_context():
    history = ChatHistory()
    history.add_user("Hello")
    history.add_assistant("Hi")
    context = history.get_context()
    assert len(context) == 2