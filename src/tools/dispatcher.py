from typing import Any, Dict
from .calculator import calc_tool
from .search import search_tool
from .file_ops import read_file_tool, write_file_tool, find_file_tool, delete_file_tool, move_file_tool, grep_file_tool

class ToolDispatcher:
    def __init__(self):
        self.tools = {
            "calculator": calc_tool,
            "search": search_tool,
            "file_read": read_file_tool,
            "file_write": write_file_tool,
            "find_file": find_file_tool,
            "delete_file": delete_file_tool,
            "move_file": move_file_tool,
            "grep_file": grep_file_tool,
        }

    def dispatch(self, tool_name: str, params: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"
        try:
            return str(self.tools[tool_name](**params))
        except Exception as e:
            return f"Tool error: {e}"
