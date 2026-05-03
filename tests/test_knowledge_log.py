import os
import tempfile
from src.knowledge.log import append_log, read_log


def test_append_and_read_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "log.md")

        append_log("ingest", "python-handbook.md", "Extracted 12 concepts", log_path)
        append_log("lint", "", "Found 2 orphan pages", log_path)

        content = read_log(log_path)
        assert "ingest" in content
        assert "python-handbook.md" in content
        assert "Extracted 12 concepts" in content
        assert "lint" in content
        assert "Found 2 orphan pages" in content
        assert "## [" in content


def test_read_empty_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "log.md")
        content = read_log(log_path)
        assert content == ""
