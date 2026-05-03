import os
import subprocess

from .tool_base import Tool


def _read_file(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write_file(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Written to {path}"


def _append_file(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)
    return f"Appended to {path}"


def _copy_file(src: str, dst: str) -> str:
    if not os.path.exists(src):
        return f"Source file not found: {src}"
    cmd = ["cp", src, dst]
    try:
        subprocess.run(cmd, check=True)
        return f"$ cp {src} {dst}\nCopied: {src} → {dst}"
    except subprocess.CalledProcessError:
        return f"Failed to copy: {src} → {dst}"


def _list_dir(path: str = ".") -> str:
    if not os.path.exists(path):
        return f"Directory not found: {path}"
    try:
        entries = os.listdir(path)
        # 过滤隐藏文件和常见无关目录
        visible = [e for e in entries if not e.startswith(".")]
        if not visible:
            return "(empty)"
        return "\n".join(visible)
    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Listing error: {e}"


def _find_file(pattern: str, path: str = ".") -> str:
    cmd = ["find", path, "-name", pattern, "-type", "f"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.stdout.strip():
            return result.stdout.strip()
        return f"No files matching '{pattern}' found in {path}"
    except subprocess.TimeoutExpired:
        return "Search timed out"
    except Exception as e:
        return f"Search error: {e}"


def _delete_file(path: str) -> str:
    if not os.path.exists(path):
        return f"File not found: {path}"
    cmd = ["rm", path]
    try:
        subprocess.run(cmd, check=True)
        return f"$ rm {path}\nDeleted: {path}"
    except subprocess.CalledProcessError:
        return f"Failed to delete: {path}"


def _move_file(src: str, dst: str) -> str:
    if not os.path.exists(src):
        return f"Source file not found: {src}"
    cmd = ["mv", src, dst]
    try:
        subprocess.run(cmd, check=True)
        return f"$ mv {src} {dst}\nMoved: {src} → {dst}"
    except subprocess.CalledProcessError:
        return f"Failed to move: {src} → {dst}"


def _grep_file(pattern: str, path: str = ".") -> str:
    cmd = [
        "grep",
        "-rn",
        "-E",
        pattern,
        path,
        "--exclude-dir=__pycache__",
        "--exclude-dir=.git",
        "--exclude-dir=.pytest_cache",
        "--exclude-dir=.venv",
        "--exclude-dir=node_modules",
        "--exclude-dir=.claude",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        total = len(lines)
        MAX_LINES = 50
        if total > MAX_LINES:
            shown = lines[:MAX_LINES]
            return "\n".join(shown) + f"\n[显示前 {MAX_LINES} 条结果，共找到 {total} 条]"
        elif total > 0:
            return result.stdout.strip()
        else:
            return f"No matches found for '{pattern}' in {path}"
    except subprocess.TimeoutExpired:
        return "Search timed out"
    except Exception as e:
        return f"Search error: {e}"


# Tool definitions below


read_file_tool = Tool(
    name="file_read",
    description="读取文件内容",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"}
        },
        "required": ["path"],
    },
    fn=_read_file,
)

write_file_tool = Tool(
    name="file_write",
    description="写入文件内容（覆盖已有内容）",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"},
            "content": {"type": "string", "description": "要写入的内容"},
        },
        "required": ["path", "content"],
    },
    fn=_write_file,
)

file_append_tool = Tool(
    name="file_append",
    description="追加内容到文件末尾",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"},
            "content": {"type": "string", "description": "要追加的内容"},
        },
        "required": ["path", "content"],
    },
    fn=_append_file,
)

copy_file_tool = Tool(
    name="copy_file",
    description="复制文件",
    parameters={
        "type": "object",
        "properties": {
            "src": {"type": "string", "description": "源文件路径"},
            "dst": {"type": "string", "description": "目标文件路径"},
        },
        "required": ["src", "dst"],
    },
    fn=_copy_file,
)

list_dir_tool = Tool(
    name="list_dir",
    description="列出目录内容",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "目录路径（默认当前目录）",
            }
        },
        "required": [],
    },
    fn=_list_dir,
)

find_file_tool = Tool(
    name="find_file",
    description="按文件名搜索文件",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "文件名模式，支持通配符"},
            "path": {
                "type": "string",
                "description": "搜索目录（默认当前目录）",
            },
        },
        "required": ["pattern"],
    },
    fn=_find_file,
)

delete_file_tool = Tool(
    name="delete_file",
    description="删除指定文件",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"}
        },
        "required": ["path"],
    },
    fn=_delete_file,
)

move_file_tool = Tool(
    name="move_file",
    description="移动或重命名文件",
    parameters={
        "type": "object",
        "properties": {
            "src": {"type": "string", "description": "源文件路径"},
            "dst": {"type": "string", "description": "目标文件路径"},
        },
        "required": ["src", "dst"],
    },
    fn=_move_file,
)

grep_file_tool = Tool(
    name="grep_file",
    description="在文件中搜索文本，支持正则表达式",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "搜索模式，支持正则"},
            "path": {
                "type": "string",
                "description": "搜索目录（默认当前目录）",
            },
        },
        "required": ["pattern"],
    },
    fn=_grep_file,
)
