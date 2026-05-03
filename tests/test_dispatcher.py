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


def test_generate_system_prompt_includes_role():
    dispatcher = ToolDispatcher()
    prompt = dispatcher.generate_system_prompt(role_prompt="# 测试角色\n行为准则")
    assert prompt.startswith("# 测试角色")
    assert "行为准则" in prompt


def test_generate_system_prompt_without_role():
    """不传 role_prompt 时从 load_role 读取，prompt 应包含角色内容"""
    dispatcher = ToolDispatcher()
    prompt = dispatcher.generate_system_prompt()
    assert "白泽" in prompt
    assert "## 1. 做什么" in prompt
    assert "【tool】" in prompt


def test_generate_system_prompt_contains_param_hints():
    dispatcher = ToolDispatcher()
    prompt = dispatcher.generate_system_prompt()
    assert "（必需）" in prompt
    assert "（可选）" in prompt


def test_dispatcher_with_custom_tools():
    from src.tools.tool_base import Tool

    custom = Tool(
        name="custom_tool",
        description="A test tool",
        parameters={"type": "object", "properties": {}, "required": []},
        fn=lambda: "custom result",
    )
    dispatcher = ToolDispatcher(tools=[custom])
    assert "custom_tool" in dispatcher.tools
    assert "calculator" not in dispatcher.tools
    result = dispatcher.dispatch("custom_tool", {})
    assert result == "custom result"


def test_dispatcher_with_none_uses_defaults():
    dispatcher = ToolDispatcher(tools=None)
    assert "calculator" in dispatcher.tools
    assert "file_read" in dispatcher.tools


def test_system_prompt_forbids_xml_format():
    dispatcher = ToolDispatcher()
    prompt = dispatcher.generate_system_prompt()
    assert "禁止" in prompt or "不得" in prompt or "严禁" in prompt or "不要" in prompt
    assert "XML" in prompt or "<tool" in prompt or "<invoke" in prompt
