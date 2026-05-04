import os
from src.knowledge.chunker import chunk_markdown, list_chunks


BOOK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge",
    "raw",
    "超越智商.md",
)


def test_chunker_on_real_book():
    if not os.path.exists(BOOK_PATH):
        return
    chunks = chunk_markdown(BOOK_PATH)
    assert len(chunks) > 50
    assert len(chunks) < 120
    for c in chunks:
        assert c["content"].strip(), f"Chunk {c['index']} is empty"
        assert len(c["content"]) <= 16000, f"Chunk {c['index']} exceeds 16K: {len(c['content'])}"
    assert chunks[0]["title"] == "front_matter"
    with_chapter = [c for c in chunks if c["chapter"]]
    assert len(with_chapter) > 40


def test_list_chunks_on_real_book():
    if not os.path.exists(BOOK_PATH):
        return
    info = list_chunks(BOOK_PATH)
    assert len(info) > 50
    for i in info:
        assert "content" not in i
        assert "char_count" in i
