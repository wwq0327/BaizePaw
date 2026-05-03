import os


def init_knowledge_dir(base_dir: str = None) -> str:
    if base_dir is None:
        base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "knowledge",
        )
    for subdir in ["raw", "concepts", "comparisons"]:
        os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)
    return base_dir
