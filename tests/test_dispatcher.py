import pytest
from src.tools.dispatcher import ToolDispatcher

def test_dispatch_calculator():
    dispatcher = ToolDispatcher()
    result = dispatcher.dispatch("calculator", {"expr": "2 + 3"})
    assert result == "5"

def test_dispatch_unknown_tool():
    dispatcher = ToolDispatcher()
    result = dispatcher.dispatch("unknown_tool", {})
    assert "Unknown tool" in result