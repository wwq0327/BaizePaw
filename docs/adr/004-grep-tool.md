# ADR-004: 添加文件内容搜索工具（grep）

## 状态
已通过

## 背景

需要让 BaizePaw 能够搜索文件内容，比如：
- "在当前目录搜索 `def main` 的文件"
- "在 src 目录搜索 `class AgentRunner`"

## 决策

### 工具名

`grep_file` — 在文件中搜索文本

### 调用方式

使用 macOS 自带的 `grep` 命令，带以下参数：
- `-n` 显示行号
- `-r` 递归搜索
- `-E` 支持正则表达式

### 命令格式

```bash
grep -rn -E "搜索内容" 目录路径
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `pattern` | str | 要搜索的文本（支持正则） |
| `path` | str | 搜索目录，默认 "." |

### 输出展示

执行前显示命令：
```
$ grep -rn -E "AgentRunner" src/
```

执行后显示匹配结果（含行号）：
```
src/agent.py:7:class AgentRunner:
src/agent.py:14:    def run(self, user_input: str) -> str:
```

### 数量限制

最多显示 50 条匹配结果，超出时提示：
```
[显示前 50 条结果，共找到 XX 条]
```

### System Prompt 更新

```
- 搜索文件内容：使用【tool】grep_file【/tool】后跟搜索内容和目录
  格式：「在 src 目录搜索 AgentRunner」→ 【tool】grep_file【/tool】AgentRunner in src
  支持正则表达式
```

## 实现清单

- [x] `file_ops.py` 添加 `grep_file_tool` 函数
- [x] `dispatcher.py` 注册 `grep_file`
- [x] `agent.py` 更新参数映射
- [x] `llm_client.py` 更新 system prompt
- [x] 测试验证

---

**决议日期：2026-05-02**
