import os
from dotenv import load_dotenv

load_dotenv()

# 硅基流动 API 配置
SILICON_API_KEY = os.getenv("SILICON_API_KEY") or os.getenv("SILICONFLOW_API_KEY") or ""
SILICON_API_BASE = os.getenv("SILICON_API_BASE", "https://api.siliconflow.cn/v1")

# 模型配置（优先使用 DeepSeek）
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")

# Agent 配置
MAX_LOOP = 10  # 最大循环次数，防止死循环
