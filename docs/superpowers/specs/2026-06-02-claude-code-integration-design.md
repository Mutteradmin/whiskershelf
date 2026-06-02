# WhiskerShelf × Claude Code Integration — Design Spec

**Date**: 2026-06-02
**Status**: Approved (3 sections, user-confirmed)
**Author**: brainstorming session, with Claude

---

## 1. Context

WhiskerShelf v1.0 has shipped with the headline "Idea Spark" feature: a LLM collides 2–4 user-selected papers into a structured Markdown research brief that includes a "ready-to-paste Claude Code task block".

Today, the user's workflow ends at downloading that `.md` and pasting it into Claude Code manually. We want to close the loop: **make WhiskerShelf a first-class upstream tool that hands off work to Claude Code**, with reproducible project directories, auto-discovered Skills, and a minimal agent API.

This is the strategic move that differentiates WhiskerShelf from every other paper manager in the 2026 AI-agent era. It also makes the project more attractive for the "1k stars" milestone because it gives Claude Code users a concrete reason to install and star the repo.

---

## 2. Goals & Non-Goals

### Goals

1. **Lower friction** — One click in Idea Spark → a project directory Claude Code can `cd` into and immediately understand the task.
2. **Opinionated Skills** — Provide Skills that guide CC through a *research process*, not just expose HTTP endpoints. CC should know what to do next.
3. **Optional coupling** — WhiskerShelf still works fully without CC. The integration is opt-in and degrades gracefully.
4. **Zero new runtime dependencies** — Skills are pure Markdown; the agent API reuses the existing Python stdlib HTTP server.

### Non-Goals

- Subprocess-invoking CC from a button (too fragile, see §4.2 trade-off).
- Full MCP server implementation (overkill for v1; revisit if users ask).
- Auto-committing generated projects to git (let the user control).
- Real-time bidirectional sync between WhiskerShelf and CC (out of scope; the brief is a snapshot).

---

## 3. Differentiation Narrative (README)

Add a new section to `README.md` between "AI Features in Detail" and "Innovations":

```markdown
## 🆚 How is this different from ...?

A cheat sheet for the "why not just use X" question:

| Tool | What it does well | What WhiskerShelf adds |
|---|---|---|
| **Zotero / Mendeley** | Reference management, citation export | AI-synthesized cross-paper research directions |
| **Elicit / Consensus** | AI paper discovery, Q&A over literature | Local-first: your PDFs never leave your disk |
| **Obsidian / Logseq** | Note-taking, knowledge graph | Purpose-built for paper reading → idea generation |
| **Connected Papers** | Visual citation graph | The graph becomes *executable tasks* for Claude Code |
| **ChatGPT + papers** | Ad-hoc Q&A | Persistent research history across sessions and devices |

### The unique combination

WhiskerShelf is the only tool that combines all three:

1. **Local-first paper library** (PDFs never leave your disk)
2. **LLM-driven cross-paper idea generation** (Idea Spark)
3. **First-class Markdown export designed for Agent Coding** (drop the brief into Claude Code as a task)
```

---

## 4. Claude Code Integration — Project Handoff

### 4.1 Chosen approach: Project Handoff (not subprocess, not MCP)

User generates a brief → WhiskerShelf packages it into a self-contained project directory → user `cd`s in and runs `claude`. CC auto-discovers Skills via `.claude/skills/`.

### 4.2 Why not subprocess / MCP

| Approach | Why rejected |
|---|---|
| **Subprocess** (`subprocess.Popen(['claude', ...])`) | Cross-platform bugs (Windows console, PATH, detached mode), lifecycle management, no clear failure mode for the user. |
| **MCP server** | Heavy protocol, auth/CORS concerns, breaks the "local stdlib, zero deps" promise. |

Project Handoff is the only approach that:
- Has no new failure modes
- Works with every CC version that supports Skills
- Lets the user control the launch moment
- Keeps the architecture simple

### 4.3 Generated directory structure

When the user clicks `🚀 Generate Claude Code Project` in Idea Spark results, WhiskerShelf writes this directory (user picks the location):

