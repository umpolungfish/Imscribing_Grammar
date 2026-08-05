#!/usr/bin/env python3
"""
bughunter_operator.py — the bug-hunter specialist, exactly like the other
operators (heterodox/math/chembio/editorial): launches a TrueAgenticAgent
with the specialist's system prompt, inherits all tools, Frobenius
verification, and the THINK->ACT->OBSERVE->UPDATE loop. Session persistence:
context auto-saves between invocations; use --continue or --session-id to
resume prior work with full message history and trajectory restored.

The system prompt IS the constitution (BUGHUNTER_CONSTITUTION.md, same dir):
identity + derived tuple, 7-stage pipeline, verification discipline, WAIT
protocol, vernacular layer, email template, initiation. It is the
interactive mode "like the one we are talking through right now": the human
talks, the agent acts and reports, and the terminal state of every action
is WAIT unless the human says otherwise.

Usage:
    uv run agents/specialists/bughunter_operator.py "discover participating hosts and scan them"
    uv run agents/specialists/bughunter_operator.py --interactive
    uv run agents/specialists/bughunter_operator.py "prepare the email and wait"
    uv run agents/specialists/bughunter_operator.py --continue "scan torproject.org"
    uv run agents/specialists/bughunter_operator.py --list-sessions
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from true_agentic_agent import (TrueAgenticAgent,
                                _GRAMMAR_FIRST_RIDER, _PARTNERSHIP_RIDER)
from session_db import get_session_db

_CONSTITUTION = Path(__file__).resolve().parent / "BUGHUNTER_CONSTITUTION.md"


def _load_constitution() -> str:
    return _CONSTITUTION.read_text(encoding="utf-8")


class BughunterOperator(TrueAgenticAgent):
    """The bug-hunter specialist. Operates the p4rapend framework
    end-to-end: browse bounty sites, discover participating hosts, scan
    (SAFE), verify, triage, race, report, translate, email, WAIT.
    Session-aware: auto-saves trajectory and message history."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._custom_system_prompt = (
            _load_constitution() + _GRAMMAR_FIRST_RIDER + _PARTNERSHIP_RIDER
        )
        self._session_id: str | None = None

    async def run(self, task: str) -> str:
        """Run with the bughunter constitution injected as the system prompt."""
        import true_agentic_agent as _taa
        _original_load = _taa._load_system_prompt
        _taa._load_system_prompt = lambda: self._custom_system_prompt
        try:
            return await super().run(task)
        finally:
            _taa._load_system_prompt = _original_load

    def save_session(self, task: str, tags: list | None = None,
                     extra: dict | None = None) -> str:
        db = get_session_db()
        sid = db.save(self, task, tags=tags, extra=extra)
        self._session_id = sid
        return sid

    @staticmethod
    def load_session(session_id: str):
        db = get_session_db()
        return db.load(session_id)

    @staticmethod
    def list_sessions(limit: int = 20):
        db = get_session_db()
        return db.list_sessions(limit=limit)


def main():
    import argparse
    p = argparse.ArgumentParser(
        prog="bughunter_operator",
        description="The bug-hunter specialist — interactive, like the other operators",
    )
    p.add_argument("task", nargs="?", default=None,
                   help="Task description. If omitted, enters interactive mode.")
    p.add_argument("--interactive", "-i", action="store_true", help="Interactive mode.")
    p.add_argument("--model", default=None,
                   help="Model id, or provider:model. Taken from $IG_PROVIDER and $IG_MODEL.")
    p.add_argument("--max-windings", type=int, default=0,
                   help="Max windings. 0 (default) runs unbounded.")
    p.add_argument("--max-tokens", type=int, default=32768,
                   help="Max tokens per THINK phase (default: 32768)")
    p.add_argument("--base-url", default="", help="Override API base URL")
    p.add_argument("--api-key", default="", help="Override API key")
    p.add_argument("--output", "-o", default="", help="Save trajectory JSON to file")
    p.add_argument("--quiet", action="store_true", help="Suppress per-winding log")
    p.add_argument("--session-id", default="",
                   help="Continue from a prior session ID (restores message history).")
    p.add_argument("--continue", dest="continue_", action="store_true",
                   help="Continue from the most recent saved session.")
    p.add_argument("--list-sessions", action="store_true",
                   help="List saved sessions and exit.")
    p.add_argument("--no-save", action="store_true",
                   help="Do not save the session.")
    a = p.parse_args()

    if a.list_sessions:
        # list_sessions returns a list of row dicts, not (id, meta) pairs.
        for s in BughunterOperator.list_sessions():
            print(f"{s['id']}\t{s.get('created_at', '')[:19]}\t"
                  f"{s.get('task', '')[:60]}")
        return

    kw = {}
    if a.model:
        kw["model"] = a.model
    if a.max_windings:
        kw["max_windings"] = a.max_windings
    # The base constructor names it max_think_tokens; max_tokens is the flag,
    # not the parameter, and passing the flag name raised TypeError on every run.
    if a.max_tokens:
        kw["max_think_tokens"] = a.max_tokens
    if a.base_url:
        kw["base_url"] = a.base_url
    if a.api_key:
        kw["api_key"] = a.api_key
    # verbose is the base's knob; quiet is this launcher's flag, resolved here.
    # output has no constructor slot — the trajectory is written after the run.
    kw["verbose"] = not a.quiet

    op = BughunterOperator(**kw)

    # list_sessions returns row dicts; the most recent id is [0]["id"], not [0][0].
    _recent = BughunterOperator.list_sessions(1)
    sid = a.session_id or (_recent[0]["id"] if (a.continue_ and _recent) else "")
    if sid:
        op._session_id = sid

    def _one(task):
        result = asyncio.run(op.run(task))
        if not a.no_save:
            op.save_session(task)
        # --output was accepted and then ignored; honour it. The trajectory is
        # written after the run, as the other operators do, not passed in.
        if a.output:
            import json as _json
            with open(a.output, "w", encoding="utf-8") as fh:
                _json.dump({
                    "specialist": "bughunter_operator",
                    "task": task,
                    "result": result,
                    "structural_type": getattr(op, "structural_type", None),
                }, fh, indent=2, ensure_ascii=False)
            print(f"  trajectory saved to {a.output}")

    if a.interactive or not a.task:
        print("bughunter operator — interactive. Enter a task, or 'quit' to end.")
        while True:
            try:
                line = input("hunter> ").strip()
            except EOFError:
                break
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                break
            _one(line)
    else:
        _one(a.task)


if __name__ == "__main__":
    main()
