import uuid
from typing import Optional


class UserMessage:
    role = "user"

    def __init__(self, content: str):
        self.content = content

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class AssistantMessage:
    role = "assistant"

    def __init__(self, content: str):
        self.content = content

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class ToolCallMessage:
    role = "assistant"

    def __init__(
        self,
        content: str,
        tool_name: str,
        arguments: str,
        tool_call_id: Optional[str] = None,
    ):
        self.content = content
        self.tool_name = tool_name
        self.arguments = arguments
        self._tool_call_id = tool_call_id or str(uuid.uuid4())

    @property
    def tool_call_id(self) -> str:
        return self._tool_call_id

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": [
                {
                    "id": self._tool_call_id,
                    "type": "function",
                    "function": {
                        "name": self.tool_name,
                        "arguments": self.arguments,
                    },
                }
            ],
        }


class ToolResultMessage:
    role = "tool"

    def __init__(self, tool_call_id: str, name: str, content: str):
        self.tool_call_id = tool_call_id
        self.name = name
        self.content = content

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "tool_call_id": self.tool_call_id,
            "name": self.name,
            "content": self.content,
        }
