import os
from datetime import datetime


def init_progress(path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("# 学习进度\n\n")
        f.write(f"> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("## 掌握\n\n")
        f.write("## 卡住\n\n")
        f.write("## 跳过\n\n")
        f.write("## 当前\n\n")


def read_progress(path: str) -> dict:
    if not os.path.exists(path):
        return {"current": None, "mastered": [], "stuck": [], "skipped": []}

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    mastered = _read_list(content, "掌握")
    stuck = _read_list(content, "卡住")
    skipped = _read_list(content, "跳过")
    current = _read_current(content)

    return {"current": current, "mastered": mastered, "stuck": stuck, "skipped": skipped}


def set_current(name: str, path: str) -> None:
    progress = read_progress(path)
    progress["current"] = name
    _write_progress(progress, path)


def mark_mastered(name: str, path: str) -> None:
    progress = read_progress(path)
    if name not in progress["mastered"]:
        progress["mastered"].append(name)
    if progress["current"] == name:
        progress["current"] = None
    _remove_from_lists(name, progress, ["stuck", "skipped"])
    _write_progress(progress, path)


def mark_stuck(name: str, path: str) -> None:
    progress = read_progress(path)
    if name not in progress["stuck"]:
        progress["stuck"].append(name)
    _remove_from_lists(name, progress, ["mastered", "skipped"])
    _write_progress(progress, path)


def mark_skipped(name: str, path: str) -> None:
    progress = read_progress(path)
    if name not in progress["skipped"]:
        progress["skipped"].append(name)
    _remove_from_lists(name, progress, ["mastered", "stuck"])
    if progress["current"] == name:
        progress["current"] = None
    _write_progress(progress, path)


def _read_list(content: str, section: str) -> list:
    items = []
    in_section = False
    for line in content.split("\n"):
        if line.strip() == f"## {section}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            items.append(line.strip()[2:].strip())
    return items


def _read_current(content: str) -> str | None:
    for line in content.split("\n"):
        if line.strip().startswith("→ "):
            return line.strip()[2:].strip()
    return None


def _remove_from_lists(name: str, progress: dict, lists: list) -> None:
    for key in lists:
        if name in progress[key]:
            progress[key].remove(name)


def _write_progress(progress: dict, path: str) -> None:
    lines = [
        "# 学习进度\n",
        f"> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "## 掌握\n",
    ]
    for item in progress["mastered"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 卡住\n")
    for item in progress["stuck"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 跳过\n")
    for item in progress["skipped"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 当前\n")
    if progress["current"]:
        lines.append(f"→ {progress['current']}")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
