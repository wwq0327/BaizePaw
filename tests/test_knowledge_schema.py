import os
import tempfile
from src.knowledge.schema import load_schema


def test_load_schema_returns_content():
    content = load_schema()
    assert "concept" in content
    assert "index" in content


def test_load_schema_custom_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test Schema\n## concept\nname: test")
        path = f.name
    try:
        content = load_schema(path)
        assert "Test Schema" in content
    finally:
        os.unlink(path)
