# Function Calling 标准化 迁移计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将工具调用从自定义 DSML 文本标记迁移到 OpenAI 标准 function calling API，删除正则解析链，提升鲁棒性。

**Architecture:** LLMClient.chat() 新增 `tools` 参数，payload 传 `tools` 字段，响应从 `response.tool_calls` 结构化字段取工具调用。Core.run_iter() 直接迭代 `tool_calls`，删除 `_extract_tool_call` / `_clean_response` / `_legacy_parse_params` 三层 fallback。ToolDispatcher 新增 `generate_tools_param()` 将已注册工具序列化为 OpenAI tools 格式。

**Tech Stack:** Python 3.x, DeepSeek OpenAI-compatible API (`/chat/completions`), pytest

---

## File Structure

| 文件 | 改动类型 | 职责 |
|------|----------|------|
| `src/llm_client.py` | 修改 | ChatResponse 加 tool_calls 字段；LLMClient 接受 tools 参数；修复错误时返回类型不一致 |
| `src/core.py` | 修改 | run_iter() 从 response.tool_calls 取调用；删 3 个 fallback 方法；__init__ 传 tools 给 LLMClient |
| `src/agent.py` | 修改 | 同 Core 模式改 run()；删 _legacy_parse_params |
| `src/tools/dispatcher.py` | 修改 | 新增 generate_tools_param()；简化 generate_system_prompt() |
| `src/message.py` | 修改 | ToolCallMessage.content 改 Optional[str] |
| `src/chat_history.py` | 修改 | add_tool_call 加 tool_call_id 参数 |
| `tests/test_core.py` | 修改 | mock 数据改 ChatResponse；删 4 个 DSML/XML 测试；新增多工具调用测试 |
| `tests/test_agent.py` | 修改 | mock 数据改 ChatResponse；删 legacy 测试 |
| `tests/test_dispatcher.py` | 修改 | 删格式禁止测试；新增 generate_tools_param 测试 |
| `tests/test_chat_history.py` | 修改 | content 参数改 None |
| `tests/test_coach.py` | 修改 | mock 数据改 ChatResponse |
| `tests/test_ingest_e2e.py` | 修改 | mock 数据改 ChatResponse |

---

### Task 1: ToolDispatcher.generate_tools_param()

**Files:**
- Modify: `src/tools/dispatcher.py:33-81`
- Test: `tests/test_dispatcher.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_dispatcher.py` 末尾添加：

```python
def test_generate_tools_param_returns_openai_format():
    dispatcher = ToolDispatcher()
    tools_param = dispatcher.generate_tools_param()
    assert isinstance(tools_param, list)
    assert len(tools_param) > 0
    first = tools_param[0]
    assert first["type"] == "function"
    assert "name" in first["function"]
    assert "description" in first["function"]
    assert "parameters" in first["function"]


def test_generate_tools_param_matches_registered_tools():
    from src.tools.tool_base import Tool

    custom = Tool(
        name="my_tool",
        description="Does something",
        parameters={
            "type": "object",
            "properties": {"x": {"type": "string", "description": "input"}},
            "required": ["x"],
        },
        fn=lambda x: x,
    )
    dispatcher = ToolDispatcher(tools=[custom])
    tools_param = dispatcher.generate_tools_param()
    assert len(tools_param) == 1
    assert tools_param[0]["function"]["name"] == "my_tool"
    assert tools_param[0]["function"]["description"] == "Does something"
    assert tools_param[0]["function"]["parameters"]["required"] == ["x"]
```

- [ ] **Step 2: 跑测试确认 FAIL**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_dispatcher.py::test_generate_tools_param_returns_openai_format tests/test_dispatcher.py::test_generate_tools_param_matches_registered_tools -v`
Expected: FAIL — `AttributeError: 'ToolDispatcher' object has no attribute 'generate_tools_param'`

- [ ] **Step 3: 实现 generate_tools_param()**

在 `src/tools/dispatcher.py` 的 `ToolDispatcher` 类中，`dispatch` 方法之后添加：

```python
def generate_tools_param(self) -> list:
    """将已注册工具序列化为 OpenAI function calling tools 格式。"""
    tools = []
    for tool in self.tools.values():
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
        )
    return tools
