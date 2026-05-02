# 6. 工具封装重构：从裸函数到结构化 Tool 对象

## 状态

- 2026-05-03：已实现

## 背景

工具系统有三个痛点：

1. **分散**：加一个新工具要改 4 个文件（写函数、dispatcher 注册、agent.py 加 if/elif、prompts.py 写格式）
2. **脆弱**：6 分支 if/elif 参数解析容易出 bug（如 search 工具的 else 分支映射错参数名）
3. **手写**：System Prompt 手动维护，容易和实际工具有偏差

## 方案

引入 `Tool` 数据类，让工具成为自包含的结构化定义。

### Tool 定义

```python
@dataclass
class Tool:
    name: str           # "file_read"
    description: str     # "读取文件内容"
    parameters: dict      # JSON Schema
    fn: Callable          # 实现函数
```

### 变更

| 层面 | 改前 | 改后 |
|------|------|------|
| 工具定义 | 裸函数 | `Tool` 实例，内嵌描述 + 参数 Schema |
| 注册 | `dispatcher.py` 手写 dict | `register(tool)` 方法 |
| 参数解析 | 6 分支 if/elif | `json.loads()` 优先，旧格式 fallback |
| System Prompt | `prompts.py` 手写 | 由 `dispatcher.generate_system_prompt()` 自动生成 |
| 实现函数 | 公开导出 | 下划线开头（`_read_file`），不对外暴露 |

### 文件清单

新增：`src/tools/tool_base.py`
改动：`calculator.py`、`search.py`、`file_ops.py`、`dispatcher.py`、`__init__.py`、`agent.py`、`llm_client.py`、`prompts.py`、测试文件

## 收益

- 新工具只需在一个文件里写 `Tool(...)` 实例，dispatcher 加一行 import 即可注册
- System Prompt 自动同步，不会漏掉工具
- JSON 参数解析统一了所有工具的接口
- 旧格式兼容层保留，不会破坏已有对话
