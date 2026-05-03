import os
from typing import Generator

from .core import Core
from .event import Event
from .tools.file_ops import read_file_tool, list_dir_tool, find_file_tool, grep_file_tool
from .tools.calculator import calculator_tool
from .tools.search import search_tool
from .tools.knowledge_tools import create_knowledge_tools


class Coach:
    def __init__(self, knowledge_dir: str):
        coach_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "COACH.md",
        )
        knowledge_tools = create_knowledge_tools(knowledge_dir)
        coach_tools = [
            read_file_tool,
            list_dir_tool,
            find_file_tool,
            grep_file_tool,
            calculator_tool,
            search_tool,
        ] + knowledge_tools

        self.core = Core(role_path=coach_path, tools=coach_tools)

    def run_iter(self, text: str) -> Generator[Event, None, None]:
        yield from self.core.run_iter(text)
