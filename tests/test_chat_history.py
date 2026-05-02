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

def test_add_tool_result():
    history = ChatHistory()
    history.add_tool_result("search", "result data")
    assert len(history.messages) == 1
    assert history.messages[0]["role"] == "tool"
    assert history.messages[0]["name"] == "search"

def test_get_context():
    history = ChatHistory()
    history.add_user("Hello")
    history.add_assistant("Hi")
    context = history.get_context()
    assert len(context) == 2