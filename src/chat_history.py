import uuid

class ChatHistory:
    def __init__(self, max_turns: int = 20):
        self.messages = []
        self.max_turns = max_turns
        self._tool_call_id = None

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def add_tool_result(self, name: str, content: str, tool_call_id: str = None):
        if tool_call_id is None:
            tool_call_id = str(uuid.uuid4())
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
            "content": content
        })
        self._trim()

    def set_next_tool_call_id(self, tool_call_id: str):
        self._tool_call_id = tool_call_id

    def get_next_tool_call_id(self) -> str:
        return self._tool_call_id or str(uuid.uuid4())

    def get_context(self):
        return self.messages

    def _trim(self):
        # 保留最近的 max_turns * 2 条（user + assistant 各算一轮）
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]