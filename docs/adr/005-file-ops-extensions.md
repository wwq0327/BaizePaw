# 5. 完善文件操作工具

## 状态
- 2026-05-03：通过

## 背景

现有文件操作工具缺少三个基础能力：复制文件、查看目录、追加写入。用户希望通过补齐这三个工具，覆盖日常文件操作需求。

## 方案

给 `file_ops.py` 新增三个工具，调用 macOS CLI 实现：

| 工具 | 函数 | CLI | 参数 |
|------|------|-----|------|
| `copy_file` | `copy_file_tool` | `cp` | src, dst |
| `list_dir` | `list_dir_tool` | `ls -la` | path（默认当前目录） |
| `file_append` | `file_append_tool` | open `a` | path, content |

### 解析规则（agent.py）

- `copy_file`：`src -> dst`（复用 move_file 的解析逻辑）
- `list_dir`：直接传路径，支持空参数（默认 `.`）
- `file_append`：`path:content`（复用 file_write 的解析逻辑）

### 更新项

1. **`src/tools/file_ops.py`** — 新增三个函数
2. **`src/agent.py`** — 在工具解析分支中注册三个新工具
3. **`src/tools/dispatcher.py`** — 注册到工具映射表
4. **`src/tools/__init__.py`** — 补齐导出
5. **`src/prompts.py`** — System Prompt 加入新工具说明
6. **`README.md`** — 工具列表更新
7. **`docs/devlog/TODO.md`** — 更新完成状态

### 安全

- 不限制路径（与现有文件工具一致）
- 直接执行 CLI，不做沙箱处理

## 代价

- `file_append` 对较大日志文件追加时可能出现问题，当前不做限制
