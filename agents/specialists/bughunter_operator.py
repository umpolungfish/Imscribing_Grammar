#!/usr/bin/env python3
"""
bughunter_operator.py — the bug-hunter specialist, exactly like the other
operators (heterodox/math/chembio/editorial): launches a TrueAgenticAgent
with the specialist's system prompt, inherits all tools, Frobenius
verification, and the THINK->ACT->OBSERVE->UPDATE loop. Session persistence:
context auto-saves between invocations; use --continue or --session-id to
resume prior work with full message history and trajectory restored.

The system prompt IS the constitution (BUGHUNTER_CONSTITUTION.md, same dir):
identity + derived tuple, 7-stage pipeline, verification discipline,
vernacular layer, email template, initiation. It is the
interactive mode "like the one we are talking through right now": the human
talks, the agent acts and reports. The prepared email is handed to the
human to send; the agent does not stop and wait for permission to continue.

Usage:
    uv run agents/specialists/bughunter_operator.py "discover participating hosts and scan them"
    uv run agents/specialists/bughunter_operator.py --interactive
    uv run agents/specialists/bughunter_operator.py "prepare the email"
    uv run agents/specialists/bughunter_operator.py --continue "scan torproject.org"
    uv run agents/specialists/bughunter_operator.py --list-sessions
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

import true_agentic_agent as _taa
from true_agentic_agent import (
    TrueAgenticAgent,
    _load_system_prompt,
    _GRAMMAR_FIRST_RIDER,
    _PARTNERSHIP_RIDER,
    _EPISTEMIC_OUTLOOK_RIDER,
)
from session_db import get_session_db

# ── Dialetheic network spider (inclosure_telemetry) ──
from inclosure_telemetry.spider import (
    spider_walk as _spider_walk_fn,
    run_default as _spider_run_default,
    SPIDER_ID,
    SpiderReport,
    filter_spider,
)
from inclosure_telemetry.engine import Ledger, Rule, Event, close, closure_certificate
from inclosure_telemetry.lattice import Atom, name, parse, graph_neighbors
from inclosure_telemetry.trace import trace_all

_CONSTITUTION = Path(__file__).resolve().parent / "BUGHUNTER_CONSTITUTION.md"


def _load_constitution() -> str:
    return _CONSTITUTION.read_text(encoding="utf-8")


class BughunterOperator(TrueAgenticAgent):
    """The bug-hunter specialist. Operates the p4rapend framework
    end-to-end: browse bounty sites, discover participating hosts, scan
    (SAFE), verify, triage, race, report, translate, email.
    Session-aware: auto-saves trajectory and message history."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._custom_system_prompt = (
            _load_constitution() + _GRAMMAR_FIRST_RIDER + _PARTNERSHIP_RIDER + _EPISTEMIC_OUTLOOK_RIDER
        )
        self._session_id: str | None = None

    async def run(self, task: str) -> str:
        """Run with the bughunter constitution injected as the system prompt."""
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



    # ── Dialetheic network spider (inclosure_telemetry) ──
    def spider_run(self, ticks: int = 500, seed: str = "B",
                   spider_id: str = SPIDER_ID,
                   events_path: str | None = None,
                   rules_path: str | None = None,
                   weights: dict | None = None) -> dict:
        """Walk the dialetheic B-seam spider and return its report."""
        from pathlib import Path as _Path
        from inclosure_telemetry.engine import Rule as _Rule
        import json as _json
        rules = ()
        if rules_path is not None:
            rules = tuple(_Rule.from_dict(r) for r in _json.loads(_Path(rules_path).read_text()))
        report = _spider_run_default(
            seed=parse(seed),
            ticks=ticks,
            out_path=_Path(events_path) if events_path else None,
            rules=rules,
            spider_id=spider_id,
            weights=weights,
        )
        return {
            'spider_id': report.spider_id,
            'events_written': report.events_written,
            'seam_counts': {
                'classical': report.seam_counts.get(0, 0),
                'boundary_B': report.seam_counts.get(1, 0),
                'interior_B': report.seam_counts.get(2, 0),
            },
            'final_atom': name(report.final_atom),
            'certificate': report.certificate,
        }

    def spider_trace(self, events_path: str, spider_id: str = SPIDER_ID,
                     rules_path: str | None = None) -> dict:
        """Trace a spider's event ledger back to source events."""
        from pathlib import Path as _Path
        from inclosure_telemetry.engine import Ledger as _Ledger, Rule as _Rule
        import json as _json
        ledger = _Ledger()
        with _Path(events_path).open(encoding='utf-8') as fh:
            for line in fh:
                if line.strip():
                    ledger.append(Event.from_dict(_json.loads(line)))
        rules = ()
        if rules_path is not None:
            rules = tuple(_Rule.from_dict(r) for r in _json.loads(_Path(rules_path).read_text()))
        sub = filter_spider(ledger, spider_id)
        if not sub.events:
            raise KeyError(f'no events for spider {spider_id!r}')
        result = close(sub.projection(), rules)
        return {
            'spider_id': spider_id,
            'event_count': len(sub.events),
            'subjects': sorted(result.states),
            'lineage': trace_all(sub, result),
        }

    def spider_diagnose(self, system: str, environment: str) -> dict:
        """§33 diagnostic lookup on the spider's own state."""
        from inclosure_telemetry.diagnostics import diagnose as _diagnose
        return _diagnose(system, environment)

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
    p.add_argument("--stream", action="store_true", default=False,
                   help="Stream local generation token by token to stderr (also: IG_STREAM=1).")
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
    p.add_argument('--spider-run', action='store_true', help='Run the dialetheic B-seam spider.')
    p.add_argument('--spider-ticks', type=int, default=500, help='Spider tick count.')
    p.add_argument('--spider-seed', default='B', help='Spider starting site (T/F/B/N/TB/A/NONE).')
    p.add_argument('--spider-id', default='spider', help='Spider identifier.')
    p.add_argument('--spider-events', default='', help='Path to write/read spider event JSONL.')
    p.add_argument('--spider-rules', default='', help='Path to JSON closure rules for spider.')
    p.add_argument('--spider-trace', action='store_true', help='Trace spider events back to source.')
    p.add_argument('--spider-diag-system', default='', help='Spider diagnose system (N/T/F/B/TB/A).')
    p.add_argument('--spider-diag-env', default='', help='Spider diagnose environment (N/T/F/B/TB/A).')

    a = p.parse_args()
    # The flag and IG_STREAM are one switch: the reader in true_agentic_agent
    # consults the environment, so setting it here makes both spellings work.
    if getattr(a, "stream", False):
        os.environ["IG_STREAM"] = "1"

    # Resolve the model from IG_PROVIDER/IG_MODEL when --model is absent, as every
    # other operator does. Without this the help text lied — it claimed the env
    # was read — and a flagless run fell through to the base constructor's
    # hardcoded default, ignoring the shell's provider entirely.
    if not a.model:
        _m = os.environ.get("IG_MODEL", "")
        _pv = os.environ.get("IG_PROVIDER", "")
        if not _m:
            raise SystemExit(
                "IG_MODEL is not set. Set IG_PROVIDER and IG_MODEL, or pass --model.\n"
                "  export IG_PROVIDER=openrouter\n"
                "  export IG_MODEL=<model-id>")
        a.model = f"{_pv}:{_m}" if _pv and ":" not in _m else _m

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
    # output has no constructor slot — the trajectory is written after the run,
    # as the other operators do, not passed in.
    kw["verbose"] = not a.quiet

    # Resolve the session to continue from, if any.
    _recent = BughunterOperator.list_sessions(1)
    sid = a.session_id or (_recent[0]["id"] if (a.continue_ and _recent) else "")

    preloaded_messages: list | None = None
    preloaded_trajectory: list | None = None
    starting_winding_offset = 0
    if sid:
        _meta, _messages, _windings = BughunterOperator.load_session(sid)
        preloaded_messages = _messages
        preloaded_trajectory = _windings
        starting_winding_offset = len(_windings)
        kw["preloaded_messages"] = preloaded_messages
        kw["preloaded_trajectory"] = preloaded_trajectory
        kw["starting_winding_offset"] = starting_winding_offset


    op = BughunterOperator(**kw)
    op._session_id = sid
    # ── Spider CLI dispatch ──
    spider_mode = any([
        getattr(a, 'spider_run', False),
        getattr(a, 'spider_trace', False),
        bool(getattr(a, 'spider_diag_system', '')) or bool(getattr(a, 'spider_diag_env', '')),
    ])
    if spider_mode:
        if not op._session_id:
            op._session_id = sid or 'spider-cli'
        if a.spider_run:
            result = op.spider_run(
                ticks=a.spider_ticks,
                seed=a.spider_seed,
                spider_id=a.spider_id,
                events_path=a.spider_events or None,
                rules_path=a.spider_rules or None,
            )
        elif a.spider_trace:
            result = op.spider_trace(
                events_path=a.spider_events,
                spider_id=a.spider_id,
                rules_path=a.spider_rules or None,
            )
        else:
            result = op.spider_diagnose(
                system=a.spider_diag_system,
                environment=a.spider_diag_env,
            )
        import json as _json
        print(_json.dumps(result, indent=2, ensure_ascii=False))
        return


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
