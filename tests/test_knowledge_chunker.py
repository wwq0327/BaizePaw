import os
import tempfile
from src.knowledge.chunker import chunk_markdown, list_chunks


def test_chunk_single_section():
    md = "# Book\n\n## Chapter 1\n\n### Section A\n\nContent A.\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md)
        path = f.name
    try:
        chunks = chunk_markdown(path)
        assert len(chunks) == 1
        assert "Section A" in chunks[0]["title"]
        assert "Content A" in chunks[0]["content"]
        assert chunks[0]["index"] == 0
    finally:
        os.unlink(path)


def test_chunk_multiple_sections():
    md = (
        "# Book\n\n## Chapter 1\n\n"
        "### Alpha\n\nAlpha content.\n\n"
        "### Beta\n\nBeta content.\n\n"
        "### Gamma\n\nGamma content.\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md)
        path = f.name
    try:
        chunks = chunk_markdown(path)
        assert len(chunks) == 3
        assert chunks[0]["title"] == "Alpha"
        assert chunks[1]["title"] == "Beta"
        assert chunks[2]["title"] == "Gamma"
    finally:
        os.unlink(path)


def test_chunk_includes_chapter_context():
    md = (
        "# Book\n\n"
        "## Chapter 1\n\n### Section A\n\nContent A.\n\n"
        "## Chapter 2\n\n### Section B\n\nContent B.\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md)
        path = f.name
    try:
        chunks = chunk_markdown(path)
        assert chunks[0]["chapter"] == "Chapter 1"
        assert chunks[1]["chapter"] == "Chapter 2"
    finally:
        os.unlink(path)


def test_chunk_oversize_split():
    long_content = "Word " * 4000
    md = f"# Book\n\n## Chapter 1\n\n### Big Section\n\n{long_content}\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md)
        path = f.name
    try:
        chunks = chunk_markdown(path, max_chars=10000)
        assert len(chunks) > 1
        for c in chunks:
            assert "Big Section" in c["title"]
    finally:
        os.unlink(path)


def test_chunk_h2_only_sections():
    md = "# Book\n\n## Chapter 1\n\nSome intro text.\n\n## Chapter 2\n\nMore text.\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md)
        path = f.name
    try:
        chunks = chunk_markdown(path)
        assert len(chunks) == 2
        assert "Chapter 1" in chunks[0]["title"]
        assert "Chapter 2" in chunks[1]["title"]
    finally:
        os.unlink(path)


def test_list_chunks():
    md = (
        "# Book\n\n## Chapter 1\n\n"
        "### Alpha\n\nAlpha content.\n\n"
        "### Beta\n\nBeta content.\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md)
        path = f.name
    try:
        info = list_chunks(path)
        assert len(info) == 2
        assert info[0]["index"] == 0
        assert info[0]["title"] == "Alpha"
        assert "char_count" in info[0]
        assert "content" not in info[0]
    finally:
        os.unlink(path)


def test_chunk_skips_front_matter():
    md = "# Book Title\n\nAuthor: Someone\n\nTable of Contents\n\n## Chapter 1\n\n### Intro\n\nHello.\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md)
        path = f.name
    try:
        chunks = chunk_markdown(path)
        assert len(chunks) >= 2
        assert chunks[0]["title"] == "front_matter"
    finally:
        os.unlink(path)