```
whiskershelf-brief-2026-06-02-1530/
├── README.md                   # 简述：这是 WhisKerShelf Idea Spark 输出
├── brief.md                    # Idea Spark 的 Markdown 研究方向（已有内容）
├── CLAUDE.md                   # CC 的项目级 system prompt：上下文 + 任务 + 约束
├── selected-papers.json        # 选中的论文元信息（CC 可引用）
├── start-claude.sh             # Linux/macOS 启动器
├── start-claude.bat            # Windows 启动器
└── .claude/
    └── skills/
        ├── whiskershelf-brief/
        │   └── SKILL.md
        ├── whiskershelf-search/
        │   └── SKILL.md
        └── whiskershelf-tag/
            └── SKILL.md
```

### 4.4 `start-claude.sh` / `.bat` content

Both launchers do the same thing:

- **Linux/macOS**:
  ```bash
  #!/usr/bin/env bash
  echo "Starting Claude Code with WhiskerShelf project context..."
  echo "Tip: if 'claude' is not found, install: https://claude.com/code"
  exec claude
  ```

- **Windows** (`start-claude.bat`):
  ```bat
  @echo off
  echo Starting Claude Code with WhiskerShelf project context...
  echo Tip: if 'claude' is not found, install: https://claude.com/code
  claude
  pause
  ```

Simple, no magic, no assumptions about CC's exact invocation flags.

### 4.5 `CLAUDE.md` (project-level system prompt)

This is read by CC on every interaction in the project. It frames the research context:

```markdown
# Project: Research Brief from WhiskerShelf

This project was generated by **WhiskerShelf's Idea Spark** feature on 2026-06-02.
You are helping the user turn a research brief into executable work.

## Context
- The user selected 2-4 papers from their local WhiskerShelf library.
- `brief.md` contains the LLM-generated research directions.
- `selected-papers.json` has full paper metadata (titles, abstracts, tags, notes).

## Your role
You are a research collaborator, not just a code generator. Before writing code:
1. Read `brief.md` end to end
2. Identify which of the 3-5 directions the user wants to pursue
3. Propose a concrete plan (5-7 steps) and ask for confirmation
4. Then begin execution

## Available skills (auto-loaded)
- `whiskershelf-brief` — load and interpret the brief
- `whiskershelf-search` — query the user's local library
- `whiskershelf-tag` — organize papers with tags

## Conventions
- When implementing a direction from the brief, follow the "method transfer path" and "expected challenges" sections.
- When the user references "the X paper" or "my notes on Y", use `whiskershelf-search` to find it.
- After meaningful progress, suggest tags for the new artifact.
```

### 4.6 UI: New button in Idea Spark modal

In the Idea Spark result toolbar, add a new button between "下载为 .md" and "复制源码":

```html
<button class="btn-ai-recommend" id="exportClaudeProjectBtn">🚀 生成 CC 项目</button>
```

Click handler:
1. Default save location: `<user-home>/Documents/whiskershelf-briefs/whiskershelf-brief-YYYY-MM-DD-HHMM/` (configurable later via settings).
   - Rationale: avoids cross-browser File System Access API incompatibilities. The user can `mv` the directory after if needed.
2. Python backend: create the directory, write all files from §4.3, return the absolute path.
3. Show toast: "已生成到 <path> ✅ 是否打开？"
4. If user clicks "open", call `os.startfile / open / xdg-open` on the directory.

