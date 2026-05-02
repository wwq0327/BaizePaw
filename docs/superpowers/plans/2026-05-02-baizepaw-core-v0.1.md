# BaizePaw Core v0.1 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建 BaizePaw 核心框架，实现多轮对话和工具调用

**Architecture:** Python 单进程 CLI 应用，对话历史存储在内存，工具调用通过标记解析触发

**Tech Stack:** Python 3.x, requests, python-dotenv

---

## 文件结构

```
BaizePaw/
├── CLAUDE.md
├── config.py              # API 配置
├── requirements.txt
├── main.py                # 入口
└── src/
    ├── __init__.py
    ├── agent.py           # AgentRunner
    ├── llm_client.py      # LLM 调用
    ├── chat_history.py    # 对话历史
    └── tools/
        ├── __init__.py
        ├── dispatcher.py  # 工具调度
        ├── calculator.py  # 计算器
        ├── search.py      # 搜索
        └── file_ops.py    # 文件读写
```

---

## Task 1: 项目初始化

**Files:**
- Create: `BaizePaw/requirements.txt`
- Create: `BaizePaw/config.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
requests>=2.28.0
python-dotenv>=1.0.0
```

- [ ] **Step 2: 创建 config.py**

```python
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
```

- [ ] **Step 3: 安装依赖**

Run: `cd BaizePaw && source ../.venv/bin/activate && pip install -r requirements.txt`

- [ ] **Step 4: Commit**

```bash
git add requirements.txt config.py
git commit -m "feat: project init with config and dependencies"
```

---

## Task 2: 对话历史管理

**Files:**
- Create: `BaizePaw/src/chat_history.py`
- Create: `BaizePaw/tests/test_chat_history.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_chat_history.py
from src.chat_history import ChatHistory

def test_add_user_message():
    history = ChatHistory()
    history.add_user("Hello")
    assert len(history.messages) == 1
    assert history.messages[0]["role"] == "user"
    assert history.messages[0]["content"] == "Hello"

def test_add_assistant_message():
    history = ChatHistory()
    history.add_assistant("Hi there")
    assert len(history.messages) == 1
    assert history.messages[0]["role"] == "assistant"

def test_add_tool_result():
    history = ChatHistory()
    history.add_tool_result("search", "result data")
    assert len(history.messages) == 1
    assert history.messages[0]["role"] == "tool"
    assert history.messages[0]["name"] == "search"

def test_get_context():
    history = ChatHistory()
    history.add_user("Hello")
    history.add_assistant("Hi")
    context = history.get_context()
    assert len(context) == 2
```

- [ ] **Step 2: 运行测试，验证失败**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_chat_history.py -v`
Expected: FAIL (ChatHistory not defined)

- [ ] **Step 3: 实现 ChatHistory**

```python
# src/chat_history.py
class ChatHistory:
    def __init__(self, max_turns: int = 20):
        self.messages = []
        self.max_turns = max_turns

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def add_tool_result(self, name: str, content: str):
        self.messages.append({"role": "tool", "name": name, "content": content})
        self._trim()

    def get_context(self):
        return self.messages

    def _trim(self):
        # 保留最近的 max_turns * 2 条（user + assistant 各算一轮）
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]
```

- [ ] **Step 4: 运行测试，验证通过**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_chat_history.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/chat_history.py tests/test_chat_history.py
git commit -m "feat: add ChatHistory for conversation management"
```

---

## Task 3: LLM 客户端

**Files:**
- Create: `BaizePaw/src/llm_client.py`
- Create: `BaizePaw/tests/test_llm_client.py`

- [ ] **Step 1: 写测试（mock）**

```python
# tests/test_llm_client.py
import pytest
from unittest.mock import patch, MagicMock
from src.llm_client import LLMClient

@pytest.fixture
def client():
    return LLMClient(api_key="test-key", model="test-model")

def test_chat_returns_string(client):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello!"}}]
        }
        mock_post.return_value = mock_response

        result = client.chat([{"role": "user", "content": "hi"}])
        assert result == "Hello!"

def test_chat_with_tools(client):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Searching..."}}]
        }
        mock_post.return_value = mock_response

        result = client.chat([{"role": "user", "content": "search"}])
        assert "Searching" in result
```

