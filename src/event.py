from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union


Event = Union["ToolEvent", "DoneEvent", "ErrorEvent"]


@dataclass
class ToolEvent:
    tool_name: str
    params: Dict[str, Any] = field(default_factory=dict)
    result: str = ""
    command: Optional[str] = None


@dataclass
class DoneEvent:
    content: str


@dataclass
class ErrorEvent:
    message: str