```

- [ ] **Step 4: 跑测试确认 PASS**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_dispatcher.py::test_generate_tools_param_returns_openai_format tests/test_dispatcher.py::test_generate_tools_param_matches_registered_tools -v`
Expected: PASS

- [ ] **Step 5: 跑全量测试确认无回归**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest -v`
Expected: 全部 PASS

- [ ] **Step 6: Commit**

```bash
git add src/tools/dispatcher.py tests/test_dispatcher.py
git commit -m "feat: add ToolDispatcher.generate_tools_param() for OpenAI tools format"
```

---

### Task 2: ChatResponse + LLMClient tool_calls 支持

**Files:**
- Modify: `src/llm_client.py:10-83`
- Test: `tests/test_core.py`（在此 Task 中只验证 ChatResponse 本身，Core 集成测试在 Task 4）

- [ ] **Step 1: 写失败测试**

在 `tests/test_core.py` 末尾添加：

```python
from src.llm_client import ChatResponse


def test_chat_response_with_tool_calls():
    tc = {
        "id": "call_1",
        "type": "function",
        "function": {"name": "calculator", "arguments": '{"expr": "2+2"}'},
    }
    resp = ChatResponse(content=None, tool_calls=[tc])
    assert resp.content is None
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0]["function"]["name"] == "calculator"
    assert str(resp) == ""


def test_chat_response_without_tool_calls():
    resp = ChatResponse(content="Hello!", tool_calls=None)
    assert resp.content == "Hello!"
    assert resp.tool_calls is None
    assert str(resp) == "Hello!"
```

- [ ] **Step 2: 跑测试确认 FAIL**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_core.py::test_chat_response_with_tool_calls tests/test_core.py::test_chat_response_without_tool_calls -v`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'tool_calls'`

- [ ] **Step 3: 实现 ChatResponse 改动**

修改 `src/llm_client.py`：

```python
@dataclass
class ChatResponse:
    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None

    def __str__(self):
        return self.content or ""
```

- [ ] **Step 4: 修改 LLMClient.chat()**

修改 `src/llm_client.py` 中 `LLMClient` 类：

`__init__` 加 `tools` 参数：

```python
def __init__(
    self,
    api_key: str = None,
    model: str = None,
    base_url: str = None,
    max_retries: int = 2,
    system_prompt: Optional[str] = None,
    tools: Optional[List[Dict]] = None,
):
    from config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL_NAME

    self.api_key = api_key or LLM_API_KEY
    self.model = model or LLM_MODEL_NAME
    self.base_url = base_url or LLM_API_BASE
    self.max_retries = max_retries
    self.system_prompt = system_prompt
    self.tools = tools
```

`chat()` 方法签名改为返回 `ChatResponse`，payload 加 `tools`，解析 `tool_calls`：

```python
def chat(self, messages: List[Dict], timeout: int = 30) -> ChatResponse:
    url = f"{self.base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json",
    }
    system_content = (
        self.system_prompt if self.system_prompt is not None else SYSTEM_PROMPT
    )
    all_messages = [{"role": "system", "content": system_content}] + messages
    payload = {"model": self.model, "messages": all_messages}
    if self.tools:
        payload["tools"] = self.tools

    last_error = None
    for attempt in range(self.max_retries + 1):
        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            msg = data["choices"][0]["message"]
            return ChatResponse(
                content=msg.get("content"),
                reasoning_content=msg.get("reasoning_content"),
                tool_calls=msg.get("tool_calls"),
            )

        except requests.exceptions.Timeout:
            last_error = "API 请求超时，请检查网络连接"
        except requests.exceptions.ConnectionError:
            last_error = f"无法连接到 API 服务器：{self.base_url}"
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status == 401:
                last_error = "API Key 认证失败，请检查 LLM_API_KEY"
            elif status == 429:
                last_error = "API 请求过于频繁，请稍后重试"
            else:
                last_error = f"API 返回错误 {status}：{e.response.text[:200]}"
            break
        except (KeyError, IndexError, ValueError) as e:
            last_error = f"API 返回格式异常：{e}"
            break

        if attempt < self.max_retries:
            wait = 2**attempt
            time.sleep(wait)

    return ChatResponse(content=f"Error: {last_error}")
