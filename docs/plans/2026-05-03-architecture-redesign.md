# 架构重设计实现计划

## Goal

从单体 `AgentRunner` 拆为三层：表现层 → App 桥接层 → Core(Pipeline)。

## 开发原则

**每个 Task 三步骤：**
1. 写测试 → 跑 `pytest` → 确认 FAIL
2. 写实现 → 跑 `pytest` → 确认 PASS
3. 确认后，下一 Task

一步做完再做下一步，不跳不并行。

---

## Task 1: Event 类型

- Create: `src/event.py`
- `ToolEvent`（tool_name、params、result、command）
- `DoneEvent`（content）
- `ErrorEvent`（message）
- Create: `tests/test_event.py`
  - 测试每个 Event 的构造和属性

## Task 2: Plugin 接口 + Pipeline

- Create: `src/pipeline.py`
- Plugin 基类（三个可选 hook）
- Pipeline 类（持有插件列表，不传插件也能跑）
- LoggerPlugin（只记日志）
- Create: `tests/test_pipeline.py`
  - Plugin 不传 → Pipeline 照常跑
  - LoggerPlugin 正常 callback
  - after_tool 返回系统消息

## Task 3: Core + run_iter 生成器

- Create: `src/core.py`
- `Core.run_iter(text) → yield Event`
- 内部复用 `ChatHistory`、`LLMClient`、`ToolDispatcher`（不动）
- 参数解析逻辑从 `agent.py` 迁入
- Create: `tests/test_core.py`
  - Mock LLMClient → 验证无工具时 yield DoneEvent
  - Mock LLMClient → 验证有工具时 yield ToolEvent → DoneEvent
  - 验证 LLM 原始含 `【tool】` 的文本不出现在 Event 中
- `agent.py` 标记废弃

## Task 4: Conversation 桥接层

- Create: `src/conversation.py`
- Always-on worker + `_in` / `_out` queue
- `submit(text)` → `_in.put(text)`，不阻塞
- `poll()` → 非阻塞返回事件列表
- worker 异常时 yield ErrorEvent，不崩溃
- Create: `tests/test_conversation.py`
  - submit 不阻塞
  - poll 能拿到事件
  - 多条 submit 排队执行

## Task 5: 去 print() 污染

- Modify: `src/tools/file_ops.py`
- 去掉所有 `print(f"$ ...")`
- 命令信息附加到工具返回字符串中（或由 Core 在构造 ToolEvent 时提取）
- 测试：现有 `tests/test_dispatcher.py` 全过

## Task 6: Textual TUI

- Create: `src/tui/app.py` + `src/tui/__init__.py`
- RichLog + Input + Status
- `on_input_submitted` → `conversation.submit(text)`
- `set_interval(1/10s)` → `conversation.poll()` → 更新 UI
- 测试：手动启动 TUI 验证

## Task 7: CLI 入口走 Conversation 层

- Modify: `src/shell.py`
- `submit(text)` 后 poll 循环 → DoneEvent 则输出 → 继续等 input()
- Modify: `main.py`
- 默认 TUI，`--cli` 走 CLI
- 测试：手动 `python main.py --cli` 验证，现有测试全过

## Task 8: 文档收尾

- DevLog：`docs/devlog/v0.2-architecture-redesign.md`
- 记录本次重设计过程 + 踩坑
- 提交代码

## 验证

```bash
PYTHONPATH=. pytest -v          # 全过
python main.py                   # TUI 启动正常
python main.py --cli             # CLI 启动正常
```
