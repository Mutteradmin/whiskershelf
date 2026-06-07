# WhiskerShelf Meta-Review API Reference

## `POST /api/ai/meta-review`

Generate a methodology meta-review across 3-8 papers.

### Request
```json
{
  "papers": ["Spikformer v1.pdf", "Spikformer v2.pdf", "SpikingResformer.pdf", "QKFormer.pdf"],
  "focus": "evaluations and training recipes"  // optional
}
```

### Response (200)
```json
{
  "success": true,
  "content": "## 1. 共同方法学背景\n...\n## 6. 关键洞察\n...",
  "reasoning_content": "...",
  "papers": [
    {"name": "...", "title": "...", "abstract": "...", "tags": [...], "notes": "..."},
    ...
  ],
  "focus": "evaluations and training recipes",
  "session_id": "1700000000000"
}
```

### Output structure (6 sections)
The LLM is prompted to produce exactly these sections, in this order:
1. **共同方法学背景** — 2-3 sentence framing
2. **方法学分类法** — ≤3-level hierarchical taxonomy
3. **跨论文差异矩阵** — markdown table (rows = papers, 4 cols: 核心方法/数据集/评估方式/关键创新点)
4. **方法学趋势** — 2-3 bullets: converging, diverging, emerging
5. **共同盲点** — 2-3 bullets: shared assumptions, evaluation gaps
6. **关键洞察** — 1 paragraph, opinionated

The UI's `renderMarkdown()` handles all 6 — no special parsing needed.

### Error cases
- `400 {"error": "请选择 3-8 篇论文"}` — N < 3 or N > 8, or `papers` not a list.
- `400 {"error": "AI未配置或已禁用"}` — AI config empty or disabled.
- `404 {"error": "以下论文不存在: <names>"}` — one or more paper names not in library.

## `GET /api/ai/meta-review/history`

List saved meta-review sessions (newest first, capped at 50).

### Response (200)
```json
{
  "success": true,
  "sessions": [
    {
      "id": "1700000000000",
      "time": 1700000000,
      "titles": ["Spikformer v1", "Spikformer v2", "SpikingResformer", "QKFormer"],
      "focus": "evaluations",
      "preview": "## 1. 共同方法学背景..."
    }
  ]
}
```

## `GET /api/ai/meta-review/history/{id}`

Fetch a single session in full.

### Response (200)
```json
{
  "success": true,
  "session": {
    "id": "...",
    "time": ...,
    "papers": [...],
    "focus": "...",
    "result": "<full 6-section markdown>",
    "reasoning_content": "..."
  }
}
```

### Error cases
- `400 {"error": "invalid id"}` — empty id.
- `404 {"error": "not found"}` — no session with that id.

## Tips for the agent

- The 6 sections are stable; if any is missing in the response, re-dispatch the LLM with a tighter prompt (this is a prompt-level failure, not an API failure).
- The matrix table in section 3 is the highest-density output — copy it verbatim when presenting to the user.
- For N=8 the LLM context is ~12K tokens; well within deepseek-chat and GPT-4 limits. For N=3 the output is shorter; the user may want more depth — consider re-running with a tighter `--focus`.

## Versioning

Stable as of WhiskerShelf v1.x. The 6-section structure is the contract; new fields may be added but the section order is preserved.
