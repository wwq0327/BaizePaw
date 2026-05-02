def calc_tool(expr: str) -> float:
    """安全计算器，只支持基本数学运算"""
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expr):
        raise ValueError("Invalid characters in expression")
    try:
        result = eval(expr)
        return result
    except Exception as e:
        raise ValueError(f"Calculation error: {e}")
