from .tool_base import Tool


def _calc_impl(expr: str) -> float:
    """安全计算器，只支持基本数学运算"""
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expr):
        raise ValueError("Invalid characters in expression")
    try:
        return eval(expr)
    except Exception as e:
        raise ValueError(f"Calculation error: {e}")


calculator_tool = Tool(
    name="calculator",
    description="数学计算，支持四则运算和括号",
    parameters={
        "type": "object",
        "properties": {
            "expr": {
                "type": "string",
                "description": "数学表达式，如 2+2 或 (3+5)*2",
            }
        },
        "required": ["expr"],
    },
    fn=_calc_impl,
)
