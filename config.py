import os
from dotenv import load_dotenv

load_dotenv()

# 硅基流动 API 配置
SILICON_API_KEY = os.getenv("SILICON_API_KEY", "")
SILICON_API_BASE = os.getenv("SILICON_API_BASE", "https://api.siliconflow.cn/v1")

# 模型配置
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")

# Agent 配置
MAX_LOOP = 10  # 最大循环次数，防止死循环
