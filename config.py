import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API（Anthropic 兼容接口）
LLM_API_KEY = (
    os.getenv("LLM_API_KEY")
    or os.getenv("DEEPSEEK_API_KEY")
    or ""
)
LLM_API_BASE = os.getenv("LLM_API_BASE", os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"))

# 模型配置
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", os.getenv("MODEL_NAME", "deepseek-v4-flash"))

# Agent 配置
MAX_LOOP = 10  # 最大循环次数，防止死循环
