import os
from dotenv import load_dotenv

load_dotenv()

# LLM API 配置
# 优先使用 LLM_API_KEY，依次回退 SILICONFLOW_API_KEY / DEEPSEEK_API_KEY
LLM_API_KEY = (
    os.getenv("LLM_API_KEY")
    or os.getenv("SILICONFLOW_API_KEY")
    or os.getenv("DEEPSEEK_API_KEY")
    or ""
)
# 硅基流动 API，也兼容 DeepSeek 官方 API（需改为 https://api.deepseek.com/v1）
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")

# 模型配置
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", os.getenv("MODEL_NAME", "deepseek-chat"))

# Agent 配置
MAX_LOOP = 10  # 最大循环次数，防止死循环
