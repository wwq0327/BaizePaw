# DEPRECATED: Use src.core.Core instead. This module will be removed in v0.3.
import json
from .llm_client import LLMClient
from .chat_history import ChatHistory
from .tools.dispatcher import ToolDispatcher


class AgentRunner:
    def __init__(self):
        self.dispatcher = ToolDispatcher()
        system_prompt = self.dispatcher.generate_system_prompt()
        tools_param = self.dispatcher.generate_tools_param()
        self.llm = LLMClient(system_prompt=system_prompt, tools=tools_param)
        self.history = ChatHistory()

    def run(self, user_input: str) -> str:
        self.history.add_user(user_input)

        while True:
            response = self.llm.chat(self.history.get_context())

            if response.tool_calls:
                for tc in response.tool_calls:
                    tool_call_id = tc["id"]
                    tool_name = tc["function"]["name"]
                    args_json = tc["function"]["arguments"]
                    params = json.loads(args_json)

                    self.history.add_tool_call(
                        response.content,
                        tool_name,
                        args_json,
                        tool_call_id=tool_call_id,
                    )

                    tool_result = self.dispatcher.dispatch(tool_name, params)
                    self.history.add_tool_result(
                        tool_call_id, tool_name, str(tool_result)
                    )
                continue

            content = response.content or ""
            self.history.add_assistant(content)
            return content