```

注意：错误路径也返回 `ChatResponse` 而非字符串，修复了原有的返回类型不一致问题。

- [ ] **Step 5: 跑测试确认 PASS**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_core.py::test_chat_response_with_tool_calls tests/test_core.py::test_chat_response_without_tool_calls -v`
Expected: PASS

- [ ] **Step 6: 跑全量测试确认无回归**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest -v`
Expected: 全部 PASS（现有代码通过 `str(response)` 和 `getattr` 访问 ChatResponse，新默认值 `tool_calls=None` 和 `content=None` 不影响现有行为）

- [ ] **Step 7: Commit**

```bash
git add src/llm_client.py tests/test_core.py
git commit -m "feat: add tool_calls support to ChatResponse and LLMClient"
```

---

### Task 3: ToolCallMessage + ChatHistory — Optional content + tool_call_id

**Files:**
- Modify: `src/message.py:29-67`
- Modify: `src/chat_history.py:22-26`
- Test: `tests/test_chat_history.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_chat_history.py` 末尾添加：

```python
def test_add_tool_call_with_api_provided_id():
    history = ChatHistory()
    tool_call_id = history.add_tool_call(
        None, "calculator", '{"expr": "2+2"}', tool_call_id="call_abc123"
    )
    assert tool_call_id == "call_abc123"
    assert isinstance(history.messages[0], ToolCallMessage)
    assert history.messages[0].content is None


def test_tool_call_message_content_none_in_dict():
    history = ChatHistory()
    history.add_tool_call(
        None, "calculator", '{"expr": "2+2"}', tool_call_id="call_1"
    )
    context = history.get_context()
    assert context[0]["content"] is None
    assert context[0]["tool_calls"][0]["id"] == "call_1"
```

- [ ] **Step 2: 跑测试确认 FAIL**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_chat_history.py::test_add_tool_call_with_api_provided_id tests/test_chat_history.py::test_tool_call_message_content_none_in_dict -v`
Expected: FAIL — `TypeError: add_tool_call() got an unexpected keyword argument 'tool_call_id'`

- [ ] **Step 3: 实现 ToolCallMessage.content 改 Optional**

修改 `src/message.py` 中 `ToolCallMessage.__init__` 签名：

```python
class ToolCallMessage:
    role = "assistant"

    def __init__(
        self,
        content: Optional[str],
        tool_name: str,
        arguments: str,
        tool_call_id: Optional[str] = None,
        reasoning_content: Optional[str] = None,
    ):
        self.content = content
        self.tool_name = tool_name
        self.arguments = arguments
        self._tool_call_id = tool_call_id or str(uuid.uuid4())
        self.reasoning_content = reasoning_content
```

`to_dict()` 不需要改，`self.content` 为 `None` 时自然输出 `"content": None`。

- [ ] **Step 4: 实现 ChatHistory.add_tool_call 加 tool_call_id 参数**

修改 `src/chat_history.py:22-26`：

```python
def add_tool_call(self, content: Optional[str], tool_name: str, arguments: str, reasoning_content: str = None, tool_call_id: str = None) -> str:
    msg = ToolCallMessage(content, tool_name, arguments, tool_call_id=tool_call_id, reasoning_content=reasoning_content)
    self.messages.append(msg)
    self._trim()
    return msg.tool_call_id
```

需要在文件头部导入 `Optional`：

```python
from typing import Optional
```

- [ ] **Step 5: 跑测试确认 PASS**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_chat_history.py::test_add_tool_call_with_api_provided_id tests/test_chat_history.py::test_tool_call_message_content_none_in_dict -v`
Expected: PASS

- [ ] **Step 6: 更新 test_chat_history.py 中旧测试的 content 参数**

修改 `tests/test_chat_history.py` 中三个旧测试，将 `content` 从 DSML 字符串改为 `None`：

```python
def test_add_tool_call_and_result():
    history = ChatHistory()
    tool_call_id = history.add_tool_call(
        None, "calculator", '{"expr": "2+2"}'
    )
    # ... 其余不变
```

```python
def test_tool_call_with_reasoning_content():
    history = ChatHistory()
    history.add_tool_call(
        None,
        "calculator",
        '{"expr": "2+2"}',
        reasoning_content="Let me calculate...",
    )
    # ... 其余不变
