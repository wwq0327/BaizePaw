# 从零搭建一个 Agent：BaizePaw 实录

> 完整记录从 v0.1 到 v0.3 的搭建过程、思考方式和关键决策。

---

## 前言：为什么自己搭

市面上的 Agent 框架不少（LangChain、AutoGPT、CrewAI），但用一个东西和懂一个东西是两回事。框架帮你省了代码量，但也藏了原理。

这篇文章的目标读者是**想从原理上理解 Agent 怎么工作的人**。每个决策都记录下来，踩的坑也都在——没有黑盒。

## 技术选型

- Python 3.12 + requests + python-dotenv
- API：DeepSeek（Anthropic 兼容接口）
- TUI：Textual

选 Python 因为开发快，选 DeepSeek 因为便宜且兼容 Anthropic 接口格式，选 Textual 因为终端原生体验好。

---

## v0.1：能跑起来

### 项目结构

```
BaizePaw/
├── src/
│   ├── agent.py          # AgentRunner — 核心循环
│   ├── llm_client.py      # LLM 调用封装
│   ├── chat_history.py    # 对话历史
│   ├── shell.py           # 命令行交互
│   └── tools/
│       ├── dispatcher.py  # 工具注册与分发
│       ├── calculator.py  # 计算器
│       ├── file_ops.py    # 文件操作
│       └── search.py      # 搜索（占位）
├── config.py              # 环境变量配置
├── main.py                # 入口
└── tests/
```

思路：**最小可行版本**。一个 Agent 循环 + 一个 LLM 调用 + 几个工具，先跑起来再说。

### Agent 核心循环

```python
class AgentRunner:
    def run(self, user_input: str) -> str:
        self.history.add_user(user_input)
        while True:
            response = self.llm.chat(self.history.get_context())
            # 检查回复里有没有工具调用标记
            tool_match = re.search(r"【tool】(\w+)【/tool】(.+)", response)
            if tool_match:
                # 解析 → 执行 → 记录结果 → 继续循环
                ...
                continue
            # 没有工具调用，返回给用户
            self.history.add_assistant(response)
            return response
```

核心思想：while 循环里连续调 LLM，直到不再返回工具调用。

### 自发明工具格式

不想用 OpenAI function calling（太复杂），自创了一个简单标记：

```
【tool】calculator【/tool】2+2
【tool】file_read【/tool】config.py
【tool】grep_file【/tool】import in src
```

**关键决策**：这比 JSON 格式简单得多，LLM 很容易学会。缺点是必须通过 system prompt 告诉 LLM 这个格式的存在和用法。

### 踩坑

**坑 1：LLM 不知道工具格式**

第一次运行时，LLM 回复："抱歉，我无法读取你的文件..."

原因：LLM 不知道 `【tool】xxx【/tool】` 是我们发明的标记，它以为用户在问它能做什么。

解决：在 system prompt 里明确说明格式和用法，给示例。

**坑 2：tool\_call\_id 400 错误**

DeepSeek API 报：`Messages with role 'tool' must be a response to a preceding message with 'tool_calls'`

原因：用 tool role 发工具结果时，API 要求前一条 assistant 消息包含对应的 tool\_calls 字段。

解决：给 assistant 消息加上 tool\_calls 结构体：

```python
{
    "role": "assistant",
    "content": response,
    "tool_calls": [{
        "id": tool_call_id,
        "type": "function",
        "function": {"name": tool_name, "arguments": args}
    }]
}
```

### v0.1 阶段总结

**核心认知**：Agent 本质上是一个 while 循环——调 LLM → 解析结果 → 如果有工具就执行 → 把结果喂回去 → 继续。

**经验**：先从最简单的架构开始，不要一上来就设计复杂的分层。v0.1 只有一个 AgentRunner 类和 4 个文件，但足够验证核心逻辑。

---

## v0.2：架构重设计

### 为什么重来

v0.1 能跑，但代码集中在一个 AgentRunner 里：

- 解析工具调用
- 执行工具
- 管理历史
- 错误处理

全部混在一起，加功能越来越困难。比如想加输入排队功能，需要改 AgentRunner 甚至 shell.py；想加事件日志，也没地方插。

### 重设计思路

从问题出发：**关注点分离**。

Agent 本质上做了三件事：

1. 接收用户输入、展示结果（表现层）
2. 控制对话流程、管理并发（桥接层）
3. 调 LLM、执行工具、产出事件（核心层）

对照 MVC 的变体：

```
TUI / CLI (表现层)
    ↓ submit() / poll()
Conversation (桥接层, worker thread + queue)
    ↓ run_iter()
Core (Pipeline)
    ↓ yield Event
    ChatHistory + LLMClient + ToolDispatcher
```

### Event 体系

Core 不直接 print 也不直接写 UI，而是通过生成器 yield Event：

