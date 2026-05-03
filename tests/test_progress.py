import os
import tempfile
from src.knowledge.progress import (
    init_progress,
    read_progress,
    set_current,
    mark_mastered,
    mark_stuck,
    mark_skipped,
)


def test_init_progress_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "progress.md")
        init_progress(path)
        assert os.path.exists(path)
        content = open(path, "r", encoding="utf-8").read()
        assert "# 学习进度" in content


def test_read_progress_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "progress.md")
        result = read_progress(path)
        assert result == {"current": None, "mastered": [], "stuck": [], "skipped": []}


def test_read_progress_after_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "progress.md")
        init_progress(path)
        result = read_progress(path)
        assert result == {"current": None, "mastered": [], "stuck": [], "skipped": []}


def test_set_current():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "progress.md")
        init_progress(path)
        set_current("variables", path)
        result = read_progress(path)
        assert result["current"] == "variables"


def test_mark_mastered():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "progress.md")
        init_progress(path)
        set_current("variables", path)
        mark_mastered("variables", path)
        result = read_progress(path)
        assert "variables" in result["mastered"]
        assert result["current"] is None


def test_mark_stuck():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "progress.md")
        init_progress(path)
        set_current("decorators", path)
        mark_stuck("decorators", path)
        result = read_progress(path)
        assert "decorators" in result["stuck"]


def test_mark_skipped():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "progress.md")
        init_progress(path)
        set_current("generators", path)
        mark_skipped("generators", path)
        result = read_progress(path)
        assert "generators" in result["skipped"]


def test_mark_mastered_idempotent():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "progress.md")
        init_progress(path)
        mark_mastered("variables", path)
        mark_mastered("variables", path)
        result = read_progress(path)
        assert result["mastered"].count("variables") == 1
