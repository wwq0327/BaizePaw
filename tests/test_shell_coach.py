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
