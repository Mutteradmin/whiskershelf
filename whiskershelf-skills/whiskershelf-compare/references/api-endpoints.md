# WhiskerShelf Compare API Reference

## `POST /api/ai/compare`

Generate a structured comparison of exactly 2 papers.

### Request
```json
{
  "paper_a": "SPIKFORMER v2.pdf",
  "paper_b": "RWKV-7 Goose with Expressive Dynamic State Evolution.pdf",
  "focus": "memory efficiency on long sequences"  // optional, 1-2 sentences
}
```

### Response (200)
```json
{
  "success": true,
  "content": "## 1. 对照表\n\n| 维度 | 论文 A | 论文 B |\n|---|---|---|...|",
  "reasoning_content": "...",  // present only when thinking mode is on AND the model supports it
  "paper_a": {"name": "...", "title": "...", "abstract": "...", "tags": [...], "notes": "..."},
  "paper_b": {"name": "...", "title": "...", "abstract": "...", "tags": [...], "notes": "..."},
  "focus": "memory efficiency on long sequences",
  "session_id": "1700000000000"
}
```

### Error cases
- `400 {"error": "请提供两篇论文的 PDF 文件名"}` — missing paper_a or paper_b.
- `400 {"error": "请选择两篇不同的论文"}` — paper_a == paper_b.
- `400 {"error": "AI未配置或已禁用"}` — AI config empty or disabled.
- `404 {"error": "以下论文不存在: <names>"}` — one or both paper names not in library.

### Auto-extracted abstracts

If either paper has no stored abstract in `paper_abstracts.json`, the server **synchronously** tries to extract one from the PDF using PyPDF2. The extraction only reads the first 3 pages; if PyPDF2 isn't installed or extraction fails, the LLM is given an empty abstract for that paper (which usually yields a less specific output — surface this to the user).

## `GET /api/ai/compare/history`

List all saved compare sessions (newest first, capped at 50).

### Response (200)
```json
{
  "success": true,
  "sessions": [
    {
      "id": "1700000000000",
      "time": 1700000000,
      "titles": ["SPIKFORMER v2", "RWKV-7 Goose..."],
      "focus": "memory efficiency on long sequences",
      "preview": "## 1. 对照表\n..."
    }
  ]
}
```

## `GET /api/ai/compare/history/{id}`

Fetch a single session in full.

### Response (200)
```json
{
  "success": true,
  "session": {
    "id": "...",
    "time": ...,
    "paper_a": {...},
    "paper_b": {...},
    "focus": "...",
    "result": "<full markdown>",
    "reasoning_content": "..."
  }
}
```

### Error cases
- `400 {"error": "invalid id"}` — empty id.
- `404 {"error": "not found"}` — no session with that id.

## Versioning

Stable as of WhiskerShelf v1.x. New fields may be added; existing ones will not be renamed.
