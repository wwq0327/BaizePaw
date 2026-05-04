import re


def chunk_markdown(path: str, max_chars: int = 15000) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    has_h3 = bool(re.search(r"^### ", text, re.MULTILINE))
    sections = []
    current_chapter = ""

    # 收集 front matter（第一个 ## 之前的内容）
    body_start = 0
    for i, line in enumerate(lines):
        if re.match(r"^## ", line):
            body_start = i
            break
    else:
        body_start = len(lines)

    if body_start > 0:
        # 跳过 h1 行（书名），只保留实质内容
        front_lines = [l for l in lines[:body_start] if not re.match(r"^# [^#]", l)]
        front_content = "\n".join(front_lines).strip()
        if front_content:
            sections.append({
                "title": "front_matter",
                "chapter": "",
                "content": front_content,
            })

    # 按标题拆分正文
    current_title = None
    current_lines = []

    def flush():
        nonlocal current_title, current_lines
        if current_title is not None and current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                sections.append({
                    "title": current_title,
                    "chapter": current_chapter,
                    "content": content,
                })
        current_title = None
        current_lines = []

    for i in range(body_start, len(lines)):
        line = lines[i]
        h2_match = re.match(r"^## (.+)", line)
        h3_match = re.match(r"^### (.+)", line)

        if has_h3 and h3_match:
            flush()
            current_title = h3_match.group(1).strip()
            current_lines = []
        elif not has_h3 and h2_match:
            flush()
            current_title = h2_match.group(1).strip()
            current_chapter = current_title
            current_lines = []
        elif h2_match:
            flush()
            current_chapter = h2_match.group(1).strip()
        else:
            if current_title is not None:
                current_lines.append(line)

    flush()

    # 超长段落二次分割
    result = []
    idx = 0
    for sec in sections:
        if len(sec["content"]) <= max_chars:
            sec["index"] = idx
            sec["char_count"] = len(sec["content"])
            result.append(sec)
            idx += 1
        else:
            paragraphs = re.split(r"\n\n+", sec["content"])
            # 单个段落超过 max_chars 时强制切分
            split_paras = []
            for para in paragraphs:
                if len(para) > max_chars:
                    for j in range(0, len(para), max_chars):
                        split_paras.append(para[j:j + max_chars])
                else:
                    split_paras.append(para)
            paragraphs = split_paras
            buf = []
            buf_len = 0
            for para in paragraphs:
                if buf_len + len(para) + 2 > max_chars and buf:
                    chunk_content = "\n\n".join(buf).strip()
                    result.append({
                        "index": idx,
                        "title": sec["title"],
                        "chapter": sec["chapter"],
                        "content": chunk_content,
                        "char_count": len(chunk_content),
                    })
                    idx += 1
                    buf = []
                    buf_len = 0
                buf.append(para)
                buf_len += len(para) + 2
            if buf:
                chunk_content = "\n\n".join(buf).strip()
                result.append({
                    "index": idx,
                    "title": sec["title"],
                    "chapter": sec["chapter"],
                    "content": chunk_content,
                    "char_count": len(chunk_content),
                })
                idx += 1

    return result


def list_chunks(path: str, max_chars: int = 15000) -> list[dict]:
    chunks = chunk_markdown(path, max_chars=max_chars)
    return [
        {
            "index": c["index"],
            "title": c["title"],
            "chapter": c["chapter"],
            "char_count": c["char_count"],
        }
        for c in chunks
    ]
