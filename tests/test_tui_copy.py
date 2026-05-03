from unittest.mock import MagicMock, patch

from src.tui.app import BaizePawApp


def test_copy_keybinding_exists():
    """验证 app 有 copy 相关的 key binding"""
    app = BaizePawApp()
    assert hasattr(app, "action_copy_last_response")


def test_copy_last_response_with_content():
    app = BaizePawApp()
    # 模拟有 DoneEvent 内容
    app._last_response = "Hello world"

    with patch("subprocess.run") as mock_run:
        app.action_copy_last_response()
        mock_run.assert_called_once()
        # 验证传给了 pbcopy
        args = mock_run.call_args[0][0]
        assert args[0] == "pbcopy"


def test_copy_last_response_without_content():
    """没有内容时不调 pbcopy"""
    app = BaizePawApp()
    app._last_response = None

    with patch("subprocess.run") as mock_run:
        app.action_copy_last_response()
        mock_run.assert_not_called()
