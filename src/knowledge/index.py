import os


def _ensure_index(path: str) -> None:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Knowledge Index\n\n")


def add_to_index(name: str, summary: str, path: str) -> None:
    _ensure_index(path)
    link = f"concepts/{name.lower().replace(' ', '-')}.md"
    entry = f"- [{name}]({link}) — {summary}\n"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if entry.strip() not in content:
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)


def read_index(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def remove_from_index(name: str, path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    link = f"concepts/{name.lower().replace(' ', '-')}.md"
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            if link not in line:
                f.write(line)