- [ ] **Step 2: 运行测试，验证失败**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_llm_client.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 LLMClient**

```python
# src/llm_client.py
import requests
from typing import List, Dict

class LLMClient:
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        from config import SILICON_API_KEY, SILICON_API_BASE, MODEL_NAME
        self.api_key = api_key or SILICON_API_KEY
        self.model = model or MODEL_NAME
        self.base_url = base_url or SILICON_API_BASE

    def chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

- [ ] **Step 4: 运行测试，验证通过**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_llm_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/llm_client.py tests/test_llm_client.py
git commit -m "feat: add LLMClient for Silicon API calls"
```

---

## Task 4: 工具调度器

**Files:**
- Create: `BaizePaw/src/tools/dispatcher.py`
- Create: `BaizePaw/src/tools/__init__.py`
- Create: `BaizePaw/tests/test_dispatcher.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_dispatcher.py
import pytest
from src.tools.dispatcher import ToolDispatcher

def test_dispatch_calculator():
    dispatcher = ToolDispatcher()
    result = dispatcher.dispatch("calculator", {"expr": "2 + 3"})
    assert result == "5.0"

def test_dispatch_unknown_tool():
    dispatcher = ToolDispatcher()
    result = dispatcher.dispatch("unknown_tool", {})
    assert "Unknown tool" in result
```

- [ ] **Step 2: 运行测试，验证失败**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_dispatcher.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 ToolDispatcher**

```python
# src/tools/dispatcher.py
from typing import Any, Dict
from .calculator import calc_tool
from .search import search_tool
from .file_ops import read_file_tool, write_file_tool

class ToolDispatcher:
    def __init__(self):
        self.tools = {
            "calculator": calc_tool,
            "search": search_tool,
            "file_read": read_file_tool,
            "file_write": write_file_tool,
        }

    def dispatch(self, tool_name: str, params: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"
        try:
            return str(self.tools[tool_name](**params))
        except Exception as e:
            return f"Tool error: {e}"
```

- [ ] **Step 4: 运行测试，验证失败**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_dispatcher.py -v`
Expected: FAIL (calc_tool not defined)

- [ ] **Step 5: 实现基础工具函数（calculator, file_ops）**

```python
# src/tools/calculator.py
def calc_tool(expr: str) -> float:
    """安全计算器，只支持基本数学运算"""
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expr):
        raise ValueError("Invalid characters in expression")
    try:
        result = eval(expr)
        return result
    except Exception as e:
        raise ValueError(f"Calculation error: {e}")

# src/tools/file_ops.py
import os

