import requests
from typing import List, Dict

# System prompt that instructs the LLM to use tools
SYSTEM_PROMPT = """你叫白泽（BaizePaw），是一个个人助手。

当你需要完成具体任务时，请使用以下工具格式：
- 计算：直接给出数学表达式的结果
- 搜索信息：使用【tool】search【/tool】后跟搜索关键词
- 读取文件：使用【tool】file_read【/tool】后跟文件路径
- 写入文件：使用【tool】file_write【/tool】后跟文件路径和内容

格式示例：
「帮我计算 2+2」→ 【tool】calculator【/tool】2+2
「搜索天气」→ 【tool】search【/tool】天气
「读取 config.py」→ 【tool】file_read【/tool】config.py

如果不需要工具，直接回答。"""

class LLMClient:
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        from config import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE, MODEL_NAME
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.model = model or MODEL_NAME
        self.base_url = base_url or DEEPSEEK_API_BASE

    def chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Insert system prompt at the beginning
        all_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        payload = {
            "model": self.model,
            "messages": all_messages
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]