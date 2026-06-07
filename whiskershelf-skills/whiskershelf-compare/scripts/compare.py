#!/usr/bin/env python3
"""
compare.py — CLI wrapper for POST /api/ai/compare.

Stdlib-only.

Usage:
    python compare.py --paper-a "A.pdf" --paper-b "B.pdf"
    python compare.py --paper-a "A.pdf" --paper-b "B.pdf" --focus "memory efficiency"
    python compare.py --paper-a "A.pdf" --paper-b "B.pdf" --json
    python compare.py --history
    python compare.py --history --json
    python compare.py --session <id>           # fetch a specific saved session
"""
from __future__ import annotations

import argparse
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


def _print_human_compare(result: dict) -> None:
    pa = result.get("paper_a") or {}
    pb = result.get("paper_b") or {}
    a_title = pa.get("title") or pa.get("name", "?")
    b_title = pb.get("title") or pb.get("name", "?")
    print(f"# Compare: {a_title}  vs  {b_title}\n")
    if result.get("focus"):
        print(f"> 对照角度: {result['focus']}\n")
    print(result.get("content", "(no content)"))
    rc = result.get("reasoning_content") or ""
    if rc.strip():
        print(f"\n<!-- 思考过程 ({len(rc)} 字) — 存在服务器端 history；如需查看请用 --session {result.get('session_id')} -->")


def _print_human_history(sessions: list) -> None:
    if not sessions:
        print("(no history)")
        return
    for s in sessions:
        titles = s.get("titles") or []
        label = " vs ".join(titles) if len(titles) >= 2 else (titles[0] if titles else "(untitled)")
        focus = f" — {s['focus']}" if s.get("focus") else ""
        print(f"[{s['id']}] {label}{focus}")
        print(f"    {s.get('preview', '')[:80].replace(chr(10), ' ')}…")
        print(f"    {time_str(s.get('time', 0))}\n")


def time_str(epoch: int) -> str:
    if not epoch:
        return "(unknown time)"
    import datetime as dt
    return dt.datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def main() -> int:
    ap = argparse.ArgumentParser(description="WhiskerShelf Compare CLI")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--paper-a", help="first paper filename (PDF)")
    ap.add_argument("--paper-b", help="second paper filename (PDF)")
    ap.add_argument("--focus", help="optional 1-2 sentence comparison angle")
    ap.add_argument("--history", action="store_true", help="list saved compare sessions")
    ap.add_argument("--session", help="fetch a specific saved session by id")
    ap.add_argument("--json", action="store_true", help="emit raw JSON")
    args = ap.parse_args()

    # Mutual exclusion
    flags = [bool(args.paper_a or args.paper_b), args.history, bool(args.session)]
    if sum(flags) != 1:
        ap.error("use exactly one mode: --paper-a/--paper-b, --history, or --session <id>")

    if args.history:
        data = _request("GET", "/api/ai/compare/history", base=args.base)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            _print_human_history(data.get("sessions") or [])
        return 0

    if args.session:
        data = _request("GET", "/api/ai/compare/history/" + urllib.parse.quote(args.session),
                        base=args.base)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            s = data.get("session") or {}
            if not s:
                print("(not found)")
                return 2
            pa = s.get("paper_a") or {}
            pb = s.get("paper_b") or {}
            a_title = pa.get("title") or pa.get("name", "?")
            b_title = pb.get("title") or pb.get("name", "?")
            print(f"# Saved Compare [{s.get('id')}]")
            print(f"  {a_title}  vs  {b_title}")
            if s.get("focus"):
                print(f"  focus: {s['focus']}")
            print(f"  saved: {time_str(s.get('time', 0))}\n")
            print(s.get("result", "(no content)"))
        return 0

    # Run mode
    if not args.paper_a or not args.paper_b:
        ap.error("--paper-a and --paper-b are both required in run mode")
    try:
        result = _request("POST", "/api/ai/compare", base=args.base,
                          body={"paper_a": args.paper_a, "paper_b": args.paper_b,
                                "focus": args.focus or ""})
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if not result.get("success"):
        print(f"server returned error: {result.get('error', 'unknown')}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human_compare(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
