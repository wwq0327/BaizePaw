import os
import tempfile
from unittest.mock import MagicMock, patch

from src.knowledge import init_knowledge_dir
from src.knowledge.concept import create_concept
from src.knowledge.index import add_to_index
from src.knowledge.progress import init_progress
from src.coach import Coach
from src.llm_client import ChatResponse


def _setup_knowledge(tmpdir):
    knowledge_dir = init_knowledge_dir(tmpdir)
    concepts_dir = os.path.join(knowledge_dir, "concepts")
    index_path = os.path.join(knowledge_dir, "index.md")
    progress_path = os.path.join(knowledge_dir, "progress.md")

    create_concept("variables", "# Variables\nVariables store values.", concepts_dir)
    add_to_index("variables", "Variables store values.", index_path)
    init_progress(progress_path)

    return knowledge_dir


def test_coach_creates_with_knowledge_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        mock_client = MagicMock()
        mock_client.chat.return_value = "OK"
        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)
        assert coach.core is not None
        assert "阅读教练" in coach.core.role_prompt


def test_coach_has_readonly_tools():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        mock_client = MagicMock()
        mock_client.chat.return_value = "OK"
        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)
        tool_names = set(coach.core.dispatcher.tools.keys())
        assert "file_read" in tool_names
        assert "list_dir" in tool_names
        assert "find_file" in tool_names
        assert "grep_file" in tool_names
        assert "calculator" in tool_names
        assert "search" in tool_names
        assert "knowledge_index" in tool_names
        assert "knowledge_concept" in tool_names
        assert "progress_read" in tool_names
        assert "progress_update" in tool_names


def test_coach_no_write_tools():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        mock_client = MagicMock()
        mock_client.chat.return_value = "OK"
        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)
        tool_names = set(coach.core.dispatcher.tools.keys())
        assert "file_write" not in tool_names
        assert "file_append" not in tool_names
        assert "delete_file" not in tool_names
        assert "move_file" not in tool_names
        assert "copy_file" not in tool_names


def test_coach_run_iter_delegates_to_core():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        mock_client = MagicMock()
        mock_client.chat.return_value = ChatResponse(content="Let's start learning!")
        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)
            events = list(coach.run_iter("Hello"))
        assert len(events) >= 1
        assert any("Let's start learning!" in str(e) for e in events)


def test_coach_dispatches_knowledge_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            ChatResponse(
                content=None,
                tool_calls=[{
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "knowledge_index", "arguments": '{}'},
                }],
            ),
            ChatResponse(content="Here are the topics."),
        ]
        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)
            events = list(coach.run_iter("What can I learn?"))
        tool_events = [e for e in events if hasattr(e, "tool_name")]
        assert len(tool_events) >= 1
        assert tool_events[0].tool_name == "knowledge_index"


def test_coach_has_ingest_tools():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = _setup_knowledge(tmpdir)
        mock_client = MagicMock()
        mock_client.chat.return_value = "OK"
        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)
        tool_names = set(coach.core.dispatcher.tools.keys())
        assert "ingest_list_raw" in tool_names
        assert "ingest_read_chunk" in tool_names
        assert "ingest_write_concept" in tool_names
        assert "ingest_log" in tool_names
