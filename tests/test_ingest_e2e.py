import os
import tempfile
from unittest.mock import patch, MagicMock
from src.knowledge import init_knowledge_dir
from src.coach import Coach
from src.llm_client import ChatResponse


def _tc(name, arguments, call_id=None):
    """构造 tool_calls 条目。"""
    return {
        "id": call_id or f"call_{name}",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def test_ingest_e2e_with_mock_llm():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_dir = init_knowledge_dir(tmpdir)

        raw_dir = os.path.join(knowledge_dir, "raw")
        with open(os.path.join(raw_dir, "mini-book.md"), "w") as f:
            f.write(
                "# Mini Book\n\n"
                "## Chapter 1\n\n"
                "### Rationality\n\n"
                "Rationality is the ability to think based on reason.\n\n"
                "### Cognitive Bias\n\n"
                "Cognitive biases are systematic deviations from rationality.\n"
            )

        mock_client = MagicMock()

        # Phase 1: Scan
        scan_responses = [
            ChatResponse(content=None, tool_calls=[_tc("ingest_list_raw", '{}')]),
            ChatResponse(content=None, tool_calls=[_tc("ingest_read_chunk", '{"filename":"mini-book.md","chunk_index":0}')]),
            ChatResponse(content=None, tool_calls=[_tc("ingest_read_chunk", '{"filename":"mini-book.md","chunk_index":1}')]),
            ChatResponse(content="I found 2 concepts: rationality and cognitive-bias. Shall I proceed?"),
        ]
        # Phase 2: Write
        write_responses = [
            ChatResponse(content=None, tool_calls=[_tc("ingest_write_concept", '{"name":"rationality","summary":"Thinking based on reason","content":"Rationality is the ability to think based on reason rather than emotion."}')]),
            ChatResponse(content=None, tool_calls=[_tc("ingest_write_concept", '{"name":"cognitive-bias","summary":"Systematic deviation from rationality","content":"Cognitive biases are systematic patterns of deviation from rationality in judgment."}')]),
            ChatResponse(content=None, tool_calls=[_tc("ingest_log", '{"operation":"ingest_complete","source":"mini-book.md","detail":"Extracted 2 concepts: rationality, cognitive-bias"}')]),
            ChatResponse(content="Ingest complete! Created 2 concept pages."),
        ]
        mock_client.chat.side_effect = scan_responses + write_responses

        with patch("src.core.LLMClient", return_value=mock_client):
            coach = Coach(knowledge_dir)

            # Phase 1: Start ingest, scan the book
            events1 = list(coach.run_iter("请开始 ingest 流程"))
            tool_events1 = [e for e in events1 if hasattr(e, "tool_name")]
            tool_names1 = [e.tool_name for e in tool_events1]
            assert "ingest_list_raw" in tool_names1
            assert "ingest_read_chunk" in tool_names1

            # Phase 2: User confirms, write concepts
            events2 = list(coach.run_iter("继续，创建这些知识点"))
            tool_events2 = [e for e in events2 if hasattr(e, "tool_name")]
            tool_names2 = [e.tool_name for e in tool_events2]
            assert "ingest_write_concept" in tool_names2
            assert "ingest_log" in tool_names2

        concepts_dir = os.path.join(knowledge_dir, "concepts")
        assert os.path.exists(os.path.join(concepts_dir, "rationality.md"))
        assert os.path.exists(os.path.join(concepts_dir, "cognitive-bias.md"))

        index_path = os.path.join(knowledge_dir, "index.md")
        with open(index_path) as f:
            index_content = f.read()
        assert "rationality" in index_content
        assert "cognitive-bias" in index_content

        log_path = os.path.join(knowledge_dir, "log.md")
        with open(log_path) as f:
            log_content = f.read()
        assert "mini-book.md" in log_content