(We considered `<input type="file" webkitdirectory>` but it's upload-only. The File System Access API (`showDirectoryPicker`) is Chrome/Edge-only. A documented default location works everywhere and is the principle-of-least-surprise choice.)

### 4.7 WhisKerShelf agent API (CC → WhisKerShelf)

Reuse the existing `BaseHTTPRequestHandler`. Add 3 endpoints under `/api/agent/*`:

| Endpoint | Method | Body | Response | Allowed? |
|---|---|---|---|---|
| `/api/agent/search` | POST | `{"query": "..."}` | `{"results": [{name, title, abstract_preview}, ...]}` | ✅ |
| `/api/agent/papers` | GET | — | `{"papers": [...]}` (full list, truncated abstract) | ✅ |
| `/api/agent/papers/{name}` | GET | — | `{"name", "title", "abstract", "tags", "notes"}` | ✅ |
| `/api/agent/papers/{name}/tags` | POST | `{"tags": [...]}` | `{"success": true, "tags": [...]}` | ⚠️ Gated |

No authentication (server binds to 127.0.0.1 only by default). CC connects via `http://127.0.0.1:8080/api/agent/...`.

**Write gate for POST tags**: CC can propose tag changes, but the `whiskershelf-tag` SKILL.md instructs CC to **show the user the proposed change and wait for explicit confirmation** before POSTing. The backend logs every write so the user can audit. No bulk write endpoint in v1 (one paper at a time, one tag-set at a time).

---

## 5. Skills Directory — Research-Process-Oriented

Per user feedback: "让 CC 知道下一步 research 怎么办" — Skills should guide CC through a **research workflow**, not just document API endpoints.

### 5.1 `whiskershelf-brief/SKILL.md`

**Frontmatter:**
```yaml
---
name: whiskershelf-brief
description: Load a WhisKerShelf Idea Spark research brief and treat it as a task spec. Use when the user starts working on a brief-based project.
---
```

**Body** (excerpt):
```markdown
# Whiskershelf Research Brief

This project came from WhiskerShelf's Idea Spark.

## What `brief.md` contains
- Common themes and methodological tensions across N papers
- 3-5 actionable research directions, each with:
  - **核心 Idea** (one-sentence pitch)
  - **方法迁移路径** (which paper's method to use, how to adapt it)
  - **预期难点** (what might go wrong)
  - **验证方案** (minimal experiment)
- Cross-domain leap suggestions
- Risk and blind-spot analysis
- An embedded "Claude Code task block" (the original Markdown)

## Research workflow you should follow

1. **Read brief.md fully** before asking the user any question.
2. **Summarize back** the 3-5 directions in your own words. Ask the user which to pursue.
3. **For the chosen direction**, extract:
   - The method transfer path (which paper, which method)
   - The expected challenges
   - The validation criteria
4. **Propose a 5-7 step execution plan**. Wait for user approval before coding.
5. **Execute step by step**, checking off the validation criteria as you go.
6. **After meaningful progress** (e.g., first working prototype), suggest:
   - Running `whiskershelf-search` to find related work the user might have missed
   - Tagging the new artifact via `whiskershelf-tag`
7. **When stuck**:
   - Re-read the relevant section of brief.md
   - Search the user's library for related context
   - Ask the user for clarification rather than guessing

## Tone
You are a research collaborator. Be opinionated when you have evidence from the brief. Be humble when you don't.
```

### 5.2 `whiskershelf-search/SKILL.md`

**Frontmatter:**
```yaml
---
name: whiskershelf-search
description: Search the user's local WhiskerShelf paper library. Use when the user references a paper by partial title, or asks "find papers about X".
---
```

**Body** (excerpt):
```markdown
# Whiskershelf Search

WhiskerShelf runs locally on http://127.0.0.1:8080. **It only responds when the user has the app open.** If a search call fails, ask the user to start WhiskerShelf.

## Endpoints

```
POST http://127.0.0.1:8080/api/agent/search
Body: {"query": "spiking neural networks for time series"}
→ {"results": ["paper1.pdf", "paper2.pdf", ...]}

GET  http://127.0.0.1:8080/api/agent/papers
→ {"papers": [{name, title, tags, abstract_preview}, ...]}

GET  http://127.0.0.1:8080/api/agent/papers/{name}
→ {name, title, abstract, tags, notes}
```

## When to search

- **Before starting work**: search for related work the user might already have read but didn't surface in the brief.
- **User says "my X paper"**: search by partial title, then fetch the abstract.
- **User asks "what's in my library"**: use `GET /papers`.
- **Direction requires deep context** (e.g., "implement the method from paper X"): fetch the full abstract via `GET /papers/{name}`.

## Research-process guidance

After every search, ask yourself: "Does this change the direction we're pursuing?" If yes, surface it to the user before continuing. Search is a research move, not a routine.
```

### 5.3 `whiskershelf-tag/SKILL.md`

**Frontmatter:**
```yaml
---
name: whiskershelf-tag
description: Read/write tags on papers in the user's local WhisKerShelf library. Use to organize new artifacts or re-tag after a research session.
---
```

**Body** (excerpt):
```markdown
# Whiskershelf Tag Operations

The user has a 24+ taxonomy of preset tags. Use them; don't invent new ones unless necessary.

## Endpoints

```
GET    http://127.0.0.1:8080/api/agent/papers/{name}/tags
→ {"tags": ["linear-attention", "snn", ...]}

POST   http://127.0.0.1:8080/api/agent/papers/{name}/tags
Body: {"tags": ["snn", "brain-inspired"]}
→ {"success": true, "tags": [...]}

GET    http://127.0.0.1:8080/api/presets
→ {"presets": ["Agent", "Transformer", "大语言模型 LLM", ...]}
```

## When to tag

- **After completing a research direction** — ask the user if they want to tag any newly-relevant papers.
- **User adds a new paper to the library** — suggest 1-3 tags from the preset list.
- **User says "X is now important" or "stop reading Y"** — adjust tags accordingly.

## Research-process guidance

Tagging is how the user remembers. Don't tag silently. Always:
1. Show the proposed tag change
2. Wait for user confirmation
3. Confirm what was actually written

If a tag isn't in the presets, ask the user before creating a new one (avoid tag sprawl).
```

---

## 6. Implementation Tasks (high-level for writing-plans)

These are NOT step-by-step — `writing-plans` will break them down. Order matters.

1. **Add agent API endpoints** (`/api/agent/search`, `/api/agent/papers`, `/api/agent/papers/{name}`) — backend only.
2. **Write the 3 SKILL.md files** — pure content, no code, ship as part of the project bundle.
3. **Add `🚀 Generate Claude Code Project` button** to Idea Spark results — frontend.
4. **Implement directory generation** in Python — takes the current Idea Spark session + a target directory, writes all files.
5. **Update README** with the §3 differentiation section.
6. **Smoke test**: pick 2 papers, generate a project, `cd` into it, run `claude`, verify Skills are loaded.
7. **Document the workflow** in README "Quick Start" with a small walkthrough.

---

## 7. Risks & Open Questions

| Risk | Mitigation |
|---|---|
| WhiskerShelf might not be running when CC tries to call it | Skills document the URL assumption; CC is told to ask the user to start it. |
| `claude` CLI not installed | Starters print a tip with install link. |
| User picks a project directory they don't have write access to | Use webkitdirectory input + write to a tmpdir first, then move? Or just show error toast. |
| Skills become stale as CC versions change | Re-validate on every release. Skills follow CC's documented frontmatter spec. |
| User generates a project in a git repo and it pollutes git status | Add a `.gitignore` line to the generated project (e.g., `whiskershelf-brief-*/` is NOT ignored — user might want it; let them decide). |

### Open questions for writing-plans to address

- Should the agent API be rate-limited?
- Should there be a "open in CC" button that calls CC's deep link (`claude://`) or only a directory open?
- Where to store the Skills globally vs per-project? (Decision: per-project only, simpler.)

---

## 8. Success Criteria

- [ ] User can click "🚀 生成 CC 项目" and have a usable project directory in <5 seconds.
- [ ] Running `claude` in the generated directory loads the 3 Skills automatically.
- [ ] CC can call `/api/agent/search` and get relevant results when WhiskerShelf is open.
- [ ] README has a clear "different from X" section that resonates with new visitors.
- [ ] The integration works on Windows, macOS, and Linux (starters + permissions).
- [ ] Zero new runtime dependencies added to WhiskerShelf.

---

## 9. References

- Claude Code Skills documentation (frontmatter spec, `SKILL.md` format)
- WhiskerShelf existing API: `app.py` `do_GET` / `do_POST` handlers
- WhiskerShelf Idea Spark implementation: `ai_idea_spark()` in `app.py`
- WhiskerShelf front-end modal: `static/index.html` `#ideaSparkModal`
