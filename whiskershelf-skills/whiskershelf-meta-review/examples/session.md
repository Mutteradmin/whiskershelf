# Example: meta-review on 4 SNN-transformer papers

Scenario: the user is writing the related work section of a thesis chapter on "SNN for vision" and needs a methodology-level synthesis. They have 4 candidate papers.

## Step 1: identify the set

The user said "all my SNN-transformer papers". The cleanest way to find them:

```bash
python .claude/skills/whiskershelf-search/scripts/ws_papers.py --tag "脉冲神经网络 SNN" --json | jq -r '.papers[].name'
```

Filter to those whose titles include "Transformer" or "former". Suppose we get:
- `SPIKFORMER WHEN SPIKING NEURAL NETWORK MEETS TRANSFORMER.pdf`
- `SPIKFORMER v2.pdf`
- `SpikingResformer Bridging ResNet and Vision Transformer in Spiking Neural Networks.pdf`
- `QKformer Hierachical Spiking Transformer.pdf`

N = 4, within the [3, 8] range.

## Step 2: confirm the set

> "I'll synthesize these 4 SNN-transformer papers:
> 1. SPIKFORMER (the original SSA)
> 2. SPIKFORMER v2 (SSL-pretrained)
> 3. SpikingResformer (DSSA)
> 4. QKformer (Q-K separated)
>
> Proceed? Or want to swap any?"

User: "Looks right. Do it."

## Step 3: run meta-review

No focus — the user wants the full landscape.

```bash
python .claude/skills/whiskershelf-meta-review/scripts/meta_review.py \
    --papers \
      "SPIKFORMER WHEN SPIKING NEURAL NETWORK MEETS TRANSFORMER.pdf" \
      "SPIKFORMER v2.pdf" \
      "SpikingResformer Bridging ResNet and Vision Transformer in Spiking Neural Networks.pdf" \
      "QKformer Hierachical Spiking Transformer.pdf"
```

## Step 4: present the 6 sections

The output is ~1800 words across 6 sections. Surface them in order:

1. **共同方法学背景** — 2-3 sentence framing (always quote verbatim)
2. **方法学分类法** — the taxonomy tree, copy the markdown verbatim
3. **跨论文差异矩阵** — the table; this is the highest-density artifact
4. **方法学趋势** — 2-3 bullets
5. **共同盲点** — 2-3 bullets; this is often the most useful for a thesis
6. **关键洞察** — the opinionated paragraph

> "Here's the synthesis. The taxonomy (section 2) shows the field has split into 2 camps: **non-softmax sparse attention** (Spikformer, SpikingResformer) vs **Q-K separated** (QKFormer). The matrix (section 3) shows everyone uses ImageNet + Top-1, but only Spikformer v2 adds SSL pretraining.
>
> Most useful for your thesis: section 5 — every paper assumes i.i.d. test data, none evaluates on OOD or adversarial. That's a gap you could flag in your related work."

## Step 5: hand off

If the user wants to:
- **Write a related work paragraph** → hand off to a new `whiskershelf-brief` (Idea Spark) session with the 4 papers + a "write a related work paragraph" focus.
- **Fill the OOD-evaluation gap** → start a new brief with the gap as the research direction.
- **Add a 5th paper to the synthesis** → re-run meta-review with N=5; the LLM handles the extra paper without major quality loss.

## Anti-patterns in this scenario

- Picking random papers instead of pre-filtering by tag. A coherent methodology set is what makes meta-review useful; 4 unrelated papers = generic output.
- Pasting the full 1800-word output to the user. They want section 2 (taxonomy) + section 3 (matrix) + section 5 (blind spots) as the highlights; the rest is for them to read.
- Re-running with the same N to "get a different answer". Change the `--focus` instead.
- Confusing meta-review with a per-paper summary. If the user wants "explain Spikformer v2 to me", use `whiskershelf-search` to fetch the abstract.