```

```python
def test_tool_call_without_reasoning_content():
    history = ChatHistory()
    history.add_tool_call(
        None,
        "calculator",
        '{"expr": "2+2"}',
    )
    # ... 其余不变
```

- [ ] **Step 7: 跑全量测试确认无回归**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest -v`
Expected: 全部 PASS

- [ ] **Step 8: Commit**

```bash
git add src/message.py src/chat_history.py tests/test_chat_history.py
git commit -m "feat: support Optional content and API-provided tool_call_id in ToolCallMessage"
```

---

### Task 4: Core.run_iter() 重写

**Files:**
- Modify: `src/core.py:1-141`
- Test: `tests/test_core.py`

这是核心改动。先更新测试，再改实现。

- [ ] **Step 1: 重写 test_core.py**

整个文件替换为：

```python
from unittest.mock import MagicMock, patch

from src.core import Core
from src.event import DoneEvent, ErrorEvent, ToolEvent
from src.llm_client import ChatResponse


def _tool_call(name, arguments, call_id=None):
    """构造 OpenAI tool_calls 条目。"""
    return {
        "id": call_id or f"call_{name}",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def _make_core(mock_client):
    with patch("src.core.LLMClient", return_value=mock_client):
        return Core()


def test_no_tool_yields_done():
    mock_client = MagicMock()
    mock_client.chat.return_value = ChatResponse(content="Hello!")
    core = _make_core(mock_client)

    events = list(core.run_iter("Hi"))
    assert len(events) == 1
    assert isinstance(events[0], DoneEvent)
    assert events[0].content == "Hello!"


def test_tool_then_done():
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        ChatResponse(
            content=None,
            tool_calls=[_tool_call("calculator", '{"expr": "2+2"}')],
        ),
        ChatResponse(content="The answer is 4"),
    ]
    core = _make_core(mock_client)

    events = list(core.run_iter("calc 2+2"))
    assert len(events) == 2
    assert isinstance(events[0], ToolEvent)
    assert events[0].tool_name == "calculator"
    assert events[0].params == {"expr": "2+2"}
    assert isinstance(events[1], DoneEvent)
    assert "4" in events[1].content


def test_multiple_tool_calls_in_one_response():
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        ChatResponse(
            content=None,
            tool_calls=[
                _tool_call("calculator", '{"expr": "1+1"}'),
                _tool_call("calculator", '{"expr": "2+2"}'),
            ],
        ),
        ChatResponse(content="Done"),
    ]
    core = _make_core(mock_client)

    events = list(core.run_iter("calc"))
    assert len(events) == 3
    assert isinstance(events[0], ToolEvent)
    assert events[0].tool_name == "calculator"
    assert events[0].params == {"expr": "1+1"}
    assert isinstance(events[1], ToolEvent)
    assert events[1].tool_name == "calculator"
    assert events[1].params == {"expr": "2+2"}
    assert isinstance(events[2], DoneEvent)


def test_error_yields_error_event():
    mock_client = MagicMock()
    mock_client.chat.side_effect = Exception("boom")
    core = _make_core(mock_client)

    events = list(core.run_iter("Hi"))
    assert len(events) == 1
    assert isinstance(events[0], ErrorEvent)
    assert "boom" in events[0].message


def test_core_with_custom_role_path():
    import tempfile, os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Custom Role\nBe helpful.")
        role_path = f.name

    try:
        mock_client = MagicMock()
        mock_client.chat.return_value = ChatResponse(content="OK")
        with patch("src.core.LLMClient", return_value=mock_client):
            core = Core(role_path=role_path)
        assert "Custom Role" in core.role_prompt
    finally:
        os.unlink(role_path)


def test_core_with_custom_tools():
    from src.tools.tool_base import Tool

    custom = Tool(
        name="custom",
        description="test",
        parameters={"type": "object", "properties": {}, "required": []},
        fn=lambda: "custom",
    )
    mock_client = MagicMock()
    mock_client.chat.return_value = ChatResponse(content="OK")
    with patch("src.core.LLMClient", return_value=mock_client):
        core = Core(tools=[custom])
    assert "custom" in core.dispatcher.tools
    assert "calculator" not in core.dispatcher.tools


def test_tool_call_id_preserved_in_history():
    mock_client = MagicMock()
    mock_client.chat.side_effect = [
        ChatResponse(
            content=None,
            tool_calls=[_tool_call("calculator", '{"expr": "2+2"}', "call_abc")],
        ),
        ChatResponse(content="Done"),
    ]
    core = _make_core(mock_client)

    list(core.run_iter("calc"))
    from src.message import ToolCallMessage

    tc_msgs = [m for m in core.history.messages if isinstance(m, ToolCallMessage)]
    assert len(tc_msgs) == 1
    assert tc_msgs[0].tool_call_id == "call_abc"
```

