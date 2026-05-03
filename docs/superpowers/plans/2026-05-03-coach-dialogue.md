# v0.5 教练对话实现计划

## Context

v0.4 建了知识库模块（concept/index/log/schema），但 Agent 还不能用知识库来教学。v0.5 目标：让 Agent 作为阅读教练，主动引导学习——读取知识库、讲解知识点、出题检验、评估掌握、记录进度。

## 设计决策

1. **Coach 创建自己的 Core 实例**（COACH.md 角色 + 教练工具集），不走原有 Conversation 的 Core。两个 Core 各自独立对话历史。
2. **TUI 双 Conversation**：chat_conversation + coach_conversation，`/coach` `/chat` 切换 active 指针，状态栏显示模式。
3. **教练工具驱动学习循环**：注册 knowledge_index / knowledge_concept / progress_read / progress_update 四个工具，LLM 自己决定何时读知识、何时教、何时考。
4. **progress.py 专用模块**：不用裸 file_write 操作 progress.md，提供语义 API（mark_mastered/mark_stuck/mark_skipped/set_current）。
5. **Core 和 ToolDispatcher 改为可注入**：Core 接受 role_path + tools 参数，ToolDispatcher 接受 tools 列表参数。默认值保持向后兼容。

## File Map

| 文件 | 职责 |
|------|------|
| `COACH.md` | 教练角色定义 |
| `src/knowledge/progress.py` | progress.md 读写 API |
| `src/tools/knowledge_tools.py` | 教练专用工具（4 个） |
| `src/coach.py` | Coach 类：组装教练 Core |
| `src/core.py` | 改造：接受 role_path + tools 参数 |
| `src/conversation.py` | 改造：接受 Core 实例 |
| `src/tools/dispatcher.py` | 改造：工具列表可注入 |
| `src/tui/app.py` | 双 Conversation + /coach /chat 切换 |
| `src/shell.py` | CLI 同样支持 /coach /chat |

---

## Task 1: COACH.md 角色文件

- Create: `COACH.md`
- 内容：教练身份、学习循环协议、沟通风格、工具使用规则、约束
- 验证：`load_role("COACH.md")` 返回非空

## Task 2: progress.py 模块

- Create: `src/knowledge/progress.py`, `tests/test_progress.py`
- API: `init_progress()`, `read_progress()`, `set_current()`, `mark_mastered()`, `mark_stuck()`, `mark_skipped()`
- `read_progress()` 返回 dict: `{"current": str|None, "mastered": list, "stuck": list, "skipped": list}`
- TDD: 8 个测试

## Task 3: 教练工具 knowledge_tools.py

- Create: `src/tools/knowledge_tools.py`, `tests/test_knowledge_tools.py`
- 工厂函数 `create_knowledge_tools(knowledge_dir) → list[Tool]`
- 4 个工具：knowledge_index, knowledge_concept, progress_read, progress_update
- TDD: 7 个测试

## Task 4: ToolDispatcher 工具列表可注入

- Modify: `src/tools/dispatcher.py`, `tests/test_dispatcher.py`
- `__init__(self, tools: list = None)`，None 时用默认列表（向后兼容）
- TDD: 2 个新测试

## Task 5: Core 支持参数注入

- Modify: `src/core.py`, `tests/test_core.py`
- `Core.__init__(self, role_path: str = None, tools: list = None)`
- Coach 通过 `Core(role_path="COACH.md", tools=coach_tools)` 创建教练实例
- 现有测试不受影响（默认值保持原行为）
- TDD: 2 个新测试

## Task 6: Coach 模块

- Create: `src/coach.py`, `tests/test_coach.py`
- `Coach.__init__(knowledge_dir)` → 组装教练 Core（COACH.md + 只读文件工具 + 知识工具）
- `Coach.run_iter(text)` → 委托给 `self.core.run_iter(text)`
- 教练工具集：read_file, list_dir, find_file, grep_file, calculator, search + 4 个知识工具（不含 write/delete）
- TDD: 5 个测试

## Task 7: Conversation 接受 Core 实例

- Modify: `src/conversation.py`, `tests/test_conversation.py`
- `Conversation.__init__(self, core: Core = None)`，None 时创建默认 Core
- TDD: 1 个新测试

## Task 8: TUI 模式切换

- Modify: `src/tui/app.py`, `tests/test_tui_coach.py`
- 双 Conversation：chat_conversation + coach_conversation（懒初始化）
- `/coach` `/chat` 命令切换 active_conversation
- 状态栏显示 "Chat | /coach" 或 "Coach | /chat"
- TDD: 3 个测试

## Task 9: Shell 模式切换

- Modify: `src/shell.py`
- `/coach` `/chat` 切换 active_conversation
- 提示符区分：`"You: "` vs `"You [coach]: "`
- TDD: 1 个新测试

## Task 10: DevLog + 验证

- `docs/devlog/v0.5-coach-dialogue.md`
- 全量 `pytest -v` 通过
- 手动验证 TUI `/coach` 和 CLI `/coach`

## 验证

```bash
PYTHONPATH=. pytest -v          # 全过
python main.py                   # TUI 启动，/coach 切换教练模式
python main.py --cli             # CLI 启动，/coach 切换教练模式
```
