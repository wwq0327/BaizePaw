import os
import json
from .tool_base import Tool
from ..knowledge.index import read_index, add_to_index
from ..knowledge.concept import read_concept, create_concept
from ..knowledge.log import append_log
from ..knowledge.chunker import chunk_markdown
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
    log_path = os.path.join(knowledge_dir, "log.md")

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

    def _ingest_list_raw():
        raw_dir = os.path.join(knowledge_dir, "raw")
        if not os.path.exists(raw_dir):
            return "Raw directory not found."
        files = [f for f in os.listdir(raw_dir) if f.endswith(".md")]
        if not files:
            return "No markdown files found in raw/."
        entries = []
        for f in sorted(files):
            size = os.path.getsize(os.path.join(raw_dir, f))
            entries.append(f"- {f} ({size} bytes)")
        return "\n".join(entries)

    def _ingest_read_chunk(filename: str, chunk_index: int):
        raw_path = os.path.join(knowledge_dir, "raw", filename)
        if not os.path.exists(raw_path):
            return f"File not found: {filename}"
        chunks = chunk_markdown(raw_path)
        if chunk_index < 0 or chunk_index >= len(chunks):
            return f"Chunk index {chunk_index} out of range (0-{len(chunks)-1})."
        c = chunks[chunk_index]
        header = ""
        if c["chapter"]:
            header = f"## {c['chapter']}\n"
        header += f"### {c['title']}\n\n"
        return header + c["content"]

    def _ingest_write_concept(name: str, summary: str, content: str):
        create_concept(name, content, concepts_dir)
        add_to_index(name, summary, index_path)
        return f"Created concept: {name}"

    def _ingest_log(operation: str, source: str, detail: str):
        append_log(operation, source, detail, log_path)
        return f"Logged: {operation} | {source}"

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
        Tool(
            name="ingest_list_raw",
            description="列出 knowledge/raw/ 中的 Markdown 文件（待 ingest 的书）",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=_ingest_list_raw,
        ),
        Tool(
            name="ingest_read_chunk",
            description="读取指定书的某个分块内容（按章节分割，每次返回一个分块）",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "raw/ 中的文件名"},
                    "chunk_index": {"type": "integer", "description": "分块索引（从 0 开始）"},
                },
                "required": ["filename", "chunk_index"],
            },
            fn=_ingest_read_chunk,
        ),
        Tool(
            name="ingest_write_concept",
            description="创建知识点页面并添加到索引（原子操作）",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "知识点名称（kebab-case）"},
                    "summary": {"type": "string", "description": "一句话摘要"},
                    "content": {"type": "string", "description": "知识点详细内容（Markdown）"},
                },
                "required": ["name", "summary", "content"],
            },
            fn=_ingest_write_concept,
        ),
        Tool(
            name="ingest_log",
            description="记录 ingest 操作日志（如：扫描完成、概念创建完成）",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "description": "操作类型：ingest_scan / ingest_concept / ingest_complete"},
                    "source": {"type": "string", "description": "来源文件名"},
                    "detail": {"type": "string", "description": "操作详情"},
                },
                "required": ["operation", "source", "detail"],
            },
            fn=_ingest_log,
        ),
    ]
