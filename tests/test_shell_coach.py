from unittest.mock import MagicMock, patch
from src.shell import Shell


def test_shell_has_mode_switching():
    with patch("src.shell.Conversation") as MockConv:
        mock_conv = MagicMock()
        MockConv.return_value = mock_conv
        shell = Shell()
        assert shell.mode == "chat"
        shell._handle_command("/coach")
        assert shell.mode == "coach"
        shell._handle_command("/chat")
        assert shell.mode == "chat"


def test_ingest_command_switches_to_coach():
    with patch("src.shell.Conversation") as MockConv:
        mock_conv = MagicMock()
        MockConv.return_value = mock_conv
        shell = Shell()
        assert shell.mode == "chat"
        handled = shell._handle_command("/ingest")
        assert handled is True
        assert shell.mode == "coach"