```python
# 工具调用 → 通知外部
yield ToolEvent(tool_name=name, params=params, result=result)
# 对话结束 → 通知外部
yield DoneEvent(content=response_text)
# 出错 → 通知外部
yield ErrorEvent(message=error_msg)
```

### Pipeline + Plugin

横切关注点（日志、通知、监控）用插件处理，不污染 Core：

```python
class LoggerPlugin(Plugin):
    def after_tool(self, event: ToolEvent):
        log(f"[{event.tool_name}] → {event.result}")
```

### Conversation 桥接层

表现层和 Core 之间多了一层：

```python
class Conversation:
    _in: queue.Queue   # 输入队列（非阻塞）
    _out: list[Event]  # 输出缓冲区
    worker: Thread     # daemon 线程跑 Core

    def submit(self, text):  # 表现层调这个，不阻塞
    def poll(self) -> list:  # 表现层轮询这个
```

这样做的好处：用户在 Agent 处理中也能打字，输入排队等待。

### 踩坑

**坑 1：worker 死锁**

Conversation 的 worker 用 `queue.Queue.get()` 阻塞等待输入。stop() 时需要安全退出。

解决：用 `timeout=0.5` 的参数 + `None` 作为 sentinel 值：

```python
while self._running:
    try:
        text = self._in.get(timeout=0.5)
    except queue.Empty:
        continue
    if text is None:  # stop() 发来的退出信号
        break
```

**坑 2：RichLog 默认不换行**

Textual 的 RichLog 超宽内容默认水平滚动，看起来不舒服。

解决：`RichLog(wrap=True)` + CSS `overflow-x: hidden`。

### v0.2 阶段总结

**核心认知**：软件架构不是设计出来的，是重构出来的。v0.1 的单体代码让你知道"什么是必要的"，然后再拆就有底气了。

**经验**：TDD 在重构时特别有用——改完立刻验证，不怕破坏已有功能。

---

## v0.3：角色系统

### 为什么需要角色定义

v0.2 的 system prompt 只有一句"你叫白泽，是一个个人助手"。太模糊了。

LLM 的行为由 system prompt 塑造。没有清晰角色定义，它会自由发挥——可能话太多、不该做的事做了、凭空编造结果。

### 角色文件的四个维度

1. **做什么（使命）** — 一句话，它的存在意义
2. **能做什么（能力）** — 如实列出工具能力，不画饼
3. **不能做什么（约束）** — 硬边界，这是最重要的
4. **沟通风格** — 简洁/详细、正式/随意

### 为什么角色定义要分离到文件

讨论时有个关键洞察：角色定义如果硬编码在 dispatcher 里，改一次就要改代码要跑测试。放到独立文件 `AGENT.md` 里，用户直接编辑就行，不需要懂代码。

```
AGENT.md → load_role() → Core → Dispatcher → System Prompt
```

### 同时修复的细节

**reasoning\_content 400 错误**：DeepSeek thinking mode 在响应里带 `reasoning_content`，必须在下一次请求中传回。修复方式：`LLMClient.chat()` 返回 `ChatResponse` 对象（同时含 content 和 reasoning\_content），`AssistantMessage.to_dict()` 条件包含。

**TUI 文本不能复制**：Textual RichLog 不支持文本选择，用 `y` 键 + `pbcopy` 实现一键复制。

### v0.3 阶段总结

**核心认知**：细节决定体验。角色定义不是"锦上添花"，它直接影响 LLM 会不会瞎编结果、会不会越界操作。

---

## 方法论

### TDD 红绿灯

每步严格三步，不跳：

1. 写测试 → `pytest` → 确认 FAIL
2. 写实现 → `pytest` → 确认 PASS
3. 跑全量 → 确认无回归 → 下一步

### 流程

```
想法 → 讨论 → ADR → Plan → TDD → Review → DevLog → Commit
```

每次大变动都有：

- ADR：为什么做、怎么选
- Plan：分几步、每步做什么
- DevLog：过程记录、踩坑总结

### 文档即代码

不只是写代码注释，而是把思路、决策、踩坑全都写成文档。别人（包括未来的自己）可以跟着文档理解每一步为什么这样做。

---

## 版本演变

| 版本   | 核心变化                          | 测试数 | 关键认知                         |
| ---- | ----------------------------- | --- | ---------------------------- |
| v0.1 | 核心循环 + 工具调用 + 自创格式            | 15  | Agent = while(调LLM→解析→执行→循环) |
| v0.2 | 三层架构 + Event + Pipeline + TUI | 29  | 先写单体能跑的，再拆出好架构               |
| v0.3 | 角色系统 + reasoning + 复制         | 41  | 角色定义决定行为质量，细节影响体验            |

---

## 下一步

- [ ] 网络搜索功能
- [ ] 会话持久化
- [ ] 多角色切换
- [ ] 工具执行安全沙箱

