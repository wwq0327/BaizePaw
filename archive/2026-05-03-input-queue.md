# 输入排队实现计划

## Goal
Agent 处理过程中用户可随时打字，输入排队等待，当前 `agent.run()` 结束后自动处理下一条。

## Architecture
只改 `shell.py`，不动 agent、chat_history、message、工具系统。

```
Shell 启动
    ├─ 启动后台输入线程（daemon）
    │     └─ 循环 input() → queue.Queue
    │
    └─ 主循环
          └─ queue.get() → agent.run() → 打印结果 → 继续
```

## Task 1: 改 shell.py

**Files:**
- Modify: `src/shell.py`

- [ ] 引入 `threading` 和 `queue`
- [ ] `_input_reader()` 方法：后台线程，循环 `input("You: ")`，输入丢入队列
- [ ] 主循环改为：从队列取输入 → `agent.run()` → 打印 → 再取
- [ ] `quit/exit/q` 检查放主循环侧
- [ ] readline 历史改到主循环侧保存
- [ ] 退出时设置 `running = False`，输入线程自然结束

## Task 2: 测试验证

- [ ] `PYTHONPATH=. pytest -v` 全过（只改 shell.py，不影响现有测试）
- [ ] 手动跑 `./baize` 验证：输入一条指令 → 在 agent 处理时再打字 → 等上一条跑完自动处理