- [ ] **Step 2: 跑测试确认 FAIL**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_core.py -v`
Expected: FAIL — 旧实现仍用 DSML 解析，mock 返回的 ChatResponse 无法匹配 `【tool】` 正则

- [ ] **Step 3: 重写 Core.run_iter() 和 __init__**

将 `src/core.py` 整个替换为：

```python
import json
from typing import Generator, Optional

from .chat_history import ChatHistory
from .event import DoneEvent, ErrorEvent, ToolEvent
from .llm_client import ChatResponse, LLMClient
from .tools.dispatcher import ToolDispatcher
from .role import load_role


class Core:
    def __init__(self, role_path: str = None, tools: list = None):
        self.dispatcher = ToolDispatcher(tools=tools)
        self.role_prompt = load_role(role_path)
        system_prompt = self.dispatcher.generate_system_prompt(self.role_prompt)
        tools_param = self.dispatcher.generate_tools_param()
        self.llm = LLMClient(system_prompt=system_prompt, tools=tools_param)
        self.history = ChatHistory()

    def run_iter(self, text: str) -> Generator:
        try:
            self.history.add_user(text)

            while True:
                response = self.llm.chat(self.history.get_context())
                reasoning = response.reasoning_content

                if response.tool_calls:
                    for tc in response.tool_calls:
                        tool_call_id = tc["id"]
                        tool_name = tc["function"]["name"]
                        args_json = tc["function"]["arguments"]
                        params = json.loads(args_json)

                        self.history.add_tool_call(
                            response.content,
                            tool_name,
                            args_json,
                            tool_call_id=tool_call_id,
                            reasoning_content=reasoning,
                        )

                        tool_result = self.dispatcher.dispatch(tool_name, params)
                        self.history.add_tool_result(
                            tool_call_id, tool_name, str(tool_result)
                        )

                        yield ToolEvent(
                            tool_name=tool_name,
                            params=params,
                            result=str(tool_result),
                        )
                    continue

                content = response.content or ""
                self.history.add_assistant(content, reasoning)
                yield DoneEvent(content=content)
                return

        except Exception as e:
            yield ErrorEvent(message=str(e))
```

注意：`_extract_tool_call`、`_clean_response`、`_legacy_parse_params` 三个方法已删除。`import re` 也移除。

- [ ] **Step 4: 跑测试确认 PASS**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_core.py -v`
Expected: PASS

- [ ] **Step 5: 跑全量测试确认无回归**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest -v`
Expected: test_agent.py 和 test_coach.py 会 FAIL（mock 数据仍是 DSML 字符串），其余 PASS。这是预期的，后续 Task 修复。

- [ ] **Step 6: Commit**

```bash
git add src/core.py tests/test_core.py
git commit -m "feat: rewrite Core.run_iter() to use OpenAI function calling API"
```

---

### Task 5: 简化 generate_system_prompt()

**Files:**
- Modify: `src/tools/dispatcher.py:54-81`
- Test: `tests/test_dispatcher.py`

- [ ] **Step 1: 更新 test_dispatcher.py**

删除 `test_system_prompt_forbids_xml_format`（第 78-82 行），修改 `test_generate_system_prompt_without_role` 删除对 `【tool】` 的断言：

```python
def test_generate_system_prompt_without_role():
    """不传 role_prompt 时从 load_role 读取，prompt 应包含角色内容"""
    dispatcher = ToolDispatcher()
    prompt = dispatcher.generate_system_prompt()
    assert "白泽" in prompt
    assert "## 1. 做什么" in prompt
