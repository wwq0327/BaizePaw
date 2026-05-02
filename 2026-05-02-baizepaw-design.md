# BaizePaw 项目设计

## 1. 项目概述

**项目名：** BaizePaw（白泽）
**目标：** 从 0 开始搭建一个个人通用 Agent，能够多轮对话、调用工具，逐步成长
**当前阶段：** v0.1 — 核心框架，能跑能对话

---

## 2. 整体架构

```
Shell（交互层）
    │
    ▼
AgentRunner（循环运行）
    │
    ├── ChatHistory（对话历史管理）
    ├── LLMClient（LLM API 调用）
    └── ToolDispatcher（工具解析与执行）
            │
    ┌───────┼───────┐
    ▼       ▼       ▼
 calculator  search  file_ops
```

---

## 3. 核心组件

### 3.1 AgentRunner
- 循环运行：发送消息 → 调用 LLM → 解析响应 → 执行工具 → 生成回复
- 控制最大循环次数（防止死循环）
- 返回最终回复给用户

### 3.2 ChatHistory
- 管理多轮对话上下文
- 追加用户消息 / 助手消息 / 工具结果
- 可选：限制历史长度避免上下文溢出

### 3.3 LLMClient
- 对接硅基流动 API（国内，本地方便）
- 接收消息列表，返回 LLM 回复
- 支持 function calling 格式（用于工具调用标记）

### 3.4 ToolDispatcher
- 解析 LLM 输出中的工具调用标记：`【tool】函数名【/tool】`
- 根据函数名分发到对应工具函数
- 将工具执行结果插入对话历史

---

## 4. 工具调用格式

LLM 返回示例：
```
好的，我来帮你搜索相关信息。
【tool】search【/tool】
关键词：Claude API 使用教程
```

ToolDispatcher 解析后：
```python
dispatch("search", {"query": "Claude API 使用教程"})
```

---

## 5. 初始工具

| 工具 | 功能 | 实现方式 |
|------|------|----------|
| `calculator` | 执行 Python 数学计算 | `eval()` 安全封装 |
| `search` | 搜索网络信息 | DuckDuckGo API 或 curl |
| `file_read` | 读取本地文件 | 内置 |
| `file_write` | 写入本地文件 | 内置 |

---

## 6. 文件结构

```
baize-paw/
├── CLAUDE.md
├── config.py              # API 配置
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── agent.py           # AgentRunner
│   ├── llm_client.py      # LLM 调用
│   ├── chat_history.py    # 对话历史
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── dispatcher.py  # 工具调度
│   │   ├── calculator.py  # 计算器
│   │   ├── search.py     # 搜索
│   │   └── file_ops.py   # 文件读写
│   └── shell.py           # 命令行交互
└── main.py                # 入口
```

---

## 7. 技术栈

- **语言：** Python 3.x
- **虚拟环境：** `my/.venv` 共享
- **API：** 硅基流动（或其他国内 LLM API）
- **依赖：** requests、python-dotenv

---

## 8. 成长路线（未来扩展）

| 阶段 | 功能 |
|------|------|
| v0.1 | 核心框架、多轮对话、基础工具 |
| v0.2 | 记忆模块（记住用户偏好） |
| v0.3 | 主动建议能力 |
| v0.4 | Web 界面 / 微信接入 |
| ... | 持续迭代 |

---

## 9. 验证方式

启动后：
1. 能接收用户输入
2. 能返回 LLM 回复
3. 触发工具调用时能正确执行并返回结果
4. 多轮对话上下文连贯
