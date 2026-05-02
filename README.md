# BaizePaw 白泽

> 从 0 搭建的个人通用 Agent，能多轮对话、调用工具，逐步成长。

## 白泽的由来

白泽是中国古代神话传说中的神兽，出自《山海经》：

> "白泽者，狮身、人面、虎背、九尾，能言人语，通晓万物之情。"

传说黄帝巡游时遇到白泽，白泽将天下鬼神的名字、形状以及驱除方法一一告知黄帝，被视为**通晓万物、无所不知**的神兽。

取名"白泽"，寓意这个 Agent 能够：
- 通晓万物 — 掌握多种工具和能力
- 能言人语 — 自然语言交互
- 乐于助人 — 陪伴成长，持续学习

## 特性

- **多轮对话** - 记住对话上下文，连续聊天
- **工具调用** - LLM 智能触发工具执行
- **安全计算器** - 支持基本数学运算
- **文件读写** - 读取和写入本地文件
- **可扩展** - 易于添加新工具

## 快速开始

### 1. 克隆项目

```bash
cd /path/to/your/code
```

### 2. 配置 API Key

DeepSeek API Key 设置到环境变量：

```bash
export DEEPSEEK_API_KEY="your-api-key"
```

或创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 3. 安装依赖

```bash
source ../.venv/bin/activate  # 使用共享虚拟环境
pip install -r requirements.txt
```

### 4. 运行

```bash
python main.py
```

### 5. 测试对话

```
You: 你好
BaizePaw: 你好！我是白泽...

You: 计算 2+2
BaizePaw: 【calculator】执行结果：4

You: 读取 config.py
BaizePaw: 【file_read】执行结果：import os...
```

## 项目结构

```
BaizePaw/
├── src/
│   ├── agent.py          # Agent 核心循环
│   ├── llm_client.py    # DeepSeek API 调用
│   ├── chat_history.py  # 对话历史管理
│   ├── shell.py         # 命令行交互
│   └── tools/
│       ├── calculator.py    # 计算器
│       ├── file_ops.py      # 文件读写
│       └── search.py       # 搜索（待实现）
├── tests/               # 单元测试
├── config.py            # 配置
└── main.py              # 入口
```

## 工具列表

| 工具 | 用法 | 说明 |
|------|------|------|
| `calculator` | `计算 2+2` | 数学计算 |
| `file_read` | `读取 config.py` | 读取本地文件 |
| `file_write` | `写入 test.txt:内容` | 写入文件 |
| `search` | `搜索 天气` | 网络搜索（待实现）|

## 测试

```bash
PYTHONPATH=. pytest -v
```

## 技术栈

- Python 3.12
- DeepSeek API (deepseek-v4-flash)
- requests + python-dotenv

## 学习资源

本项目记录了从 0 搭建 Agent 的完整过程：

```
docs/
├── devlog/                 # 开发日志
│   └── v0.1-core-framework.md   # v0.1 开发过程
├── adr/                    # 架构决策记录
│   ├── 001-why-not-langchain.md  # 为什么不用 LangChain
│   ├── 002-custom-tool-format.md  # 为什么自创工具格式
│   └── 003-why-deepseek.md       # 为什么选 DeepSeek
└── plans/                  # 实现计划
    └── 2026-05-02-baizepaw-core-v0.1.md
```

### 亮点

- **没有黑盒**：每一行代码都知道在干什么
- **问题驱动**：踩过的坑、解决方案都有记录
- **循序渐进**：从简单开始，逐步加功能

## 许可证

MIT
