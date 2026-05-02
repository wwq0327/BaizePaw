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

        for i in range(MAX_LOOP):
            # 调用 LLM
            response = self.llm.chat(self.history.get_context())

            # 检查是否包含工具调用
            # 匹配格式：【tool】toolname【/tool】参数
            tool_match = re.search(r"【tool】(\w+)【/tool】(.+?)(?=【|$)", response, re.DOTALL)
            if tool_match:
                tool_name = tool_match.group(1)
                tool_params = tool_match.group(2).strip()
                self.history.add_assistant(response)

                # 根据工具类型构建参数
                if tool_name == "calculator":
                    params = {"expr": tool_params} if tool_params else {}
                elif tool_name in ("file_read", "search"):
                    params = {"path": tool_params} if tool_params else {}
                elif tool_name == "file_write":
                    # file_write 需要 path 和 content，从 tool_params 解析
                    parts = tool_params.split(":", 1)
                    params = {"path": parts[0], "content": parts[1]} if len(parts) > 1 else {"path": tool_params}
                else:
                    params = {"expr": tool_params} if tool_params else {}

                # 执行工具
                tool_result = self.dispatcher.dispatch(tool_name, params)

                # 第一次工具调用：直接返回结果，不继续对话
                if i == 0:
                    self.history.add_assistant(str(tool_result))
                    return f"【{tool_name}】执行结果：{tool_result}"

                # 后续工具调用：把结果加入上下文，让 LLM 继续
                result_message = f"工具「{tool_name}」执行结果：{tool_result}"
                self.history.add_user(result_message)
                continue

            # 没有工具调用，返回结果
            self.history.add_assistant(response)
            return response

        return "Maximum loops exceeded"