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

```bash
export LLM_API_KEY="your-api-key"
```

或创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
# 支持 LLM_API_KEY、SILICONFLOW_API_KEY、DEEPSEEK_API_KEY
```

### 3. 安装依赖

```bash
source ../.venv/bin/activate  # 使用共享虚拟环境
pip install -r requirements.txt
```

### 4. 运行

**方式一：一键启动（推荐）**
```bash
./baize
```

**方式二：手动启动**
```bash
source ../.venv/bin/activate
python main.py
```

### 5. 测试对话

```
You: 你好
BaizePaw: 你好！我是白泽...

You: 计算 2+2
BaizePaw: 2 + 2 = 4

You: 读取 config.py
BaizePaw: config.py 的内容是...
```

## 项目结构

```
BaizePaw/
├── src/
│   ├── agent.py          # Agent 核心循环
│   ├── llm_client.py    # LLM API 调用
│   ├── chat_history.py  # 对话历史管理
│   ├── prompts.py       # System prompt
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
| `file_append` | `追加 test.txt:内容` | 追加内容到文件 |
| `copy_file` | `复制 a.txt -> b.txt` | 复制文件 |
| `list_dir` | `查看目录` | 列出目录内容 |
| `find_file` | `查找 *.py` | 搜索文件名 |
| `grep_file` | `在 src 搜索 xxx` | 搜索文件内容，支持正则 |
| `delete_file` | `删除 test.txt` | 删除文件 |
| `move_file` | `移动 old.txt -> new.txt` | 移动/重命名文件 |
| `search` | `搜索 天气` | 网络搜索（待实现）|

## 测试

```bash
PYTHONPATH=. pytest -v
```

## 技术栈

- Python 3.12
- 硅基流动 / DeepSeek API
- requests + python-dotenv

## 学习资源

本项目记录了从 0 搭建 Agent 的完整过程：

```
docs/
├── development-process.md   # 开发流程总纲
├── devlog/                 # 开发日志
│   ├── TODO.md             # 待办想法
│   └── v0.1-core-framework.md   # v0.1 开发过程
├── adr/                    # 架构决策记录
│   ├── 001-why-not-langchain.md  # 为什么不用 LangChain
│   ├── 002-custom-tool-format.md  # 为什么自创工具格式
│   ├── 003-why-deepseek.md       # 为什么选 DeepSeek
│   └── 004-grep-tool.md          # grep 工具方案
└── superpowers/            # 高阶功能计划
```

### 亮点

- **没有黑盒**：每一行代码都知道在干什么
- **问题驱动**：踩过的坑、解决方案都有记录
- **循序渐进**：从简单开始，逐步加功能

## 许可证

MIT