```

- [ ] **Step 2: 跑测试确认 FAIL**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_dispatcher.py::test_generate_system_prompt_without_role -v`
Expected: 可能 PASS（取决于断言是否还在），但确认 `test_system_prompt_forbids_xml_format` 已删除

- [ ] **Step 3: 简化 generate_system_prompt()**

修改 `src/tools/dispatcher.py` 中 `generate_system_prompt` 方法，删除 DSML 格式约束部分：

```python
def generate_system_prompt(self, role_prompt: str = None) -> str:
    if role_prompt is None:
        from ..role import load_role
        role_prompt = load_role()
    lines = [role_prompt, "", "---", "", "可用工具："]
    for tool in self.tools.values():
        props = tool.parameters.get("properties", {})
        required = tool.parameters.get("required", [])
        param_parts = []
        for name, schema in props.items():
            desc = schema.get("description", name)
            hint = "（必需）" if name in required else "（可选）"
            param_parts.append(f"{name}{hint} — {desc}")
        lines.append(
            f"- {tool.name}：{tool.description}。参数：{'，'.join(param_parts)}"
        )
    return "\n".join(lines)
```

删除了原来的 `使用格式：【tool】...` 和 `重要约束` 两个 block（共 8 行）。工具描述保留作为 LLM 的参考信息。

- [ ] **Step 4: 跑全量测试**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_dispatcher.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/tools/dispatcher.py tests/test_dispatcher.py
git commit -m "refactor: simplify generate_system_prompt() by removing DSML format instructions"
```

---

### Task 6: AgentRunner 更新

**Files:**
- Modify: `src/agent.py:1-89`
- Test: `tests/test_agent.py`

- [ ] **Step 1: 重写 test_agent.py**

整个文件替换为：

```python
import pytest
from unittest.mock import patch, MagicMock
from src.agent import AgentRunner
from src.llm_client import ChatResponse


def _tool_call(name, arguments, call_id=None):
    return {
        "id": call_id or f"call_{name}",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def test_single_turn():
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.return_value = ChatResponse(content="Hello, I'm BaizePaw!")
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("Hi")
        assert "BaizePaw" in result


def test_tool_call_with_json_params():
    """LLM 返回标准 function calling 工具调用"""
    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            ChatResponse(
                content=None,
                tool_calls=[_tool_call("calculator", '{"expr": "2+2"}')],
            ),
            ChatResponse(content="2 + 2 = 4"),
        ]
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        result = agent.run("What's 2+2?")
        assert "4" in result


def test_tool_result_uses_tool_role():
    """工具结果用 tool role 发送，不混在 user 里"""
    from src.message import ToolResultMessage, UserMessage

    with patch("src.agent.LLMClient") as MockLLM:
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            ChatResponse(
                content=None,
                tool_calls=[_tool_call("calculator", '{"expr": "2+2"}')],
            ),
            ChatResponse(content="4"),
        ]
        MockLLM.return_value = mock_client

        agent = AgentRunner()
        agent.run("calc")

        tool_msgs = [
            m for m in agent.history.messages if isinstance(m, ToolResultMessage)
        ]
        assert len(tool_msgs) == 1
        assert tool_msgs[0].name == "calculator"

        user_msgs = [m for m in agent.history.messages if isinstance(m, UserMessage)]
        assert not any(m.content.startswith("工具「") for m in user_msgs)
```

- [ ] **Step 2: 跑测试确认 FAIL**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_agent.py -v`
Expected: FAIL — 旧 AgentRunner 仍用正则解析

- [ ] **Step 3: 重写 AgentRunner**

将 `src/agent.py` 整个替换为：

