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

    def __init__(self):
        super().__init__()
        self.conversation = Conversation()

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="log", highlight=True, markup=False, wrap=True)
        yield Static("Ready", id="status")
        yield Input(placeholder="Type your message...", id="input")

    def on_mount(self):
        self.conversation.start()
        self.set_interval(0.1, self._poll_events)

    def on_input_submitted(self, message: Input.Submitted):
        text = message.value.strip()
        if not text:
            return
        log = self.query_one("#log")
        log.write(Text.from_markup(f"[bold bright_cyan]You:[/bold bright_cyan] {text}"))
        log.write("")
        self.query_one("#input", Input).value = ""
        self.query_one("#status", Static).update("Thinking...")
        self.conversation.submit(text)

    def _poll_events(self):
        events = self.conversation.poll()
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
                log.write(Text.from_markup("[bold bright_green]BaizePaw:[/bold bright_green]"))
                log.write(Markdown(ev.content))
                log.write("")
                self.query_one("#status", Static).update("Ready")
            elif isinstance(ev, ErrorEvent):
                log.write(Text.from_markup(f"[bold red]Error:[/bold red] {ev.message}"))
                log.write("")
                self.query_one("#status", Static).update("Ready")

    def on_unmount(self):
        self.conversation.stop()
