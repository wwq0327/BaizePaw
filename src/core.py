import json
from typing import Generator, Optional

from .chat_history import ChatHistory
from .event import DoneEvent, ErrorEvent, ToolEvent
from .llm_client import ChatResponse, LLMClient
from .tools.dispatcher import ToolDispatcher
from .role import load_role


class Core:
    def __init__(self, role_path: str = None, tools: list = None):
        self.dispatcher = ToolDispatcher(tools=tools)
        self.role_prompt = load_role(role_path)
        system_prompt = self.dispatcher.generate_system_prompt(self.role_prompt)
        tools_param = self.dispatcher.generate_tools_param()
        self.llm = LLMClient(system_prompt=system_prompt, tools=tools_param)
        self.history = ChatHistory()

    def run_iter(self, text: str) -> Generator:
        try:
            self.history.add_user(text)

            while True:
                response = self.llm.chat(self.history.get_context())
                reasoning = response.reasoning_content

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
                            reasoning_content=reasoning,
                        )

                        tool_result = self.dispatcher.dispatch(tool_name, params)
                        self.history.add_tool_result(
                            tool_call_id, tool_name, str(tool_result)
                        )

                        yield ToolEvent(
                            tool_name=tool_name,
                            params=params,
                            result=str(tool_result),
                        )
                    continue

                content = response.content or ""
                self.history.add_assistant(content, reasoning)
                yield DoneEvent(content=content)
                return

        except Exception as e:
            yield ErrorEvent(message=str(e))
