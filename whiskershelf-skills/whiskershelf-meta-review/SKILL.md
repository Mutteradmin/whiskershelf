---
name: whiskershelf-meta-review
description: Generate a methodology-level meta-review across 3-8 papers from the user's local WhiskerShelf library. Use when the user wants "the forest, not the trees" — a synthesis of methodology taxonomy, cross-paper differences, and shared blind spots across a small set of related papers.
---

# Whiskershelf Meta-Review

Use this skill to produce a **methodology meta-review of 3-8 papers** in the user's library. Output is a 6-section markdown document: 共同方法学背景 / 方法学分类法 / 跨论文差异矩阵 / 方法学趋势 / 共同盲点 / 关键洞察.

This is the **forest-level** view. For 2 papers, use `whiskershelf-compare` instead. For new research directions (not just synthesis), use `whiskershelf-brief` (Idea Spark).

## When to use

- The user picks 3+ papers and asks "归纳一下方法", "做个综述", "这些方法有没有共同点".
- A brief direction is in a cross-domain area and the lead wants to understand the methodology landscape before committing.
- The user is starting a literature review for a thesis or report.
- The user wants to find "shared blind spots" — assumptions every paper makes, evaluation gaps.

**Don't use** when:
- N = 2 → use `whiskershelf-compare`.
- The user wants to brainstorm new research directions (not synthesize existing ones) → use `whiskershelf-brief`.
- The user wants a single paper explained → use `whiskershelf-search` to fetch the abstract + notes.
- N > 8 → too many papers for one LLM context; use `whiskershelf-search` to filter first, or run multiple meta-reviews on subsets.

## Endpoint

```
POST http://127.0.0.1:8080/api/ai/meta-review
Body: {"papers": ["<filename>", ...], "focus": "<optional 1-2 sentence angle>"}
→    {"success": true, "content": "<6-section markdown>", "reasoning_content": "...",
      "papers": [...], "focus": "...", "session_id": "<id>"}
```

N must be in [3, 8]. The full spec is in `references/api-endpoints.md` (request shape, error codes, history endpoints).

## Workflow

1. **Resolve paper names** — if the user said "the SNN transformers" or "all my RWKV papers", find the matching set via `whiskershelf-search` (`POST /api/agent/search` or `GET /api/agent/papers`). Pre-filtering by tag is the cleanest way to pick a coherent set.
2. **Confirm the set with the user** — show the N titles you'll synthesize, ask "Proceed?". N is the most consequential knob; wrong N = useless output.
3. **Optional: collect a focus angle** — "evaluations", "theoretical frameworks", "engineering paths". The LLM will weight the taxonomy + matrix accordingly.
4. **POST to `/api/ai/meta-review`** — use the script:
   ```bash
   python .claude/skills/whiskershelf-meta-review/scripts/meta_review.py \
       --papers "Spikformer v1.pdf" "Spikformer v2.pdf" "SpikingResformer.pdf" "QKFormer.pdf" \
       --focus "evaluations and training recipes"
   ```
5. **Present the 6 sections in order** — the LLM output is already structured. Highlight:
   - The taxonomy (section 2) — this is the most reusable artifact
   - The matrix (section 3) — copy the markdown table; don't paraphrase
   - The "关键洞察" (section 6) — opinionated take, quote verbatim
6. **If the user wants to act on a gap** (e.g., "共同盲点 #2 — nobody tests on OOD"): suggest a new `whiskershelf-brief` session with that gap as the research direction. Hand off cleanly.

## Output handling

- The result is **always Markdown**, with one markdown table in section 3 (cross-paper matrix). Surface that table verbatim — it's the highest-density info.
- If `reasoning_content` is present and the user asks "what was the model thinking?", quote 1-2 lines. Don't paste the whole thing.
- The session is automatically saved to `meta_review_history.json`; the user can revisit it in the UI.

## Anti-patterns

- Calling meta-review with N=2 (use compare) or N=9 (will get 400).
- Picking papers by random — the meta-review is only useful if the N papers share a methodology (e.g., 4 SNN transformers, not 1 SNN + 1 LLM + 1 vision). Filter first.
- Skipping the "confirm the set" step. The user often has a different N in mind than the one you'd pick.
- Re-running with the same N to "get a different angle" — the LLM output is non-deterministic but very similar; instead, change the `--focus` argument.
- Mistaking meta-review for a literature review. The 6 sections are a **methodology** synthesis, not a per-paper recap. If the user wants a per-paper summary, use `whiskershelf-search` for each.
