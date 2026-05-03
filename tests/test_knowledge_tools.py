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


def test_create_knowledge_tools_returns_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        tools = create_knowledge_tools(knowledge_dir)
        assert isinstance(tools, list)
        assert len(tools) == 4
        names = [t.name for t in tools]
        assert "knowledge_index" in names
        assert "knowledge_concept" in names
        assert "progress_read" in names
        assert "progress_update" in names


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
