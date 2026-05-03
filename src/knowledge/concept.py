import os


def _concept_path(name: str, base_dir: str) -> str:
    safe_name = name.lower().replace(" ", "-")
    return os.path.join(base_dir, f"{safe_name}.md")


def create_concept(name: str, content: str, base_dir: str) -> str:
    path = _concept_path(name, base_dir)
    header = f"# {name}\n\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + content)
    return path


def read_concept(name: str, base_dir: str):
    path = _concept_path(name, base_dir)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def update_concept(name: str, content: str, base_dir: str) -> str:
    path = _concept_path(name, base_dir)
    header = f"# {name}\n\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + content)
    return path


def delete_concept(name: str, base_dir: str) -> None:
    path = _concept_path(name, base_dir)
    if os.path.exists(path):
        os.remove(path)
