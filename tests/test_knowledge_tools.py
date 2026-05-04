import os
import tempfile
from src.knowledge import init_knowledge_dir
from src.knowledge.index import add_to_index
from src.knowledge.concept import create_concept
from src.knowledge.progress import init_progress
from src.tools.knowledge_tools import create_knowledge_tools


def _setup_knowledge(tmpdir):
    knowledge_dir = init_knowledge_dir(tmpdir)
    concepts_dir = os.path.join(knowledge_dir, "concepts")
    index_path = os.path.join(knowledge_dir, "index.md")
    progress_path = os.path.join(knowledge_dir, "progress.md")

    create_concept("variables", "# Variables\nVariables store values.", concepts_dir)
    create_concept("functions", "# Functions\nFunctions are reusable blocks.", concepts_dir)
    add_to_index("variables", "Variables store values.", index_path)
    add_to_index("functions", "Functions are reusable blocks.", index_path)
    init_progress(progress_path)

    return knowledge_dir


def test_create_knowledge_tools_returns_eight_tools():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        assert isinstance(tools, list)
        assert len(tools) == 8
        names = [t.name for t in tools]
        assert "knowledge_index" in names
        assert "knowledge_concept" in names
        assert "progress_read" in names
        assert "progress_update" in names
        assert "ingest_list_raw" in names
        assert "ingest_read_chunk" in names
        assert "ingest_write_concept" in names
        assert "ingest_log" in names


def test_knowledge_index_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        index_tool = next(t for t in tools if t.name == "knowledge_index")
        result = index_tool.fn()
        assert "variables" in result
        assert "functions" in result


def test_knowledge_concept_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        concept_tool = next(t for t in tools if t.name == "knowledge_concept")
        result = concept_tool.fn(name="variables")
        assert "Variables" in result


def test_knowledge_concept_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        concept_tool = next(t for t in tools if t.name == "knowledge_concept")
        result = concept_tool.fn(name="nonexistent")
        assert "not found" in result.lower() or "None" in result


def test_progress_read_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        read_tool = next(t for t in tools if t.name == "progress_read")
        result = read_tool.fn()
        assert "current" in result.lower() or "进度" in result


def test_progress_update_tool_set_current():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        update_tool = next(t for t in tools if t.name == "progress_update")
        result = update_tool.fn(action="set_current", name="variables")
        assert "variables" in result

        read_tool = next(t for t in tools if t.name == "progress_read")
        result = read_tool.fn()
        assert "variables" in result


def test_progress_update_tool_mark_mastered():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        update_tool = next(t for t in tools if t.name == "progress_update")

        update_tool.fn(action="set_current", name="variables")
        result = update_tool.fn(action="mark_mastered", name="variables")
        assert "variables" in result


def test_ingest_list_raw_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        raw_dir = os.path.join(knowledge_dir, "raw")
        with open(os.path.join(raw_dir, "test-book.md"), "w") as f:
            f.write("# Test Book\n\nContent here.")
        tools = create_knowledge_tools(knowledge_dir)
        list_tool = next(t for t in tools if t.name == "ingest_list_raw")
        result = list_tool.fn()
        assert "test-book.md" in result


def test_ingest_list_raw_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        list_tool = next(t for t in tools if t.name == "ingest_list_raw")
        result = list_tool.fn()
        assert "no markdown" in result.lower() or "empty" in result.lower() or "未找到" in result


def test_ingest_read_chunk_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        raw_dir = os.path.join(knowledge_dir, "raw")
        with open(os.path.join(raw_dir, "test-book.md"), "w") as f:
            f.write("# Book\n\n## Chapter 1\n\n### Alpha\n\nAlpha content.\n\n### Beta\n\nBeta content.\n")
        tools = create_knowledge_tools(knowledge_dir)
        read_tool = next(t for t in tools if t.name == "ingest_read_chunk")
        result = read_tool.fn(filename="test-book.md", chunk_index=1)
        assert "Beta" in result


def test_ingest_read_chunk_out_of_range():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        raw_dir = os.path.join(knowledge_dir, "raw")
        with open(os.path.join(raw_dir, "test-book.md"), "w") as f:
            f.write("# Book\n\n## Chapter 1\n\n### Alpha\n\nAlpha content.\n")
        tools = create_knowledge_tools(knowledge_dir)
        read_tool = next(t for t in tools if t.name == "ingest_read_chunk")
        result = read_tool.fn(filename="test-book.md", chunk_index=99)
        assert "out of range" in result.lower() or "超出" in result


def test_ingest_write_concept_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        write_tool = next(t for t in tools if t.name == "ingest_write_concept")
        result = write_tool.fn(
            name="rational-thinking",
            summary="The ability to think and act rationally",
            content="Rational thinking is the ability to think based on reason.",
        )
        assert "rational-thinking" in result or "created" in result.lower() or "创建" in result
        concept_tool = next(t for t in tools if t.name == "knowledge_concept")
        concept = concept_tool.fn(name="rational-thinking")
        assert "Rational thinking" in concept
        index_tool = next(t for t in tools if t.name == "knowledge_index")
        index = index_tool.fn()
        assert "rational-thinking" in index


def test_ingest_log_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        log_tool = next(t for t in tools if t.name == "ingest_log")
        result = log_tool.fn(
            operation="ingest",
            source="test-book.md",
            detail="Extracted 5 concepts",
        )
        assert "ingest" in result.lower() or "记录" in result
        log_path = os.path.join(knowledge_dir, "log.md")
        assert os.path.exists(log_path)
        with open(log_path) as f:
            content = f.read()
        assert "test-book.md" in content
