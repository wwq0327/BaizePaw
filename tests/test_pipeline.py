from src.pipeline import LoggerPlugin, Pipeline, Plugin
from src.event import DoneEvent, ToolEvent


def test_pipeline_no_plugins():
    p = Pipeline([])
    events = list(p.process([DoneEvent(content="hi")]))
    assert len(events) == 1
    assert events[0].content == "hi"


def test_logger_plugin():
    logs = []
    plugin = LoggerPlugin(callback=logs.append)
    p = Pipeline([plugin])
    list(p.process([DoneEvent(content="hi")]))
    assert len(logs) == 1


def test_after_tool_returns_system_message():
    class AddMsg(Plugin):
        def after_tool(self, event: ToolEvent):
            return DoneEvent(content=f"[system] {event.tool_name} done")

    p = Pipeline([AddMsg()])
    events = list(p.process([ToolEvent(tool_name="calc", result="2")]))
    # 原始 ToolEvent + 插件追加的 DoneEvent
    assert len(events) == 2
    assert events[1].content == "[system] calc done"
