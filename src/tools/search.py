from .tool_base import Tool


def _search_impl(query: str) -> str:
    """网络搜索（暂未实现）"""
    return f"Search not implemented yet. Query: {query}"


search_tool = Tool(
    name="search",
    description="搜索网络信息（暂未实现）",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索关键词",
            }
        },
        "required": ["query"],
    },
    fn=_search_impl,
)
