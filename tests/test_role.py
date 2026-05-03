import os
import tempfile
import pytest
from src.role import load_role


def test_load_role_reads_agent_md():
    """当前项目根目录有 AGENT.md，验证能读取出非空内容"""
    content = load_role()
    assert len(content) > 0
    assert "白泽" in content


def test_load_role_custom_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("test role content")
        path = f.name
    try:
        content = load_role(path)
        assert content == "test role content"
    finally:
        os.unlink(path)


def test_load_role_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_role("/nonexistent/path.md")
