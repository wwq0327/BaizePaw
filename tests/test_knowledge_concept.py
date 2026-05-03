import os
import tempfile
from src.knowledge.concept import create_concept, read_concept, update_concept, delete_concept


def test_create_and_read_concept():
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = os.path.join(tmpdir, "concepts")
        os.makedirs(concepts_dir)

        create_concept("variables", "Variables store values in memory.", concepts_dir)

        path = os.path.join(concepts_dir, "variables.md")
        assert os.path.exists(path)

        content = read_concept("variables", concepts_dir)
        assert "Variables store values" in content
        assert "# variables" in content


def test_update_concept():
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = os.path.join(tmpdir, "concepts")
        os.makedirs(concepts_dir)

        create_concept("loops", "Loops repeat code.", concepts_dir)
        update_concept("loops", "Loops: for, while, and iteration patterns.", concepts_dir)

        content = read_concept("loops", concepts_dir)
        assert "for, while" in content


def test_delete_concept():
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = os.path.join(tmpdir, "concepts")
        os.makedirs(concepts_dir)

        create_concept("temp", "Temporary concept.", concepts_dir)
        delete_concept("temp", concepts_dir)

        assert not os.path.exists(os.path.join(concepts_dir, "temp.md"))


def test_read_nonexistent_concept():
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = os.path.join(tmpdir, "concepts")
        os.makedirs(concepts_dir)

        result = read_concept("does-not-exist", concepts_dir)
        assert result is None
