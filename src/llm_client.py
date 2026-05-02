import time
from typing import Dict, List, Optional

import requests

from .prompts import SYSTEM_PROMPT


class LLMClient:
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
        max_retries: int = 2,
        system_prompt: Optional[str] = None,
    ):
        from config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL_NAME

        self.api_key = api_key or LLM_API_KEY
        self.model = model or LLM_MODEL_NAME
        self.base_url = base_url or LLM_API_BASE
        self.max_retries = max_retries
        self.system_prompt = system_prompt

    def chat(self, messages: List[Dict[str, str]], timeout: int = 30) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        system_content = (
            self.system_prompt if self.system_prompt is not None else SYSTEM_PROMPT
        )
        all_messages = [{"role": "system", "content": system_content}] + messages
        payload = {"model": self.model, "messages": all_messages}

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    url, json=payload, headers=headers, timeout=timeout
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

            except requests.exceptions.Timeout:
                last_error = "API 请求超时，请检查网络连接"
            except requests.exceptions.ConnectionError:
                last_error = f"无法连接到 API 服务器：{self.base_url}"
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code
                if status == 401:
                    last_error = "API Key 认证失败，请检查 LLM_API_KEY"
                elif status == 429:
                    last_error = "API 请求过于频繁，请稍后重试"
                else:
                    last_error = f"API 返回错误 {status}：{e.response.text[:200]}"
                break
            except (KeyError, IndexError, ValueError) as e:
                last_error = f"API 返回格式异常：{e}"
                break

            if attempt < self.max_retries:
                wait = 2**attempt
                time.sleep(wait)

        return f"Error: {last_error}"
