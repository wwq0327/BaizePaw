import json
import re
from typing import Generator

from .chat_history import ChatHistory
from .event import DoneEvent, ErrorEvent, ToolEvent
from .llm_client import LLMClient
from .tools.dispatcher import ToolDispatcher


from .role import load_role


class Core:
    def __init__(self, role_path: str = None, tools: list = None):
        self.dispatcher = ToolDispatcher(tools=tools)
        self.role_prompt = load_role(role_path)
        system_prompt = self.dispatcher.generate_system_prompt(self.role_prompt)
        self.llm = LLMClient(system_prompt=system_prompt)
        self.history = ChatHistory()

    def run_iter(self, text: str) -> Generator:
        try:
            self.history.add_user(text)

            while True:
                response = self.llm.chat(self.history.get_context())
                response_str = str(response)
                reasoning = getattr(response, "reasoning_content", None)

                tool_name, tool_params_str, clean_response = self._extract_tool_call(response_str)

                if tool_name:
                    try:
                        params = json.loads(tool_params_str)
                        if not isinstance(params, dict):
                            raise ValueError("not a dict")
                    except (json.JSONDecodeError, ValueError):
                        params = self._legacy_parse_params(tool_name, tool_params_str)

                    args_json = json.dumps(params, ensure_ascii=False)
                    tool_call_id = self.history.add_tool_call(
                        clean_response, tool_name, args_json, reasoning_content=reasoning
                    )

                    tool_result = self.dispatcher.dispatch(tool_name, params)
                    self.history.add_tool_result(tool_call_id, tool_name, str(tool_result))

                    yield ToolEvent(
                        tool_name=tool_name,
                        params=params,
                        result=str(tool_result),
                    )
                    continue

                clean_response = self._clean_response(response_str)
                self.history.add_assistant(clean_response, reasoning)
                yield DoneEvent(content=clean_response)
                return

        except Exception as e:
            yield ErrorEvent(message=str(e))

    @staticmethod
    def _extract_tool_call(response_str: str):
        """从响应中提取工具调用。返回 (tool_name, params_str, clean_response)。

        支持【tool】格式和 XML / DSML 变体格式。XML 格式会被转换为
        标准【tool】格式后存入 clean_response，避免 XML 污染历史记录。
        """
        # 优先匹配标准格式
        match = re.search(
            r"【tool】(\w+)【/tool】(.+?)(?=【|$)", response_str, re.DOTALL
        )
        if match:
            return match.group(1), match.group(2).strip(), response_str

        # Fallback：匹配 XML / DSML 变体格式（支持多参数）
        invoke_match = re.search(r'invoke\s+name=["\'](\w+)["\']', response_str)
        if invoke_match:
            tool_name = invoke_match.group(1)
            params = {}
            for pm in re.finditer(
                r'parameter\s+name=["\'](\w+)["\'](?:\s+\w+=["\'][^"\']+["\'])?\s*>([^<]+)',
                response_str,
            ):
                params[pm.group(1)] = pm.group(2).strip()
            if params:
                params_json = json.dumps(params, ensure_ascii=False)
                clean = f"【tool】{tool_name}【/tool】{params_json}"
                return tool_name, params_json, clean

        return None, None, response_str

    @staticmethod
    def _clean_response(response_str: str) -> str:
        """过滤掉 content 中的内部标记和垃圾内容。"""
        cleaned = re.sub(r"<\|.*?>", "", response_str)
        cleaned = re.sub(r"</\|.*?>", "", cleaned)
        cleaned = re.sub(r"<tool_call>.*?</tool_call>", "", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"<invoke\b.*?</invoke>", "", cleaned, flags=re.DOTALL)
        return cleaned.strip()

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
