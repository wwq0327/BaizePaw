import os
import subprocess

def read_file_tool(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file_tool(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Written to {path}"

def find_file_tool(pattern: str, path: str = ".") -> str:
    """在指定目录搜索匹配的文件"""
    try:
        result = subprocess.run(
            ["find", path, "-name", pattern, "-type", "f"],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            return result.stdout.strip()
        return f"No files matching '{pattern}' found in {path}"
    except subprocess.TimeoutExpired:
        return "Search timed out"
    except Exception as e:
        return f"Search error: {e}"

def delete_file_tool(path: str) -> str:
    """删除指定文件"""
    if not os.path.exists(path):
        return f"File not found: {path}"
    try:
        subprocess.run(["rm", path], check=True)
        return f"Deleted: {path}"
    except subprocess.CalledProcessError:
        return f"Failed to delete: {path}"

def move_file_tool(src: str, dst: str) -> str:
    """移动或重命名文件"""
    if not os.path.exists(src):
        return f"Source file not found: {src}"
    try:
        subprocess.run(["mv", src, dst], check=True)
        return f"Moved: {src} → {dst}"
    except subprocess.CalledProcessError:
        return f"Failed to move: {src} → {dst}"
