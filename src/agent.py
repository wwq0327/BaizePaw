import re
from config import MAX_LOOP
from .llm_client import LLMClient
from .chat_history import ChatHistory
from .tools.dispatcher import ToolDispatcher

class AgentRunner:
    def __init__(self):
        self.llm = LLMClient()
        self.history = ChatHistory()
        self.dispatcher = ToolDispatcher()

    def run(self, user_input: str) -> str:
        self.history.add_user(user_input)

        for _ in range(MAX_LOOP):
            # 调用 LLM
            response = self.llm.chat(self.history.get_context())

            # 检查是否包含工具调用
            tool_match = re.search(r"【tool】(\w+)【/tool】", response)
            if tool_match:
                tool_name = tool_match.group(1)
                # 从响应中提取工具参数（简化版：直接解析【tool】后的内容）
                self.history.add_assistant(response)

                # 解析参数并执行
                # 这里简化处理，实际可以从 response 中解析参数
                tool_result = self.dispatcher.dispatch(tool_name, {})
                self.history.add_tool_result(tool_name, tool_result)
                continue

            # 没有工具调用，返回结果
            self.history.add_assistant(response)
            return response

        return "Maximum loops exceeded"