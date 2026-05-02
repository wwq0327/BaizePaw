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


class ToolDispatcher:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        for t in [
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
        ]:
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

    def generate_system_prompt(self) -> str:
        lines = ["你叫白泽（BaizePaw），是一个个人助手。", "", "可用工具："]
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
            ]
        )
        return "\n".join(lines)
