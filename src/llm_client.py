import requests
from typing import List, Dict

class LLMClient:
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        from config import SILICON_API_KEY, SILICON_API_BASE, MODEL_NAME
        self.api_key = api_key or SILICON_API_KEY
        self.model = model or MODEL_NAME
        self.base_url = base_url or SILICON_API_BASE

    def chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]