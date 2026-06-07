#!/usr/bin/env python3
"""
meta_review.py — CLI wrapper for POST /api/ai/meta-review.

Stdlib-only.

Usage:
    python meta_review.py --papers "A.pdf" "B.pdf" "C.pdf"
    python meta_review.py --papers "A.pdf" "B.pdf" "C.pdf" "D.pdf" --focus "evaluations"
    python meta_review.py --papers "A.pdf" "B.pdf" "C.pdf" --json
    python meta_review.py --history
    python meta_review.py --history --json
    python meta_review.py --session <id>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_BASE = os.environ.get("WHISKERSHELF_BASE", "http://127.0.0.1:8080")
DEFAULT_TIMEOUT = float(os.environ.get("WHISKERSHELF_TIMEOUT", "60"))


def _request(method: str, path: str, body: dict | None = None,
             base: str = DEFAULT_BASE, timeout: float = DEFAULT_TIMEOUT) -> dict:
    url = base.rstrip("/") + path
    data: bytes | None = None
    headers: dict[str, str] = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raw = ""
        try:
            raw = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        try:
            err = json.loads(raw).get("error", raw) if raw else f"HTTP {e.code}"
        except json.JSONDecodeError:
            err = raw or f"HTTP {e.code}"
        raise RuntimeError(err) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Cannot reach WhiskerShelf at {base}. Is the app running? ({e.reason})") from e


def _time_str(epoch: int) -> str:
    if not epoch:
        return "(unknown time)"
    return dt.datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def _print_human_run(result: dict) -> None:
    papers = result.get("papers") or []
    print(f"# Meta-Review ({len(papers)} 篇)\n")
    for i, p in enumerate(papers, 1):
        print(f"{i}. {p.get('title') or p.get('name', '?')}")
    if result.get("focus"):
        print(f"\n> 视角: {result['focus']}\n")
    print(result.get("content", "(no content)"))
    rc = result.get("reasoning_content") or ""
    if rc.strip():
        print(f"\n<!-- 思考过程 ({len(rc)} 字) — 存在服务器端 history；用 --session {result.get('session_id')} 查看 -->")


def _print_human_history(sessions: list) -> None:
    if not sessions:
        print("(no history)")
        return
    for s in sessions:
        titles = s.get("titles") or []
        n = len(titles)
        label = f"{n} 篇：" + (", ".join(titles[:3]) + ("…" if n > 3 else "")) if titles else "(untitled)"
        focus = f" — {s['focus']}" if s.get("focus") else ""
        print(f"[{s['id']}] {label}{focus}")
        print(f"    {s.get('preview', '')[:80].replace(chr(10), ' ')}…")
        print(f"    {_time_str(s.get('time', 0))}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="WhiskerShelf Meta-Review CLI")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--papers", nargs="+",
                    help="3-8 paper filenames (PDF) to synthesize")
    ap.add_argument("--focus", help="optional 1-2 sentence methodology angle")
    ap.add_argument("--history", action="store_true", help="list saved meta-review sessions")
    ap.add_argument("--session", help="fetch a specific saved session by id")
    ap.add_argument("--json", action="store_true", help="emit raw JSON")
    args = ap.parse_args()

    flags = [bool(args.papers), args.history, bool(args.session)]
    if sum(flags) != 1:
        ap.error("use exactly one mode: --papers, --history, or --session <id>")

    if args.history:
        data = _request("GET", "/api/ai/meta-review/history", base=args.base)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            _print_human_history(data.get("sessions") or [])
        return 0

    if args.session:
        data = _request("GET", "/api/ai/meta-review/history/" + urllib.parse.quote(args.session),
                        base=args.base)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            s = data.get("session") or {}
            if not s:
                print("(not found)")
                return 2
            papers = s.get("papers") or []
            print(f"# Saved Meta-Review [{s.get('id')}]")
            print(f"  {len(papers)} 篇 — saved {_time_str(s.get('time', 0))}")
            if s.get("focus"):
                print(f"  focus: {s['focus']}")
            print()
            print(s.get("result", "(no content)"))
        return 0

    # Run mode
    if not (3 <= len(args.papers) <= 8):
        ap.error(f"--papers requires 3 to 8 items (got {len(args.papers)})")
    try:
        result = _request("POST", "/api/ai/meta-review", base=args.base,
                          body={"papers": args.papers, "focus": args.focus or ""})
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if not result.get("success"):
        print(f"server returned error: {result.get('error', 'unknown')}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human_run(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
