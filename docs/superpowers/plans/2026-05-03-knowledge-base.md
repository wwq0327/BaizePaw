# v0.4 知识库构建 Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build a markdown-based knowledge base system that an LLM agent can use to ingest a book and produce interlinked concept pages.

**Architecture:** `src/knowledge/` module provides schema loading, concept page CRUD, index management, and log management. The Agent (LLM) orchestrates the ingest workflow by reading raw sources, extracting concepts, and writing pages through these utilities.

**Tech Stack:** Python 3.12, pytest, no new dependencies

**Refs:** Spec at `docs/superpowers/specs/2026-05-03-reading-coach-design.md`

---

## File Map

| File | Responsibility |
|------|---------------|
| `knowledge/KNOWLEDGE_SCHEMA.md` | Schema rules — templates, naming conventions, link format |
| `src/knowledge/__init__.py` | Module init, `init_knowledge_dir()` |
| `src/knowledge/schema.py` | `load_schema()` — read schema file |
| `src/knowledge/concept.py` | `create_concept()`, `read_concept()`, `update_concept()`, `delete_concept()` |
| `src/knowledge/index.py` | `add_to_index()`, `list_index()`, `search_index()` |
| `src/knowledge/log.py` | `append_log()` — timestamped entries |
| `tests/test_knowledge_schema.py` | Schema loading tests |
| `tests/test_knowledge_concept.py` | Concept CRUD tests |
| `tests/test_knowledge_index.py` | Index management tests |
| `tests/test_knowledge_log.py` | Log management tests |

---

### Task 1: Directory structure and KNOWLEDGE_SCHEMA.md

**Files:**
- Create: `knowledge/KNOWLEDGE_SCHEMA.md`
- Create: `src/knowledge/__init__.py`
- Create: `src/knowledge/schema.py`
- Create: `tests/test_knowledge_schema.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_knowledge_schema.py
import os
import tempfile
from src.knowledge.schema import load_schema


def test_load_schema_returns_content():
    content = load_schema()
    assert "concept" in content
    assert "index" in content


def test_load_schema_custom_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test Schema\n## concept\nname: test")
        path = f.name
    try:
        content = load_schema(path)
        assert "Test Schema" in content
    finally:
        os.unlink(path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_knowledge_schema.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.knowledge.schema'`


- [ ] **Step 3: Write minimal implementation**

Create `knowledge/KNOWLEDGE_SCHEMA.md`:
```markdown
# Knowledge Schema

## concept
Each concept page follows this template:

```markdown
# [Concept Name]

> Source: [book-name]
> Tags: [tag1], [tag2]

## 是什么
[One sentence definition]

## 详解
[Key explanation, 3-5 paragraphs]

## 示例
\`\`\`python
# code example
\`\`\`

## 易混淆点
- [Point 1]
- [Point 2]

## 相关概念
- [Related concept](concept-name.md)
- [Related concept](other-concept.md)
```

## index
index.md format:
```markdown
# Knowledge Index

## [Category]
- [concept-name](concepts/concept-name.md) — one line summary
```

## naming
- Concept file names: kebab-case, lowercase, `.md`
- Example: `list-comprehensions.md`, `variable-scope.md`
- Comparison file names: `a-vs-b.md`
```

Create `src/knowledge/__init__.py`:
```python
import os


def init_knowledge_dir(base_dir: str = None) -> str:
    if base_dir is None:
        base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "knowledge",
        )
    for subdir in ["raw", "concepts", "comparisons"]:
        os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)
    return base_dir
```

Create `src/knowledge/schema.py`:
```python
import os


def load_schema(path: str = None) -> str:
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "knowledge",
            "KNOWLEDGE_SCHEMA.md",
        )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_knowledge_schema.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add knowledge/ src/knowledge/ tests/test_knowledge_schema.py
git commit -m "feat: add knowledge schema and directory init"
```

---

### Task 2: Concept page CRUD

**Files:**
- Create: `src/knowledge/concept.py`
- Create: `tests/test_knowledge_concept.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_knowledge_concept.py
import os
import tempfile
from src.knowledge.concept import create_concept, read_concept, update_concept, delete_concept


def test_create_and_read_concept():
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = os.path.join(tmpdir, "concepts")
        os.makedirs(concepts_dir)

        create_concept("variables", "Variables store values in memory.", concepts_dir)

        path = os.path.join(concepts_dir, "variables.md")
        assert os.path.exists(path)

        content = read_concept("variables", concepts_dir)
        assert "Variables store values" in content
        assert "# variables" in content


def test_update_concept():
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = os.path.join(tmpdir, "concepts")
        os.makedirs(concepts_dir)

        create_concept("loops", "Loops repeat code.", concepts_dir)
        update_concept("loops", "Loops: for, while, and iteration patterns.", concepts_dir)

        content = read_concept("loops", concepts_dir)
        assert "for, while" in content


def test_delete_concept():
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = os.path.join(tmpdir, "concepts")
        os.makedirs(concepts_dir)

        create_concept("temp", "Temporary concept.", concepts_dir)
        delete_concept("temp", concepts_dir)

        assert not os.path.exists(os.path.join(concepts_dir, "temp.md"))


