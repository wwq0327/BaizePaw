# BaizePaw 项目设计

## 1. 项目概述

**项目名：** BaizePaw（白泽）
**目标：** 从 0 开始搭建一个个人通用 Agent，能够多轮对话、调用工具，逐步成长
**当前版本：** v0.1 — 核心框架，多轮对话 + 工具调用

---

## 2. 整体架构

```
┌─────────────────────────────────────────┐
│              Shell（交互层）              │
│         终端输入 → 回复展示              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            AgentRunner（核心）            │
│  • 多轮对话循环                         │
│  • 工具调用解析与执行                   │
│  • 回复生成                            │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│ 工具1  │   │ 工具2  │   │ 工具3  │
│计算器  │   │文件读写│   │ 搜索   │
└────────┘   └────────┘   └────────┘
```

---

## 3. 核心组件

### 3.1 AgentRunner
- 循环运行：用户输入 → LLM 调用 → 工具解析 → 工具执行 → 返回结果
- 控制最大循环次数（MAX_LOOP=10）
- 工具调用直接返回结果，不强制多轮

### 3.2 ChatHistory
- 管理多轮对话上下文
- 消息结构：`role` + `content`
- 自动 trim 超过 `max_turns` 的旧消息

### 3.3 LLMClient
- 对接 DeepSeek API（v1 endpoint）
- Model: `deepseek-v4-flash`
- System prompt 指导 LLM 使用工具调用格式

### 3.4 ToolDispatcher
- 解析 LLM 输出中的工具调用标记：`【tool】函数名【/tool】参数`
- 根据函数名分发到对应工具函数
- 异常捕获，返回格式化错误

---

## 4. 工具调用格式

### 4.1 LLM 调用格式

LLM 返回示例：
```
【tool】calculator【/tool】2+2
【tool】file_read【/tool】config.py
```

### 4.2 Agent 解析与执行

```python
# 正则匹配
tool_match = re.search(r"【tool】(\w+)【/tool】(.+?)(?=【|$)", response, re.DOTALL)
tool_name = tool_match.group(1)  # e.g., "calculator"
tool_params = tool_match.group(2).strip()  # e.g., "2+2"

# 参数映射
if tool_name == "calculator":
    params = {"expr": tool_params}
elif tool_name in ("file_read", "search"):
    params = {"path": tool_params}
elif tool_name == "file_write":
    params = {"path": path, "content": content}

# 执行
tool_result = dispatcher.dispatch(tool_name, params)
```

---

## 5. 工具清单

| 工具 | 参数 | 功能 | 状态 |
|------|------|------|------|
| `calculator` | `expr` | 安全数学计算 | ✅ 已实现 |
| `file_read` | `path` | 读取本地文件 | ✅ 已实现 |
| `file_write` | `path`, `content` | 写入本地文件 | ✅ 已实现 |
| `search` | `path` | 搜索网络信息 | ⚠️ 占位 |

---

## 6. 文件结构

```
BaizePaw/
├── CLAUDE.md              # 项目规范
├── README.md              # 项目说明
├── config.py              # API 配置
├── main.py                # 入口
├── requirements.txt        # 依赖
├── .env.example           # 环境变量模板
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── agent.py           # AgentRunner
│   ├── llm_client.py      # LLM 调用
│   ├── chat_history.py    # 对话历史
│   ├── shell.py           # 交互界面
│   └── tools/
│       ├── __init__.py
│       ├── dispatcher.py  # 工具调度
│       ├── calculator.py  # 计算器
│       ├── file_ops.py    # 文件读写
│       └── search.py      # 搜索（占位）
└── tests/
    ├── test_agent.py
    ├── test_chat_history.py
    ├── test_dispatcher.py
    └── test_llm_client.py
```

---

## 7. 技术栈

- **语言：** Python 3.x
- **API：** DeepSeek API（`https://api.deepseek.com/v1`）
- **模型：** `deepseek-v4-flash`
- **依赖：** requests、python-dotenv

---

## 8. 版本历史

| 版本 | 日期 | 内容 |
|------|------|------|
| v0.1 | 2026-05-02 | 核心框架：多轮对话 + calculator + file_read |

---

## 9. 成长路线

| 阶段 | 功能 |
|------|------|
| v0.1 | 核心框架、多轮对话、基础工具 |
| v0.2 | 记忆模块（记住用户偏好） |
| v0.3 | 真实搜索接入 |
| v0.4 | 主动建议能力 |
| v0.5 | Web 界面 / 微信接入 |
| ... | 持续迭代 |

---

## 10. 验证方式

```bash
# 运行测试
PYTHONPATH=. pytest -v

# 交互测试
python main.py
# → 输入: 你好
# → 输入: 计算 2+2
# → 输入: 读取 config.py
```
