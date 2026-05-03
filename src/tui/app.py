import subprocess

from textual.app import App, ComposeResult
from textual.widgets import Header, Input, RichLog, Static
from rich.markdown import Markdown
from rich.text import Text

from ..conversation import Conversation
from ..event import DoneEvent, ErrorEvent, ToolEvent


class BaizePawApp(App):
    CSS = """
    #log {
        height: 1fr;
        border: solid green;
        overflow-x: hidden;
        padding: 0 1;
    }
    #status {
        height: 1;
        background: $surface;
        color: $text-muted;
    }
    #input {
        dock: bottom;
    }
    """

    BINDINGS = [("y", "copy_last_response", "Copy last reply")]

    def __init__(self):
        super().__init__()
        self.chat_conversation = Conversation()
        self.coach_conversation = None
        self.active_conversation = self.chat_conversation
        self.mode = "chat"
        self._last_response = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="log", highlight=True, markup=False, wrap=True)
        yield Static("Ready", id="status")
        yield Input(placeholder="Type your message...", id="input")

    def on_mount(self):
        self.chat_conversation.start()
        self.set_interval(0.1, self._poll_events)

    def _handle_command(self, text: str) -> bool:
        if text == "/coach":
            self.mode = "coach"
            if self.coach_conversation is None:
                from ..coach import Coach
                import os

                knowledge_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "knowledge",
                )
                coach = Coach(knowledge_dir)
                self.coach_conversation = Conversation(core=coach.core)
                self.coach_conversation.start()
            self.active_conversation = self.coach_conversation
            self._update_status("Coach | /chat")
            return True
        elif text == "/chat":
            self.mode = "chat"
            self.active_conversation = self.chat_conversation
            self._update_status("Chat | /coach")
            return True
        return False

    def _update_status(self, text: str):
        try:
            self.query_one("#status", Static).update(text)
        except Exception:
            pass

    def on_input_submitted(self, message: Input.Submitted):
        text = message.value.strip()
        if not text:
            return
        log = self.query_one("#log")
        log.write(Text.from_markup(f"[bold bright_cyan]You:[/bold bright_cyan] {text}"))
        log.write("")
        self.query_one("#input", Input).value = ""

        if self._handle_command(text):
            return

        self.query_one("#status", Static).update("Thinking...")
        self.active_conversation.submit(text)

    def _poll_events(self):
        events = self.active_conversation.poll()
        if not events:
            return
        log = self.query_one("#log")
        for ev in events:
            if isinstance(ev, ToolEvent):
                log.write(
                    Text.from_markup(
                        f"[dim grey70]$ {ev.tool_name}({ev.params}) → {ev.result}[/dim grey70]"
                    )
                )
            elif isinstance(ev, DoneEvent):
                self._last_response = ev.content
                log.write(Text.from_markup("[bold bright_green]BaizePaw:[/bold bright_green]"))
                log.write(Markdown(ev.content))
                log.write("")
                status = "Coach | /chat" if self.mode == "coach" else "Chat | /coach"
                self.query_one("#status", Static).update(f"{status} | y=copy")
            elif isinstance(ev, ErrorEvent):
                log.write(Text.from_markup(f"[bold red]Error:[/bold red] {ev.message}"))
                log.write("")
                self.query_one("#status", Static).update("Ready")

    def action_copy_last_response(self):
        if not self._last_response:
            return
        try:
            subprocess.run(
                ["pbcopy"],
                input=self._last_response.encode("utf-8"),
                check=True,
            )
            self.query_one("#status", Static).update("Copied! | y=copy")
        except Exception:
            pass

    def on_unmount(self):
        self.chat_conversation.stop()
        if self.coach_conversation is not None:
            self.coach_conversation.stop()