```python
# DEPRECATED: Use src.core.Core instead. This module will be removed in v0.3.
import json
from .llm_client import LLMClient
from .chat_history import ChatHistory
from .tools.dispatcher import ToolDispatcher


class AgentRunner:
    def __init__(self):
        self.dispatcher = ToolDispatcher()
        system_prompt = self.dispatcher.generate_system_prompt()
        tools_param = self.dispatcher.generate_tools_param()
        self.llm = LLMClient(system_prompt=system_prompt, tools=tools_param)
        self.history = ChatHistory()

    def run(self, user_input: str) -> str:
        self.history.add_user(user_input)

        while True:
            response = self.llm.chat(self.history.get_context())

            if response.tool_calls:
                for tc in response.tool_calls:
                    tool_call_id = tc["id"]
                    tool_name = tc["function"]["name"]
                    args_json = tc["function"]["arguments"]
                    params = json.loads(args_json)

                    self.history.add_tool_call(
                        response.content,
                        tool_name,
                        args_json,
                        tool_call_id=tool_call_id,
                    )

                    tool_result = self.dispatcher.dispatch(tool_name, params)
                    self.history.add_tool_result(
                        tool_call_id, tool_name, str(tool_result)
                    )
                continue

            content = response.content or ""
            self.history.add_assistant(content)
            return content
```

`_legacy_parse_params`、`import re`、正则匹配全部删除。

- [ ] **Step 4: 跑测试确认 PASS**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest tests/test_agent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/agent.py tests/test_agent.py
git commit -m "feat: rewrite AgentRunner to use OpenAI function calling API"
```

---

### Task 7: Coach + ingest_e2e 测试更新

**Files:**
- Modify: `tests/test_coach.py:83-96`
- Modify: `tests/test_ingest_e2e.py:23-39`

- [ ] **Step 1: 更新 test_coach.py**

修改 `test_coach_dispatches_knowledge_tool`（第 83-96 行），将 mock 数据从 DSML 字符串改为 ChatResponse：

```python
def test_coach_dispatches_knowledge_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            ChatResponse(
                content=None,
                tool_calls=[{
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "knowledge_index", "arguments": '{}'},
                }],
            ),
            ChatResponse(content="Here are the topics."),
        ]
        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)
            events = list(coach.run_iter("What can I learn?"))
        tool_events = [e for e in events if hasattr(e, "tool_name")]
        assert len(tool_events) >= 1
        assert tool_events[0].tool_name == "knowledge_index"
```

在文件头部添加 import：

```python
from src.llm_client import ChatResponse
```

- [ ] **Step 2: 更新 test_ingest_e2e.py**

修改 `test_ingest_e2e_with_mock_llm`（第 8-67 行），将所有 DSML mock 改为 ChatResponse：

```python
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.knowledge import init_knowledge_dir
from src.coach import Coach
from src.llm_client import ChatResponse


def _tc(name, arguments, call_id=None):
    """构造 tool_calls 条目。"""
    return {
        "id": call_id or f"call_{name}",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def test_ingest_e2e_with_mock_llm():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = init_knowledge_dir(tmpdir)

        raw_dir = os.path.join(knowledge_dir, "raw")
        with open(os.path.join(raw_dir, "mini-book.md"), "w") as f:
            f.write(
                "# Mini Book\n\n"
                "## Chapter 1\n\n"
                "### Rationality\n\n"
                "Rationality is the ability to think based on reason.\n\n"
                "### Cognitive Bias\n\n"
                "Cognitive biases are systematic deviations from rationality.\n"
            )

        mock_client = MagicMock()

        # Phase 1: Scan
        scan_responses = [
            ChatResponse(content=None, tool_calls=[_tc("ingest_list_raw", '{}')]),
            ChatResponse(content=None, tool_calls=[_tc("ingest_read_chunk", '{"filename":"mini-book.md","chunk_index":0}')]),
            ChatResponse(content=None, tool_calls=[_tc("ingest_read_chunk", '{"filename":"mini-book.md","chunk_index":1}')]),
            ChatResponse(content="I found 2 concepts: rationality and cognitive-bias. Shall I proceed?"),
        ]
        # Phase 2: Write
        write_responses = [
            ChatResponse(content=None, tool_calls=[_tc("ingest_write_concept", '{"name":"rationality","summary":"Thinking based on reason","content":"Rationality is the ability to think based on reason rather than emotion."}')]),
            ChatResponse(content=None, tool_calls=[_tc("ingest_write_concept", '{"name":"cognitive-bias","summary":"Systematic deviation from rationality","content":"Cognitive biases are systematic patterns of deviation from rationality in judgment."}')]),
            ChatResponse(content=None, tool_calls=[_tc("ingest_log", '{"operation":"ingest_complete","source":"mini-book.md","detail":"Extracted 2 concepts: rationality, cognitive-bias"}')]),
            ChatResponse(content="Ingest complete! Created 2 concept pages."),
        ]
        mock_client.chat.side_effect = scan_responses + write_responses

        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)

            # Phase 1: Start ingest, scan the book
            events1 = list(coach.run_iter("请开始 ingest 流程"))
            tool_events1 = [e for e in events1 if hasattr(e, "tool_name")]
            tool_names1 = [e.tool_name for e in tool_events1]
            assert "ingest_list_raw" in tool_names1
            assert "ingest_read_chunk" in tool_names1

            # Phase 2: User confirms, write concepts
            events2 = list(coach.run_iter("继续，创建这些知识点"))
            tool_events2 = [e for e in events2 if hasattr(e, "tool_name")]
            tool_names2 = [e.tool_name for e in tool_events2]
            assert "ingest_write_concept" in tool_names2
            assert "ingest_log" in tool_names2

        concepts_dir = os.path.join(knowledge_dir, "concepts")
        assert os.path.exists(os.path.join(concepts_dir, "rationality.md"))
        assert os.path.exists(os.path.join(concepts_dir, "cognitive-bias.md"))

        index_path = os.path.join(knowledge_dir, "index.md")
        with open(index_path) as f:
            index_content = f.read()
        assert "rationality" in index_content
        assert "cognitive-bias" in index_content

        log_path = os.path.join(knowledge_dir, "log.md")
        with open(log_path) as f:
            log_content = f.read()
        assert "mini-book.md" in log_content
