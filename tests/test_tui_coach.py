from unittest.mock import MagicMock, patch
from src.tui.app import BaizePawApp


def test_app_has_chat_and_coach_conversations():
    with patch("src.tui.app.Conversation") as MockConv:
        mock_conv = MagicMock()
        MockConv.return_value = mock_conv
        app = BaizePawApp()
        assert hasattr(app, "chat_conversation")
        assert hasattr(app, "coach_conversation")
        assert app.active_conversation is app.chat_conversation


def test_coach_command_switches_mode():
    with patch("src.tui.app.Conversation") as MockConv:
        mock_conv = MagicMock()
        MockConv.return_value = mock_conv
        app = BaizePawApp()
        assert app.mode == "chat"
        app._handle_command("/coach")
        assert app.mode == "coach"
        assert app.active_conversation is app.coach_conversation


def test_chat_command_switches_back():
    with patch("src.tui.app.Conversation") as MockConv:
        mock_conv = MagicMock()
        MockConv.return_value = mock_conv
        app = BaizePawApp()
        app._handle_command("/coach")
        assert app.mode == "coach"
        app._handle_command("/chat")
        assert app.mode == "chat"
        assert app.active_conversation is app.chat_conversation


def test_ingest_command_switches_to_coach():
    with patch("src.tui.app.Conversation") as MockConv:
        mock_conv = MagicMock()
        MockConv.return_value = mock_conv
        app = BaizePawApp()
        assert app.mode == "chat"
        handled = app._handle_command("/ingest")
        assert handled is True
        assert app.mode == "coach"