def test_read_nonexistent_concept():
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = os.path.join(tmpdir, "concepts")
        os.makedirs(concepts_dir)

        result = read_concept("does-not-exist", concepts_dir)
        assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_knowledge_concept.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.knowledge.concept'`


- [ ] **Step 3: Write minimal implementation**

```python
# src/knowledge/concept.py
import os


def _concept_path(name: str, base_dir: str) -> str:
    safe_name = name.lower().replace(" ", "-")
    return os.path.join(base_dir, f"{safe_name}.md")


def create_concept(name: str, content: str, base_dir: str) -> str:
    path = _concept_path(name, base_dir)
    header = f"# {name}\n\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + content)
    return path


def read_concept(name: str, base_dir: str):
    path = _concept_path(name, base_dir)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def update_concept(name: str, content: str, base_dir: str) -> str:
    path = _concept_path(name, base_dir)
    header = f"# {name}\n\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + content)
    return path


def delete_concept(name: str, base_dir: str) -> None:
    path = _concept_path(name, base_dir)
    if os.path.exists(path):
        os.remove(path)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_knowledge_concept.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add src/knowledge/concept.py tests/test_knowledge_concept.py
git commit -m "feat: add concept page CRUD"
```

---

### Task 3: Index management

**Files:**
- Create: `src/knowledge/index.py`
- Create: `tests/test_knowledge_index.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_knowledge_index.py
import os
import tempfile
from src.knowledge.index import add_to_index, read_index, remove_from_index


def test_add_and_read_index():
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.md")

        add_to_index("variables", "Store values in memory", index_path)
        add_to_index("functions", "Reusable blocks of code", index_path)

        content = read_index(index_path)
        assert "variables" in content
        assert "Store values in memory" in content
        assert "functions" in content


def test_remove_from_index():
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.md")

        add_to_index("variables", "Store values", index_path)
        add_to_index("functions", "Reusable code", index_path)
        remove_from_index("variables", index_path)

        content = read_index(index_path)
        assert "variables" not in content
        assert "functions" in content


def test_read_empty_index():
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.md")
        content = read_index(index_path)
        assert content == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_knowledge_index.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.knowledge.index'`


- [ ] **Step 3: Write minimal implementation**

```python
# src/knowledge/index.py
import os


def _ensure_index(path: str) -> None:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Knowledge Index\n\n")


def add_to_index(name: str, summary: str, path: str) -> None:
    _ensure_index(path)
    link = f"concepts/{name.lower().replace(' ', '-')}.md"
    entry = f"- [{name}]({link}) — {summary}\n"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if entry.strip() not in content:
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)


def read_index(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def remove_from_index(name: str, path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    link = f"concepts/{name.lower().replace(' ', '-')}.md"
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            if link not in line:
                f.write(line)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_knowledge_index.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add src/knowledge/index.py tests/test_knowledge_index.py
git commit -m "feat: add index management"
```

---

### Task 4: Log management

**Files:**
- Create: `src/knowledge/log.py`
- Create: `tests/test_knowledge_log.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_knowledge_log.py
import os
import tempfile
from src.knowledge.log import append_log, read_log


def test_append_and_read_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "log.md")

        append_log("ingest", "python-handbook.md", "Extracted 12 concepts", log_path)
        append_log("lint", "", "Found 2 orphan pages", log_path)

        content = read_log(log_path)
        assert "ingest" in content
        assert "python-handbook.md" in content
        assert "Extracted 12 concepts" in content
        assert "lint" in content
        assert "Found 2 orphan pages" in content
        # Verify timestamp format
        assert "## [" in content


def test_read_empty_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "log.md")
        content = read_log(log_path)
        assert content == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_knowledge_log.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.knowledge.log'`


- [ ] **Step 3: Write minimal implementation**

```python
# src/knowledge/log.py
import os
from datetime import datetime


def append_log(operation: str, source: str, detail: str, path: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"## [{timestamp}] {operation}"
    if source:
        entry += f" | {source}"
    entry += f"\n{detail}\n\n"

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Knowledge Log\n\n")
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry)


def read_log(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_knowledge_log.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add src/knowledge/log.py tests/test_knowledge_log.py
git commit -m "feat: add log management"
```

---

### Task 5: Integration — wire into BaizePaw

**Files:**
- Modify: `src/tools/dispatcher.py`

- [ ] **Step 1: Update existing tests if needed**

Run: `PYTHONPATH=. pytest -v`
Expected: All existing tests (41+) still pass — knowledge module is standalone, no integration yet

- [ ] **Step 2: Run full test suite to verify no regressions**

Run: `PYTHONPATH=. pytest -v`
Expected: All tests pass (41 existing + 11 new = 52)

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: v0.4 knowledge base module complete"
```

---

## Verification

```bash
PYTHONPATH=. pytest -v          # All 52 tests pass
python -c "from src.knowledge import init_knowledge_dir; print(init_knowledge_dir())"  # Creates knowledge/ dirs
```
