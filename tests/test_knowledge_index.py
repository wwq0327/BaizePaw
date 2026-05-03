import os
import tempfile
from src.knowledge.index import add_to_index, read_index, remove_from_index


def test_add_and_read_index():
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.md")

        add_to_index("variables", "Store values in memory", index_path)
        add_to_index("functions", "Reusable blocks of code", index_path)

        content = read_index(index_path)
        assert "variables" in content
        assert "Store values in memory" in content
        assert "functions" in content


def test_remove_from_index():
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.md")

        add_to_index("variables", "Store values", index_path)
        add_to_index("functions", "Reusable code", index_path)
        remove_from_index("variables", index_path)

        content = read_index(index_path)
        assert "variables" not in content
        assert "functions" in content


def test_read_empty_index():
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.md")
        content = read_index(index_path)
        assert content == ""
