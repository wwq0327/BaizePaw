import os
import tempfile
from src.tools.file_ops import list_dir_tool


def test_list_dir_shows_filenames_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, "a.txt"), "w").close()
        open(os.path.join(tmpdir, "b.md"), "w").close()

        result = list_dir_tool.fn(path=tmpdir)
        assert "a.txt" in result
        assert "b.md" in result
        assert "drwx" not in result  # 不应包含权限信息
        assert "staff" not in result  # 不应包含用户组


def test_list_dir_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = list_dir_tool.fn(path=tmpdir)
        assert result == "" or "(empty)" in result


def test_list_dir_nonexistent():
    result = list_dir_tool.fn(path="/nonexistent/path/xyz")
    assert "not found" in result.lower() or "不存在" in result or "No such" in result
