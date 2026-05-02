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
    cmd = ["find", path, "-name", pattern, "-type", "f"]
    print(f"$ {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
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
    cmd = ["rm", path]
    print(f"$ {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        return f"Deleted: {path}"
    except subprocess.CalledProcessError:
        return f"Failed to delete: {path}"

def move_file_tool(src: str, dst: str) -> str:
    """移动或重命名文件"""
    if not os.path.exists(src):
        return f"Source file not found: {src}"
    cmd = ["mv", src, dst]
    print(f"$ {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        return f"Moved: {src} → {dst}"
    except subprocess.CalledProcessError:
        return f"Failed to move: {src} → {dst}"

def grep_file_tool(pattern: str, path: str = ".") -> str:
    """在文件中搜索文本，支持正则，显示行号"""
    cmd = ["grep", "-rn", "-E", pattern, path]
    print(f"$ {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        total = len(lines)
        # 限制最多显示 50 条
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
