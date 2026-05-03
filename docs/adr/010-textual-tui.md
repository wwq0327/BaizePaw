# ADR-010: TUI with Textual

## 状态
已通过

## 背景

当前只有 CLI（`input()` / `print()`），阻塞输入、无实时状态、无中间过程展示。引入 Textual TUI 来解决。

## 方案

使用 Textual 构建 TUI，通过 Conversation 桥接层与 Core 通信。

### 布局

```
┌──────────────────────────────────────────────────┐
│  BaizePaw                                        │
├──────────────────────────────────────────────────┤
│  [dim]You: 计算 2+2[/]                            │
│  [yellow]▸ calculator: 4[/]                       │
│  [green]BaizePaw: 2 + 2 = 4[/]                    │
│  ...                                             │
├──────────────────────────────────────────────────┤
│  就绪 / 处理中...                                  │
├──────────────────────────────────────────────────┤
│  > _                                              │
└──────────────────────────────────────────────────┘
```

### 事件驱动的数据流

```
TUI.Input.on_submitted
    ↓
Conversation.submit(text)           ← 立即返回，不阻塞
    │  放入 _in 队列
    ▼
Always-on worker 线程               ← 永久循环
    │  _in.get() → Core.run_iter()
    │      ├─ ToolEvent("calculator", {"expr": "2+2"}, result="4")
    │      ├─ ToolEvent("file_read", {"path": "config.py"}, result="...")
    │      └─ DoneEvent("2 + 2 = 4")
    └─ 事件入 _out 队列
         ↓
TUI.set_interval(1/10s)
    └─ Conversation.poll()
         └─ 按事件类型更新 RichLog + 状态栏
```

### 交互约定

**输入排队**：用户可随时打字。TUI 的输入框永远可交互。多条输入自动在 `_in` 队列里排队，worker 逐条消费。

**中间状态展示**：ToolEvent 来了就在对话区显示 `▸ 工具名: 结果摘要`。DoneEvent 来了就显示完整回复。状态栏在等 LLM 时显示"处理中..."，跑完变回"就绪"。

**命令展示**：ToolEvent 携带 `command` 字段（工具执行的原始命令），UI 可选择以 dim 灰色显示或折叠隐藏。`file_ops.py` 不再自己 `print()`。

### 启动方式

```bash
pip install textual                       # 新增依赖
python main.py                            # 默认启动 TUI
python main.py --cli                      # 启动 CLI
```

CLI 也走 Conversation 层——`shell.py` 调 `conversation.submit(text)` 后，在一个轮循里去 poll 事件，收到 `DoneEvent` 后输出最终结果，继续等下一行输入。

### 变更范围

| 文件 | 动作 |
|------|------|
| `src/tui/app.py` | 新增。Textual 应用 |
| `src/tui/__init__.py` | 新增。空文件 |
| `src/conversation.py` | 新增。AD-009 共用 |
| `src/event.py` | 新增。AD-009 共用 |
| `main.py` | 修改。TUI 为默认入口，`--cli` 走旧入口 |
| `requirements.txt` | 新增 `textual` |