```

- [ ] **Step 3: 跑全量测试**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest -v`
Expected: 全部 PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_coach.py tests/test_ingest_e2e.py
git commit -m "test: update coach and ingest tests to use ChatResponse mock data"
```

---

### Task 8: 最终清理

**Files:**
- 全项目扫描残留 DSML 引用

- [ ] **Step 1: 扫描残留的 DSML / 【tool】 引用**

Run: `cd /Users/walt/codes/my/BaizePaw && grep -rn '【tool】\|_extract_tool_call\|_clean_response\|_legacy_parse_params\|DSML' src/ tests/ --include='*.py'`
Expected: 无匹配（如果有，逐一清理）

- [ ] **Step 2: 跑全量测试最终确认**

Run: `cd /Users/walt/codes/my/BaizePaw && source ../.venv/bin/activate && PYTHONPATH=. pytest -v`
Expected: 全部 PASS

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: final cleanup after function calling migration"
```

---

## Self-Review

### 1. Spec Coverage

| 需求 | 对应 Task |
|------|-----------|
| LLMClient 传 tools 参数 | Task 2 |
| ChatResponse 支持 tool_calls | Task 2 |
| Core.run_iter() 从 tool_calls 取调用 | Task 4 |
| 删除 _extract_tool_call | Task 4 |
| 删除 _clean_response | Task 4 |
| 删除 _legacy_parse_params (Core) | Task 4 |
| 删除 _legacy_parse_params (Agent) | Task 6 |
| generate_tools_param() | Task 1 |
| 简化 generate_system_prompt() | Task 5 |
| ToolCallMessage content Optional | Task 3 |
| ChatHistory add_tool_call tool_call_id | Task 3 |
| AgentRunner 迁移 | Task 6 |
| 测试全部更新 | Task 4, 5, 6, 7 |
| 残留清理 | Task 8 |

无遗漏。

### 2. Placeholder Scan

无 TBD、TODO、implement later、fill in details 等。每个步骤含完整代码。

### 3. Type Consistency

- `ChatResponse.content: Optional[str]` — Task 2 定义，Task 3/4/6/7 使用，一致
- `ChatResponse.tool_calls: Optional[List[Dict]]` — Task 2 定义，Task 4/6/7 使用，一致
- `ChatHistory.add_tool_call(content: Optional[str], ..., tool_call_id: str = None)` — Task 3 定义，Task 4/6 使用，一致
- `ToolCallMessage.__init__(content: Optional[str], ...)` — Task 3 定义，Task 3 测试验证，一致
- `ToolDispatcher.generate_tools_param() -> list` — Task 1 定义，Task 4 使用，一致
- `LLMClient.__init__(..., tools: Optional[List[Dict]] = None)` — Task 2 定义，Task 4/6 使用，一致
