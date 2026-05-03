# DEPRECATED: Use src.core.Core instead. This module will be removed in v0.3.
import json
import re
from .llm_client import LLMClient
from .chat_history import ChatHistory
from .tools.dispatcher import ToolDispatcher


class AgentRunner:
    def __init__(self):
        self.dispatcher = ToolDispatcher()
        system_prompt = self.dispatcher.generate_system_prompt()
        self.llm = LLMClient(system_prompt=system_prompt)
        self.history = ChatHistory()

    def run(self, user_input: str) -> str:
        self.history.add_user(user_input)

        while True:
            response = self.llm.chat(self.history.get_context())

            # 匹配格式：【tool】toolname【/tool】参数
            tool_match = re.search(
                r"【tool】(\w+)【/tool】(.+?)(?=【|$)", response, re.DOTALL
            )
            if tool_match:
                tool_name = tool_match.group(1)
                tool_params_str = tool_match.group(2).strip()

                # 优先 JSON 解析，失败则走旧格式兼容
                try:
                    params = json.loads(tool_params_str)
                    if not isinstance(params, dict):
                        raise ValueError("not a dict")
                except (json.JSONDecodeError, ValueError):
                    params = self._legacy_parse_params(tool_name, tool_params_str)

                # 记录 assistant 消息（含 tool_calls）
                args_json = json.dumps(params, ensure_ascii=False)
                tool_call_id = self.history.add_tool_call(
                    response, tool_name, args_json
                )

                # 执行工具，结果用 tool role 单独发送
                tool_result = self.dispatcher.dispatch(tool_name, params)
                self.history.add_tool_result(tool_call_id, tool_name, str(tool_result))
                continue

            self.history.add_assistant(response)
            return response

    @staticmethod
    def _legacy_parse_params(tool_name: str, params_str: str) -> dict:
        """旧格式参数解析（兼容非 JSON 调用）"""
        if not params_str:
            return {}
        if tool_name == "calculator":
            return {"expr": params_str}
        elif tool_name in (
            "file_read",
            "delete_file",
            "list_dir",
        ):
            return {"path": params_str}
        elif tool_name in ("find_file", "grep_file"):
            parts = params_str.split(" in ", 1)
            if len(parts) > 1:
                return {
                    "pattern": parts[0].strip(),
                    "path": parts[1].strip(),
                }
            return {"pattern": params_str}
        elif tool_name in ("move_file", "copy_file"):
            parts = params_str.split("->", 1)
            if len(parts) > 1:
                return {"src": parts[0].strip(), "dst": parts[1].strip()}
            return {"src": params_str, "dst": params_str}
        elif tool_name in ("file_write", "file_append"):
            parts = params_str.split(":", 1)
            if len(parts) > 1:
                return {
                    "path": parts[0].strip(),
                    "content": parts[1].strip(),
                }
            return {"path": params_str}
        elif tool_name == "search":
            return {"query": params_str}
        else:
            return {"input": params_str}
