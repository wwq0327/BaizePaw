# BaizePaw

## 目标
从 0 搭建一个个人通用 Agent，能多轮对话、调用工具，逐步成长。

## 技术栈
- Python 3.x
- 共享虚拟环境：`my/.venv`
- API：硅基流动（国内 LLM API）
- 依赖：requests、python-dotenv

## 启动方式
```bash
cd BaizePaw
source ../.venv/bin/activate
python main.py
```

## 测试
```bash
cd BaizePaw
source ../.venv/bin/activate
PYTHONPATH=. pytest -v
```

## 验证方式
1. 启动后能接收输入
2. 能返回 LLM 回复
3. 触发工具调用时能正确执行并返回结果
4. 多轮对话上下文连贯
