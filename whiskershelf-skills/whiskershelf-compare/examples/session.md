# Example: compare two SNN papers

Scenario: the user is choosing between Spikformer v2 and QKFormer as the base for a new SNN project. They ask "compare them on architecture, training cost, and accuracy".

## Step 1: resolve paper names

The user said "Spikformer v2" and "QKFormer". Find the exact filenames:

```bash
python .claude/skills/whiskershelf-search/scripts/ws_search.py "Spikformer v2" --limit 1
python .claude/skills/whiskershelf-search/scripts/ws_search.py "QKFormer" --limit 1
```

Suppose we get:
- `SPIKFORMER v2.pdf`
- `QKformer Hierachical Spiking Transformer.pdf`

## Step 2: confirm with the user

> "I'll compare:
> - **SPIKFORMER v2** (Spikformer v2 — the SSL-pretrained 80.38% on ImageNet-1K)
> - **QKformer Hierachical Spiking Transformer** (QKFormer — Q-K separated attention)
>
> Proceed?"

User: "Yes."

## Step 3: run compare with focus

```bash
python .claude/skills/whiskershelf-compare/scripts/compare.py \
    --paper-a "SPIKFORMER v2.pdf" \
    --paper-b "QKformer Hierachical Spiking Transformer.pdf" \
    --focus "architecture (SSA vs Q-K split), training cost (steps, params, data), and top-1 accuracy on ImageNet"
```

The `--focus` field is included because the user gave a specific angle. It tells the LLM to weight the table toward these dimensions.

## Step 4: present the result

The output is a 7-row markdown table + 1-2 paragraphs. Surface it to the user **verbatim** — the table is the value, paraphrasing loses precision. Then quote the "关键分歧" paragraph and ask:

> "Based on the table: Spikformer v2's accuracy is higher (80.38% vs ~80% on QKFormer) but it requires SSL pretraining which is expensive. QKFormer is simpler to train from scratch. Given that you want to start a 2-week project, which trade-off matches your timeline?"

## Step 5: hand off

If the user picks Spikformer v2 as the base → suggest they next run `whiskershelf-web-search` for the latest Q1 2026 follow-ups, or `whiskershelf-brief` to start a brief.

If the user wants a 3-way comparison (add a third paper) → call `whiskershelf-meta-review` instead.

## Anti-patterns in this scenario

- Skipping the "confirm papers" step. Filenames with Chinese characters or odd capitalization (e.g., `SPIKFORMER v2.pdf` with all-caps) are easy to mistype; the user catches it.
- Running compare without a focus when the user has given one. The LLM output is meaningfully better with an explicit angle.
- Pasting the full 1500-word output to the user when they only need the table + the "关键分歧" paragraph.
- Trying to compare 3 papers — use meta-review instead.
