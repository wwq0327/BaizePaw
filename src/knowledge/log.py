import os
from datetime import datetime


def append_log(operation: str, source: str, detail: str, path: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"## [{timestamp}] {operation}"
    if source:
        entry += f" | {source}"
    entry += f"\n{detail}\n\n"

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Knowledge Log\n\n")
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry)


def read_log(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
