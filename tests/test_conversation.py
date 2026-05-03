import time
from unittest.mock import MagicMock, patch

from src.conversation import Conversation
from src.event import DoneEvent, ErrorEvent, ToolEvent


def _make_conversation(mock_core_events):
    """创建 Conversation，Core.run_iter 返回预设事件"""
    with patch("src.conversation.Core") as MockCore:
        mock_core = MagicMock()
        mock_core.run_iter.return_value = iter(mock_core_events)
        MockCore.return_value = mock_core
        conv = Conversation()
        conv._core = mock_core
        conv.start()
        return conv


def test_submit_does_not_block():
    conv = _make_conversation([DoneEvent(content="hi")])
    start = time.time()
    conv.submit("hello")
    elapsed = time.time() - start
    assert elapsed < 0.1  # submit 应该立即返回
    # 等待 worker 处理完
    time.sleep(0.3)
    conv.stop()


def test_poll_returns_events():
    conv = _make_conversation([DoneEvent(content="hi")])
    conv.submit("hello")
    time.sleep(0.3)
    events = conv.poll()
    assert len(events) >= 1
    assert any(isinstance(e, DoneEvent) for e in events)
    conv.stop()


def test_multiple_submits_queue():
    events = [DoneEvent(content="first"), DoneEvent(content="second")]
    conv = _make_conversation(events)
    conv.submit("one")
    conv.submit("two")
    time.sleep(0.5)
    all_events = conv.poll()
    # worker 会按顺序处理两条输入
    assert len(all_events) >= 2
    conv.stop()


def test_worker_error_yields_error_event():
    mock_core = MagicMock()
    mock_core.run_iter.side_effect = Exception("boom")
    with patch("src.conversation.Core", return_value=mock_core):
        conv = Conversation()
        conv._core = mock_core
        conv.start()
        conv.submit("test")
        time.sleep(0.3)
        events = conv.poll()
        assert any(isinstance(e, ErrorEvent) for e in events)
        conv.stop()
