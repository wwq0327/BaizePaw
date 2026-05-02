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

    def add_tool_result(self, name: str, content: str):
        self.messages.append({"role": "tool", "name": name, "content": content})
        self._trim()

    def get_context(self):
        return self.messages

    def _trim(self):
        # 保留最近的 max_turns * 2 条（user + assistant 各算一轮）
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]