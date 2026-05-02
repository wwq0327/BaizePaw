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


def test_generate_system_prompt_contains_all_tools():
    dispatcher = ToolDispatcher()
    prompt = dispatcher.generate_system_prompt()
    assert "calculator" in prompt
    assert "file_read" in prompt
    assert "file_write" in prompt
    assert "delete_file" in prompt
    assert "move_file" in prompt
    assert "grep_file" in prompt
    assert "search" in prompt
    assert "list_dir" in prompt
    assert "copy_file" in prompt
    assert "file_append" in prompt
    assert "find_file" in prompt
    assert prompt.startswith("你叫白泽")
    assert "【tool】" in prompt


def test_generate_system_prompt_contains_param_hints():
    dispatcher = ToolDispatcher()
    prompt = dispatcher.generate_system_prompt()
    assert "（必需）" in prompt
    assert "（可选）" in prompt
