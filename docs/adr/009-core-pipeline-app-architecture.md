# ADR-009: Core + Pipeline + App 三层架构

## 状态
已通过

## 背景

当前 AgentRunner 是单体同步架构。`run()` 阻塞直到全部完成才返回，没有中间状态输出、没有插件机制、CLI 紧耦合、`print()` 直接写 stdout。支持 TUI 必须先解耦。

## 方案

拆成三层，Core 改为生成器模式。

### 架构

```
TUI / CLI（表现层）
    │
    ▼
App（桥接层）
    │  管理事件队列、worker 线程
    │  用户输入 → submit() → 等上次跑完，启动新 Core 线程
    │  poll() → 返回事件列表给 UI
    ▼
Core（核心层）
    │  run_iter(text) → yield Event
    │  Pipeline 编排 LLM + 工具 + 可选的 Plugin
    │
    ├─ Plugin.before_iteration（可选）
    ├─ LLMClient.chat
    ├─ 解析工具标记
    │   ├─ 有工具 → dispatch → Plugin.after_tool → 继续
    │   └─ 无工具 → yield DoneEvent，退出
    ├─ Plugin.after_iteration（可选）
    └─ 每一帧 yield Event 给 App 层去展示
```

### Event 类型

LLM 的原始回复（含 `【tool】` 标记文本）只在 Core 内部使用，**不对外输送**。TUI 只拿到处理后的结构：

```python
class ToolEvent:
    tool_name: str          # "find_file"
    params: dict            # {"pattern": "*.py", "path": "."}
    result: str             # 工具执行结果
    command: str            # 执行的 CLI 命令（供 TUI 展示用）

class DoneEvent:
    content: str            # LLM 最终回答文本

class ErrorEvent:
    message: str            # 出错原因
```

生成器 yield `ToolEvent` 或 `DoneEvent` 或 `ErrorEvent`，不暴露 LLM 原始输出的 `【tool】` 标记。

### Core 生成器流程

```python
def run_iter(self, text):
    self.history.add_user(text)
    while True:
        self.plugin_invoke("before_iteration")
        response = self.llm.chat(self.history.get_context())

        tool_match = re.search(...)
        if tool_match:
            tool_name, params = self._parse(response)
            self.history.add_tool_call(response, tool_name, ...)
            result = self.dispatcher.dispatch(tool_name, params)
            self.history.add_tool_result(tool_call_id, tool_name, str(result))

            yield ToolEvent(tool_name, result, params)
            self.plugin_invoke("after_tool", tool_name, result)
            continue

        self.history.add_assistant(response)
        yield DoneEvent(response)
        return
```

### Plugin 系统（轻量）

Plugin 为可选。不传 Plugin 时 Core 照常跑。

```python
class Plugin:
    def before_iteration(self, ctx) -> None: ...
    def after_tool(self, tool_name, result) -> list[str]: ...
    def after_iteration(self, ctx) -> None: ...
```

`after_tool` 返回 `list[str]`。如果返回了系统消息（如"文件太大，只读了前 1000 行"），Core 将它们作为 `user` 消息注入上下文，再回到 LLM 循环。返回空列表则不注入。SystemEventHandler 按需后续实现。

当前只实现 `LoggerPlugin`（日志记录）。

### App 桥接层

Always-on worker + 两个 `queue.Queue`：

```
          _in (输入队列)              _out (事件队列)
用户输入 ──→ queue.Queue ──→ worker 线程 ──→ queue.Queue ──→ UI poll
              submit() 不阻塞    逐条消费              UI 每帧取事件
```

worker 线程一启动就永久循环：`_in.get()` 阻塞等输入 → 取到后跑 Core → 事件入 `_out` → 回到 `_in.get()`。没输入时睡着，不耗 CPU。

**线程安全：** `queue.Queue` 自带，不需要锁。`submit()` 永远不阻塞。

**App 接口**

```python
class Conversation:
    def __init__(self):
        self._in = queue.Queue()      # 输入队列
        self._out = queue.Queue()     # 事件输出
        self._worker = Thread(target=self._loop, daemon=True)
        self._worker.start()

    def submit(self, text) -> None:
        self._in.put(text)           # 永远不阻塞

    def poll(self) -> list[Event]:
        events = []
        while not self._out.empty():
            events.append(self._out.get_nowait())
        return events

    def _loop(self):
        while True:
            text = self._in.get()          # 阻塞等输入
            try:
                for event in self.core.run_iter(text):
                    self._out.put(event)
            except Exception as e:
                self._out.put(ErrorEvent(str(e)))
```

### 去 `print()` 污染

`file_ops.py` 和 `llm_client.py` 里现存的 `print(f"$ ...")` 全部移走。工具执行的命令展示通过 `ToolEvent.command_context` 传上来，由 UI 层决定是否显示。

`_find_file` 等工具函数返回字符串结果，不再自己 `print()`。`CommandEvent` 一起跟着 `ToolEvent` 带出。

### 变更范围

| 文件 | 动作 |
|------|------|
| `src/core.py` | 新增。Core 生成器 + Pipeline 编排 |
| `src/pipeline.py` | 新增。Plugin 接口 + Pipeline |
| `src/event.py` | 新增。Event 类型定义 |
| `src/conversation.py` | 新增。App 桥接层 |
| `src/tui/app.py` | 新增。Textual 应用 |
| `src/tools/file_ops.py` | 修改。去掉 `print()`，工具结果纯字符串 |
| `src/shell.py` | 保留。改为走 Conversation 层 |
| `src/agent.py` | 废弃。功能迁到 core.py |
| `main.py` | 更新入口 |
