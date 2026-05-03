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
