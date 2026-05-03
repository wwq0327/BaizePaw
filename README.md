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

- **角色定义** - AGENT.md 独立管理角色定位、行为准则和约束
- **多轮对话** - 记住对话上下文，连续聊天
- **工具调用** - LLM 智能触发工具执行
- **TUI 界面** - Textual 驱动的终端界面，支持 Markdown 渲染
- **输入排队** - 处理中可随时输入，自动排队
- **一键复制** - TUI 中按 `y` 复制最后回复到剪贴板
- **插件系统** - Pipeline + Plugin，可扩展
- **文件操作** - 读写、复制、移动、搜索

## 架构

```
TUI / CLI (表现层)
    ↓ submit() / poll()
Conversation (桥接层, worker thread + queue)
    ↓ run_iter()
Core (Pipeline)
    ↓ yield Event
    ChatHistory + LLMClient + ToolDispatcher
```

三层分离：表现层只管 UI，Conversation 管线程和队列，Core 管业务逻辑和 Event 流。

## 快速开始

### 1. 配置 API Key

```bash
export LLM_API_KEY="your-api-key"
```

或创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
# 支持 LLM_API_KEY、SILICONFLOW_API_KEY、DEEPSEEK_API_KEY
```

### 2. 安装依赖

```bash
source ../.venv/bin/activate  # 使用共享虚拟环境
pip install -r requirements.txt
```

### 3. 运行

**TUI 模式（默认）**
```bash
python main.py
```

**CLI 模式**
```bash
python main.py --cli
```

**一键启动**
```bash
./baize
```

## 项目结构

```
BaizePaw/
├── AGENT.md               # 角色定义（使命/能力/约束/风格）
├── src/
│   ├── core.py            # Core 核心循环，yield Event
│   ├── conversation.py    # Conversation 桥接层（worker + queue）
│   ├── pipeline.py        # Plugin 基类 + Pipeline
│   ├── event.py           # Event 体系（ToolEvent/DoneEvent/ErrorEvent）
│   ├── role.py            # 角色加载（load_role）
│   ├── llm_client.py      # LLM API 调用
│   ├── chat_history.py    # 对话历史管理
│   ├── message.py         # 消息类型定义
│   ├── prompts.py         # System prompt fallback
│   ├── shell.py           # CLI 交互
│   ├── tui/
│   │   └── app.py         # Textual TUI
│   ├── agent.py           # [废弃] 旧 Agent，用 Core 替代
│   └── tools/
│       ├── tool_base.py   # Tool 基类
│       ├── dispatcher.py  # 工具分发器
│       ├── calculator.py  # 计算器
│       ├── file_ops.py    # 文件操作
│       └── search.py      # 搜索
├── tests/                 # 单元测试（41 项）
├── config.py              # 配置
├── main.py                # 入口
└── docs/
    ├── devlog/            # 开发日志
    └── adr/               # 架构决策记录
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
- DeepSeek API（Anthropic 兼容接口）
- requests + python-dotenv
- Textual（TUI）

## 角色系统

白泽的角色定义独立于代码，存放在 `AGENT.md` 中，包含四个维度：

- **做什么（使命）** — 帮助用户管理本地文件和完成日常任务
- **能做什么（能力）** — 文件读写、搜索、整理、批量处理
- **不能做什么（约束）** — 安全边界、明确授权、诚实报告
- **沟通风格** — 简洁、上下文感知、出错时解释

修改 AGENT.md 即可调整角色行为，不需改代码。

## 学习资源

本项目记录了从 0 搭建 Agent 的完整过程：

```
docs/
├── development-process.md   # 开发流程总纲
├── devlog/                  # 开发日志
│   ├── TODO.md              # 待办想法
│   ├── v0.1-core-framework.md  # v0.1 开发过程
│   └── v0.2-architecture-redesign.md  # v0.2 架构重设计
├── adr/                     # 架构决策记录
│   ├── 001-why-not-langchain.md
│   ├── 002-custom-tool-format.md
│   ├── 003-why-deepseek.md
│   └── 004-grep-tool.md
└── plans/                   # 实现计划
```

### 亮点

- **没有黑盒**：每一行代码都知道在干什么
- **问题驱动**：踩过的坑、解决方案都有记录
- **循序渐进**：从简单开始，逐步加功能
- **TDD 驱动**：先写测试再写实现，每步验证

## 许可证

MIT
