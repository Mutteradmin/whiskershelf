---
name: whiskershelf-compare
description: Generate a structured side-by-side comparison of two papers from the user's local WhiskerShelf library. Use when the user picks two specific papers and wants a focused comparison (vs. the broader "cross-paper brainstorm" of whiskershelf-brief, or the N-paper meta-review of whiskershelf-meta-review).
---

# Whiskershelf Compare

Use this skill to produce a **structured comparison of exactly two papers**. Output is a 7-row markdown table (核心问题 / 方法 / 数据集 / 评估指标 / 主要结果 / 局限性 / 复现难度) plus a 1-2 paragraph "关键分歧与适用场景" section, plus "互相借鉴的具体建议".

## When to use

- The user picks **exactly 2 papers** and asks "compare them", "对比", "有什么区别", "A vs B".
- A brief direction needs a focused comparison of two candidate methods (e.g., "should I implement X or Y?").
- A research lead wants to settle a methodology debate between two approaches.

**Don't use** when:
- The user wants 3+ papers → use `whiskershelf-meta-review`.
- The user wants to brainstorm new directions across 2-4 papers → use `whiskershelf-brief` (Idea Spark).
- The user just wants a search → use `whiskershelf-search`.

## Endpoint

```
POST http://127.0.0.1:8080/api/ai/compare
Body: {"paper_a": "<filename>", "paper_b": "<filename>", "focus": "<optional 1-2 sentence angle>"}
→    {"success": true, "content": "<markdown>", "reasoning_content": "<if thinking enabled>",
      "paper_a": {...}, "paper_b": {...}, "focus": "...",
      "session_id": "<id>"}
```

Get the full POST spec in `references/api-endpoints.md` (includes error codes, history endpoints, response shape).

## Workflow

1. **Resolve paper names** — if the user said "the Spikformer paper", find the exact filename via `whiskershelf-search` (`GET /api/agent/papers?tag=...` or `POST /api/agent/search`).
2. **Confirm with the user** — show the two titles you'll compare, ask "Proceed?". Don't silently pick a wrong paper.
3. **Optional: collect a focus angle** — if the user mentioned what to compare on (memory, scalability, bio plausibility, etc.), include it. Otherwise leave `focus` empty.
4. **POST to `/api/ai/compare`** — use the shell script in `scripts/` (avoids JSON-by-hand):
   ```bash
   python .claude/skills/whiskershelf-compare/scripts/compare.py \
       --paper-a "SPIKFORMER v2.pdf" \
       --paper-b "RWKV-7 Goose with Expressive Dynamic State Evolution.pdf" \
       --focus "memory efficiency on long sequences"
   ```
5. **Present the table + the key disagreements** — the LLM output is already structured; surface the "关键分歧" paragraph verbatim and quote 1-2 table cells that matter for the user's question.
6. **If the user picks a side**: stop here. The synthesis is the deliverable.
7. **If the user wants to act** (e.g., "OK, I'll go with X"): they may want to start a new brief or a follow-up compare. Hand off to `whiskershelf-brief` or `whiskershelf-search` as needed.

## Output handling

- The result is **always Markdown** (table + 1-2 paragraphs). Don't try to parse it into a structured object — surface the markdown to the user.
- If `reasoning_content` is present and the user asks "what was the model thinking?", quote 1-2 lines. Don't paste the whole thing.
- The session is automatically saved to `comparison_history.json`; the user can revisit it in the UI.

## Anti-patterns

- Calling compare for 1 or 3+ papers (use search / meta-review instead).
- Silently picking a paper when the user's description is ambiguous — confirm first.
- Re-running the same compare to "refresh" — the result is cached server-side, just re-call `GET /api/ai/compare/history/{id}`.
- Trying to compare papers that don't exist in the library — the API will return 404; use `whiskershelf-web-search` instead.
