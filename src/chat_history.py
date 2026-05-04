from typing import Optional
from .message import (
    AssistantMessage,
    ToolCallMessage,
    ToolResultMessage,
    UserMessage,
)


class ChatHistory:
    def __init__(self, max_turns: int = 20):
        self.messages = []
        self.max_turns = max_turns

    def add_user(self, content: str):
        self.messages.append(UserMessage(content))
        self._trim()

    def add_assistant(self, content: str, reasoning_content: str = None):
        self.messages.append(AssistantMessage(content, reasoning_content))
        self._trim()

    def add_tool_call(self, content: Optional[str], tool_name: str, arguments: str, reasoning_content: str = None, tool_call_id: str = None) -> str:
        msg = ToolCallMessage(content, tool_name, arguments, tool_call_id=tool_call_id, reasoning_content=reasoning_content)
        self.messages.append(msg)
        self._trim()
        return msg.tool_call_id

    def add_tool_result(self, tool_call_id: str, name: str, content: str):
        self.messages.append(ToolResultMessage(tool_call_id, name, content))
        self._trim()

    def get_context(self):
        return [m.to_dict() for m in self.messages]

    def _trim(self):
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2 :]
            while self.messages and isinstance(self.messages[0], ToolResultMessage):
                self.messages.pop(0)
