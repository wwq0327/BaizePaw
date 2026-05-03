import os
import json
from .tool_base import Tool
from ..knowledge.index import read_index
from ..knowledge.concept import read_concept
from ..knowledge.progress import (
    read_progress,
    set_current,
    mark_mastered,
    mark_stuck,
    mark_skipped,
)


def create_knowledge_tools(knowledge_dir: str) -> list:
    concepts_dir = os.path.join(knowledge_dir, "concepts")
    index_path = os.path.join(knowledge_dir, "index.md")
    progress_path = os.path.join(knowledge_dir, "progress.md")

    def _knowledge_index():
        return read_index(index_path) or "Index is empty."

    def _knowledge_concept(name: str):
        content = read_concept(name, concepts_dir)
        if content is None:
            return f"Concept '{name}' not found."
        return content

    def _progress_read():
        progress = read_progress(progress_path)
        return json.dumps(progress, ensure_ascii=False)

    def _progress_update(action: str, name: str):
        if action == "set_current":
            set_current(name, progress_path)
            return f"Current topic set to: {name}"
        elif action == "mark_mastered":
            mark_mastered(name, progress_path)
            return f"Marked as mastered: {name}"
        elif action == "mark_stuck":
            mark_stuck(name, progress_path)
            return f"Marked as stuck: {name}"
        elif action == "mark_skipped":
            mark_skipped(name, progress_path)
            return f"Marked as skipped: {name}"
        else:
            return f"Unknown action: {action}"

    return [
        Tool(
            name="knowledge_index",
            description="读取知识库索引，查看所有知识点列表",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
            fn=_knowledge_index,
        ),
        Tool(
            name="knowledge_concept",
            description="读取某个知识点的详细内容",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "知识点名称（kebab-case）",
                    }
                },
                "required": ["name"],
            },
            fn=_knowledge_concept,
        ),
        Tool(
            name="progress_read",
            description="读取当前学习进度",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
            fn=_progress_read,
        ),
        Tool(
            name="progress_update",
            description="更新学习进度：设置当前知识点、标记掌握/卡住/跳过",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "操作类型：set_current / mark_mastered / mark_stuck / mark_skipped",
                    },
                    "name": {
                        "type": "string",
                        "description": "知识点名称",
                    },
                },
                "required": ["action", "name"],
            },
            fn=_progress_update,
        ),
    ]