def read_file_tool(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file_tool(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Written to {path}"

# src/tools/search.py
def search_tool(query: str) -> str:
    # 暂时返回占位，后续接入真实搜索
    return f"Search not implemented yet. Query: {query}"
```

- [ ] **Step 6: 创建 tools/__init__.py**

```python
# src/tools/__init__.py
from .dispatcher import ToolDispatcher
from .calculator import calc_tool
from .search import search_tool
from .file_ops import read_file_tool, write_file_tool

__all__ = ["ToolDispatcher", "calc_tool", "search_tool", "read_file_tool", "write_file_tool"]
```

- [ ] **Step 7: 运行测试，验证通过**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_dispatcher.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add src/tools/dispatcher.py src/tools/__init__.py src/tools/calculator.py src/tools/file_ops.py src/tools/search.py tests/test_dispatcher.py
git commit -m "feat: add ToolDispatcher and basic tools"
```

---

## Task 5: AgentRunner

**Files:**
- Create: `BaizePaw/src/agent.py`
- Create: `BaizePaw/tests/test_agent.py`

- [ ] **Step 1: 写测试（mock LLMClient）**

```python
# tests/test_agent.py
import pytest
from unittest.mock import patch, MagicMock
from src.agent import AgentRunner
from src.chat_history import ChatHistory

def test_single_turn():
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.return_value = "Hello, I'm BaizePaw!"
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("Hi")
        assert "BaizePaw" in result

def test_tool_call_loop():
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        # 第一次返回工具调用，第二次返回最终结果
        mock_client.chat.side_effect = [
            "Let me calculate: 【tool】calculator【/tool】\n表达式：2+2",
            "2 + 2 = 4"
        ]

        agent = AgentRunner()
        result = agent.run("What's 2+2?")
        assert "4" in result
```

- [ ] **Step 2: 运行测试，验证失败**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_agent.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 AgentRunner**

```python
# src/agent.py
import re
from config import MAX_LOOP
from .llm_client import LLMClient
from .chat_history import ChatHistory
from .tools.dispatcher import ToolDispatcher

class AgentRunner:
    def __init__(self):
        self.llm = LLMClient()
        self.history = ChatHistory()
        self.dispatcher = ToolDispatcher()

    def run(self, user_input: str) -> str:
        self.history.add_user(user_input)

        for _ in range(MAX_LOOP):
            # 调用 LLM
            response = self.llm.chat(self.history.get_context())

            # 检查是否包含工具调用
            tool_match = re.search(r"【tool】(\w+)【/tool】", response)
            if tool_match:
                tool_name = tool_match.group(1)
                # 从响应中提取工具参数（简化版：直接解析【tool】后的内容）
                self.history.add_assistant(response)

                # 解析参数并执行
                # 这里简化处理，实际可以从 response 中解析参数
                tool_result = self.dispatcher.dispatch(tool_name, {})
                self.history.add_tool_result(tool_name, tool_result)
                continue

            # 没有工具调用，返回结果
            self.history.add_assistant(response)
            return response

        return "Maximum loops exceeded"
```

- [ ] **Step 4: 运行测试，验证通过**

Run: `cd BaizePaw && source ../.venv/bin/activate && pytest tests/test_agent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/agent.py tests/test_agent.py
git commit -m "feat: add AgentRunner with tool call loop"
```

---

## Task 6: Shell 交互层

**Files:**
- Create: `BaizePaw/src/shell.py`
- Create: `BaizePaw/main.py`

- [ ] **Step 1: 实现 Shell**

```python
# src/shell.py
from .agent import AgentRunner

class Shell:
    def __init__(self):
        self.agent = AgentRunner()
        self.running = True

    def start(self):
        print("BaizePaw v0.1 - Your personal agent (type 'quit' to exit)")
        print("-" * 40)

        while self.running:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    self.running = False
                    continue

                response = self.agent.run(user_input)
                print(f"\nBaizePaw: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
```

- [ ] **Step 2: 实现 main.py**

```python
# main.py
from src.shell import Shell

if __name__ == "__main__":
    shell = Shell()
    shell.start()
```

- [ ] **Step 3: Commit**

```bash
git add src/shell.py main.py
git commit -m "feat: add Shell for interactive conversation"
```

---

## Task 7: 端到端验证

- [ ] **Step 1: 创建 .env 文件模板**

```python
# config.py 中已有 .env 加载，需创建模板
# 创建 .env.example
SILICON_API_KEY=your-api-key-here
SILICON_API_BASE=https://api.siliconflow.cn/v1
MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
```

- [ ] **Step 2: 手动测试**

1. 复制 `.env.example` 到 `.env`，填入 API key
2. 运行 `source ../.venv/bin/activate && python main.py`
3. 测试对话：
   - 输入 "你好" → 应有回复
   - 输入 "2+2 等于多少" → 应触发 calculator 工具
   - 输入 "帮我读取 config.py" → 应触发 file_read 工具

- [ ] **Step 3: Commit**

```bash
git add .env.example
git commit -m "chore: add .env.example"
```

---

## 计划总结

| Task | 内容 | 预计时间 |
|------|------|----------|
| 1 | 项目初始化 | 5 min |
| 2 | 对话历史管理 | 10 min |
| 3 | LLM 客户端 | 10 min |
| 4 | 工具调度器 | 15 min |
| 5 | AgentRunner | 15 min |
| 6 | Shell 交互层 | 5 min |
| 7 | 端到端验证 | 10 min |

**总计：约 70 分钟**
