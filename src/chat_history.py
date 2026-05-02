import uuid


class ChatHistory:
    def __init__(self, max_turns: int = 20):
        self.messages = []
        self.max_turns = max_turns

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def add_tool_call(self, content: str, tool_name: str, arguments: str) -> str:
        tool_call_id = str(uuid.uuid4())
        self.messages.append(
            {
                "role": "assistant",
                "content": content,
                "tool_calls": [
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": arguments,
                        },
                    }
                ],
            }
        )
        self._trim()
        return tool_call_id

    def add_tool_result(self, tool_call_id: str, name: str, content: str):
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": name,
                "content": content,
            }
        )
        self._trim()

    def get_context(self):
        return self.messages

    def _trim(self):
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2 :]
            # 删除后若首条是孤立的 tool role 消息，去掉（避免 API 校验报错）
            while self.messages and self.messages[0].get("role") == "tool":
                self.messages.pop(0)
