# BaizePaw

## 目标
从 0 搭建一个个人通用 Agent，能多轮对话、调用工具，逐步成长。

## 架构
```
TUI / CLI (表现层)
    ↓ submit() / poll()
Conversation (桥接层, worker thread + queue)
    ↓ run_iter()
Core (Pipeline)
    ↓ yield Event
    ChatHistory + LLMClient + ToolDispatcher
```

三层分离：表现层只管 UI，Conversation 管线程和队列，Core 管业务逻辑和 Event 流。

## 技术栈
- Python 3.x
- 共享虚拟环境：`my/.venv`
- API：DeepSeek（Anthropic 兼容接口）
- 环境变量：`LLM_API_KEY`（支持回退 `SILICONFLOW_API_KEY` / `DEEPSEEK_API_KEY`）
- 依赖：requests、python-dotenv、textual

## 启动方式
```bash
cd BaizePaw
source ../.venv/bin/activate
python main.py          # TUI 模式（默认）
python main.py --cli    # CLI 模式
```

或直接 `./baize`

## 测试
```bash
cd BaizePaw
source ../.venv/bin/activate
PYTHONPATH=. pytest -v
```

## 验证方式
1. 启动后能接收输入
2. 能返回 LLM 回复
3. 触发工具调用时能正确执行并返回结果
4. 多轮对话上下文连贯
5. TUI 模式正常启动和交互
6. CLI 模式正常启动和交互

## 开发流程

### TDD 红绿灯
每个 Task 严格三步：
1. **写测试** → 跑 pytest → 确认 FAIL
2. **写实现** → 跑 pytest → 确认 PASS
3. **跑全量测试** → 确认无回归 → 下一 Task

一步做完再做下一步，不跳不并行。

### 改动规范
- 新模块：先建文件，再建对应测试文件
- 改现有模块：改完必须跑全量 `pytest -v`
- 废弃模块：加 `DEPRECATED` 注释，不删文件
- 工具函数的 `print()` 调试输出要清掉，信息嵌入返回字符串

### 架构规则
- **表现层**（TUI/Shell）只管 UI，不直接调 Core
- **Conversation 层**是唯一桥梁，submit 非阻塞，poll 非阻塞
- **Core 层**通过 `run_iter()` 生成器 yield Event，不直接 print
- Event 体系：ToolEvent / DoneEvent / ErrorEvent，用 `Event = Union[...]` 做类型别名
- Pipeline + Plugin 做横切关注点（日志、通知等），不改 Core

### 计划与文档
- 大改动先在 `docs/plans/` 写实现计划，确认后再动手
- 完成后在 `docs/devlog/` 写 DevLog
- 架构决策在 `docs/adr/` 记录
- 过时计划移入 `archive/`，不删

### 测试约定
- Mock LLMClient 而不发真实请求
- 测试文件命名：`tests/test_<模块名>.py`
- Conversation 测试用 `time.sleep(0.3)` 等 worker 处理，`daemon=True` 线程
