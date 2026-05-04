from typing import Any, Dict
from .tool_base import Tool
from .calculator import calculator_tool
from .search import search_tool
from .file_ops import (
    read_file_tool,
    write_file_tool,
    file_append_tool,
    copy_file_tool,
    list_dir_tool,
    find_file_tool,
    delete_file_tool,
    move_file_tool,
    grep_file_tool,
)


_DEFAULT_TOOLS = [
    calculator_tool,
    search_tool,
    read_file_tool,
    write_file_tool,
    file_append_tool,
    copy_file_tool,
    list_dir_tool,
    find_file_tool,
    delete_file_tool,
    move_file_tool,
    grep_file_tool,
]


class ToolDispatcher:
    def __init__(self, tools: list = None):
        self.tools: Dict[str, Tool] = {}
        tool_list = tools if tools is not None else _DEFAULT_TOOLS
        for t in tool_list:
            self.register(t)

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def dispatch(self, tool_name: str, params: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"
        tool = self.tools[tool_name]
        try:
            allowed = set(tool.parameters.get("properties", {}).keys())
            safe_params = {k: v for k, v in params.items() if k in allowed}
            return str(tool.fn(**safe_params))
        except Exception as e:
            return f"Tool error: {e}"

    def generate_tools_param(self) -> list:
        """将已注册工具序列化为 OpenAI function calling tools 格式。"""
        tools = []
        for tool in self.tools.values():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
            )
        return tools

    def generate_system_prompt(self, role_prompt: str = None) -> str:
        if role_prompt is None:
            from ..role import load_role
            role_prompt = load_role()
        lines = [role_prompt, "", "---", "", "可用工具："]
        for tool in self.tools.values():
            props = tool.parameters.get("properties", {})
            required = tool.parameters.get("required", [])
            param_parts = []
            for name, schema in props.items():
                desc = schema.get("description", name)
                hint = "（必需）" if name in required else "（可选）"
                param_parts.append(f"{name}{hint} — {desc}")
            lines.append(
                f"- {tool.name}：{tool.description}。参数：{'，'.join(param_parts)}"
            )
        lines.extend(
            [
                "",
                '使用格式：【tool】工具名【/tool】{"参数名": "参数值"}',
                "",
                "重要约束：",
                "- 调用工具时，回复中只能包含上述【tool】格式，严禁输出 XML、<tool_call>、<invoke>、<| 等标记",
                "- 不调用工具时，回复中不得包含任何工具相关标记",
                "- 不输出思考过程，需要调用工具就直接输出工具调用",
            ]
        )
        return "\n".join(lines)
