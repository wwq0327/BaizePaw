import os


def load_role(path: str = None) -> str:
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "AGENT.md",
        )
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
