from typing import Callable, List, Optional

from .event import DoneEvent, Event, ToolEvent


class Plugin:
    def before_run(self, text: str) -> Optional[str]:
        return None

    def after_tool(self, event: ToolEvent) -> Optional[Event]:
        return None

    def after_done(self, event: DoneEvent) -> None:
        pass


class LoggerPlugin(Plugin):
    def __init__(self, callback: Callable = None):
        self.callback = callback or print

    def after_tool(self, event: ToolEvent):
        self.callback(f"[tool] {event.tool_name} → {event.result}")
        return None

    def after_done(self, event: DoneEvent):
        self.callback(f"[done] {event.content}")


class Pipeline:
    def __init__(self, plugins: List[Plugin] = None):
        self.plugins = plugins or []

    def process(self, events: List[Event]) -> List[Event]:
        output = []
        for ev in events:
            output.append(ev)
            if isinstance(ev, ToolEvent):
                for plugin in self.plugins:
                    extra = plugin.after_tool(ev)
                    if extra is not None:
                        output.append(extra)
            if isinstance(ev, DoneEvent):
                for plugin in self.plugins:
                    plugin.after_done(ev)
        return output
