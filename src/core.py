import json
import re
from typing import Generator

from .chat_history import ChatHistory
from .event import DoneEvent, ErrorEvent, ToolEvent
from .llm_client import LLMClient
from .tools.dispatcher import ToolDispatcher


class Core:
    def __init__(self):
        self.dispatcher = ToolDispatcher()
        system_prompt = self.dispatcher.generate_system_prompt()
        self.llm = LLMClient(system_prompt=system_prompt)
        self.history = ChatHistory()

    def run_iter(self, text: str) -> Generator:
        try:
            self.history.add_user(text)

            while True:
                response = self.llm.chat(self.history.get_context())

                tool_match = re.search(
                    r"【tool】(\w+)【/tool】(.+?)(?=【|$)", response, re.DOTALL
                )
                if tool_match:
                    tool_name = tool_match.group(1)
                    tool_params_str = tool_match.group(2).strip()

                    try:
                        params = json.loads(tool_params_str)
                        if not isinstance(params, dict):
                            raise ValueError("not a dict")
                    except (json.JSONDecodeError, ValueError):
                        params = self._legacy_parse_params(tool_name, tool_params_str)

                    args_json = json.dumps(params, ensure_ascii=False)
                    tool_call_id = self.history.add_tool_call(
                        response, tool_name, args_json
                    )

                    tool_result = self.dispatcher.dispatch(tool_name, params)
                    self.history.add_tool_result(tool_call_id, tool_name, str(tool_result))

                    yield ToolEvent(
                        tool_name=tool_name,
                        params=params,
                        result=str(tool_result),
                    )
                    continue

                self.history.add_assistant(response)
                yield DoneEvent(content=response)
                return

        except Exception as e:
            yield ErrorEvent(message=str(e))

    @staticmethod
    def _legacy_parse_params(tool_name: str, params_str: str) -> dict:
        if not params_str:
            return {}
        if tool_name == "calculator":
            return {"expr": params_str}
        elif tool_name in ("file_read", "delete_file", "list_dir"):
            return {"path": params_str}
        elif tool_name in ("find_file", "grep_file"):
            parts = params_str.split(" in ", 1)
            if len(parts) > 1:
                return {"pattern": parts[0].strip(), "path": parts[1].strip()}
            return {"pattern": params_str}
        elif tool_name in ("move_file", "copy_file"):
            parts = params_str.split("->", 1)
            if len(parts) > 1:
                return {"src": parts[0].strip(), "dst": parts[1].strip()}
            return {"src": params_str, "dst": params_str}
        elif tool_name in ("file_write", "file_append"):
            parts = params_str.split(":", 1)
            if len(parts) > 1:
                return {"path": parts[0].strip(), "content": parts[1].strip()}
            return {"path": params_str}
        elif tool_name == "search":
            return {"query": params_str}
        else:
            return {"input": params_str}
