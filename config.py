import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API 配置
# 如果没有单独配置 DEEPSEEK_API_KEY，则使用 SILICONFLOW_API_KEY
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("SILICONFLOW_API_KEY") or ""
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/anthropic")

# 模型配置
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-v4-flash")

# Agent 配置
MAX_LOOP = 10  # 最大循环次数，防止死循环
