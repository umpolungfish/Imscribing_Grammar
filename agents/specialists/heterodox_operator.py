#!/usr/bin/env python3
"""
heterodox_operator.py — the Heter⊙d⊙x (Grammar-first, blended across every tool family).

Launches a TrueAgenticAgent with the Heter⊙d⊙x system prompt.
Inherits all tools, Frobenius verification, and the THINK→ACT→OBSERVE→UPDATE loop.
Session persistence: context auto-saves between invocations. Use --continue or --session-id
to resume prior work with full message history and trajectory restored.

Usage:
    uv run agents/specialists/heterodox_operator.py "Derive the Djed foundation course from the kernel-cosmos frontier"
    uv run agents/specialists/heterodox_operator.py "This route is called obstructed; find what the obstruction assumed"
    uv run agents/specialists/heterodox_operator.py "Carry the braid word into the catalog as the same tuple"
    uv run agents/specialists/heterodox_operator.py --continue "Close the pair that would not close"
    uv run agents/specialists/heterodox_operator.py --list-sessions
"""

from __future__ import annotations

import asyncio
import sys
import os
from pathlib import Path

_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from true_agentic_agent import (TrueAgenticAgent, _load_system_prompt,
                                _GRAMMAR_FIRST_RIDER, _PARTNERSHIP_RIDER)
from specialists import HETERODOX_SPECIALIST_PROMPT
from session_db import get_session_db


class HeterodoxOperator(TrueAgenticAgent):
    """The Heter⊙d⊙x — works from inside the Grammar, blending every tool family.
    Received constraints are findings about the tools that produced them.
    Session-aware: auto-saves trajectory and message history."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The base run() appends _load_imsgct_context() itself, so adding it
        # here too put the block in twice. The partnership rider is appended
        # on every base load path (§P-652); the swap bypasses that, so it is
        # carried explicitly.
        self._custom_system_prompt = (
            HETERODOX_SPECIALIST_PROMPT + _GRAMMAR_FIRST_RIDER + _PARTNERSHIP_RIDER
        )
        self._session_id: str | None = None

    async def run(self, task: str) -> str:
        """Run with the Heter⊙d⊙x system prompt injected."""
        import true_agentic_agent as _taa
        _original_load = _taa._load_system_prompt
        _taa._load_system_prompt = lambda: self._custom_system_prompt
        try:
            return await super().run(task)
        finally:
            _taa._load_system_prompt = _original_load

    def save_session(self, task: str, tags: list[str] | None = None,
                     extra: dict | None = None) -> str:
        """Save current trajectory and messages to the session DB. Returns session_id."""
        db = get_session_db()
        sid = db.save(self, task, tags=tags, extra=extra)
        self._session_id = sid
        return sid

    @staticmethod
    def load_session(session_id: str):
        """Load a prior session. Returns (metadata, messages, windings)."""
        db = get_session_db()
        return db.load(session_id)

    @staticmethod
    def list_sessions(limit: int = 20):
        """List recent saved sessions."""
        db = get_session_db()
        return db.list_sessions(limit=limit)

def main():
    import argparse
    p = argparse.ArgumentParser(
        prog="heterodox_operator",
        description="The Heter⊙d⊙x — Grammar-first, blended across every tool family",
    )
    p.add_argument("task", nargs="?", default=None,
                   help="Task description. If omitted, enters interactive mode.")
    p.add_argument("--interactive", "-i", action="store_true",
                   help="Interactive mode.")
    # Wired to the environment, with no baked-in model. Resolved after
    # parsing so --model can stand in when the environment is not set.
    p.add_argument("--model", default=None,
                   help="Model id, or provider:model. Taken from $IG_PROVIDER and $IG_MODEL.")
    p.add_argument("--stream", action="store_true", default=False,
                   help="Stream local generation token by token to stderr (also: IG_STREAM=1).")
    p.add_argument("--max-windings", type=int, default=0,
                   help="Max windings. 0 (default) runs unbounded: the loop ends on done, on the emission gate, or on context pressure.")
    p.add_argument("--max-tokens", type=int, default=32768,
                   help="Max tokens per THINK phase (default: 32768)")
    p.add_argument("--base-url", default="", help="Override API base URL")
    p.add_argument("--api-key", default="", help="Override API key")
    p.add_argument("--output", "-o", default="", help="Save trajectory JSON to file")
    p.add_argument("--quiet", action="store_true", help="Suppress per-winding log")
    # ── Session persistence ──
    p.add_argument("--session-id", default="",
                   help="Continue from a prior session ID (restores message history).")
    p.add_argument("--continue", dest="continue_", action="store_true",
                   help="Continue from the most recent saved session.")
    p.add_argument("--list-sessions", action="store_true",
                   help="List saved sessions and exit.")
    p.add_argument("--no-save", action="store_true",
                   help="Disable auto-save after run.")
    args = p.parse_args()
    # The flag and IG_STREAM are one switch: the reader in true_agentic_agent
    # consults the environment, so setting it here makes both spellings work.
    if getattr(args, "stream", False):
        os.environ["IG_STREAM"] = "1"

    if not args.model:
        _m = os.environ.get("IG_MODEL", "")
        _pv = os.environ.get("IG_PROVIDER", "")
        if not _m:
            raise SystemExit(
                "IG_MODEL is not set. Set IG_PROVIDER and IG_MODEL, or pass --model.\n"
                "  export IG_PROVIDER=openrouter\n"
                "  export IG_MODEL=<model-id>")
        args.model = f"{_pv}:{_m}" if _pv and ":" not in _m else _m

    # ── Session listing ──
    if args.list_sessions:
        sessions = HeterodoxOperator.list_sessions()
        if not sessions:
            print("No saved sessions.")
            return
        print(f"{'Session ID':<36} {'Date':<22} {'Model':<18} {'W':<6} Task")
        print("-" * 110)
        for s in sessions:
            print(f"{s['id']:<36} {s['created_at'][:19]:<22} {s['model']:<18} "
                  f"{s['windings_count']:<6} {s.get('task_preview', '')[:50]}")
        return

    # ── Resolve session continuation ──
    preloaded_msgs = None
    preloaded_traj = None
    winding_offset = 0
    restored_sid = ""

    if args.continue_:
        sessions = HeterodoxOperator.list_sessions(limit=1)
        if sessions:
            restored_sid = sessions[0]["id"]
            _meta, preloaded_msgs, winding_dicts = HeterodoxOperator.load_session(restored_sid)
            preloaded_traj = winding_dicts
            winding_offset = len(winding_dicts)
            print(f"  [Continuing from session {restored_sid[:24]}… — "
                  f"{len(preloaded_msgs)} messages, {winding_offset} windings restored]")
        else:
            print("[No prior sessions to continue from. Starting fresh.]")
    elif args.session_id:
        try:
            restored_sid = args.session_id
            _meta, preloaded_msgs, winding_dicts = HeterodoxOperator.load_session(restored_sid)
            preloaded_traj = winding_dicts
            winding_offset = len(winding_dicts)
            print(f"  [Restored session {restored_sid[:24]}… — "
                  f"{len(preloaded_msgs)} messages, {winding_offset} windings restored]")
        except KeyError:
            print(f"[Session not found: {args.session_id}. Starting fresh.]")
            restored_sid = ""    # ── Interactive mode ──
    if args.interactive or not args.task:
        print("═" * 72)
        print("  THE HETER⊙D⊙X — Interactive Mode (session-persistent)")
        print(f"  Model: {args.model}  |  Max windings: {args.max_windings}")
        print(f"  Session: {restored_sid[:24] + '…' if restored_sid else 'new'}")
        print("  Surfaces: Grammar core, mOMonadOS, m3iosis, Lean, ob3ect, para_vm")
        print("  Enter task → blank line submits. 'quit' or Ctrl-D exits.")
        print("═" * 72)

        agent = HeterodoxOperator(
            model=args.model,
            max_windings=args.max_windings,
            max_think_tokens=args.max_tokens,
            base_url=args.base_url or None,
            api_key=args.api_key or None,
            verbose=not args.quiet,
            preloaded_messages=preloaded_msgs,
            preloaded_trajectory=preloaded_traj,
            starting_winding_offset=winding_offset,
        )

        session_task_log: list[str] = []
        try:
            while True:
                task_lines = []
                try:
                    first = input(">>> ").rstrip()
                except KeyboardInterrupt:
                    # At the prompt Ctrl-C clears the line; Ctrl-D or 'quit' exits.
                    print()
                    continue
                if first.lower() in ("quit", "exit", "q"):
                    break
                task_lines.append(first)
                abandoned = False
                while True:
                    try:
                        line = input("... ").rstrip()
                    except KeyboardInterrupt:
                        # Abandon this entry, keep the session and its context.
                        print()
                        abandoned = True
                        break
                    if not line:
                        break
                    if line.lower() in ("quit", "exit", "q"):
                        break
                    task_lines.append(line)
                if abandoned:
                    continue
                task = "\n".join(task_lines)
                session_task_log.append(task)

                result = asyncio.run(agent.run(task))
                paused = getattr(agent, "interrupted", False)
                print(f"\n{'─'*52}")
                print(result)
                print(f"{'─'*52}")
                if paused:
                    print("  [context held — your next entry continues this "
                          "trajectory; it does not start a new one]")
                print(f"Windings:{len(agent.trajectory)}  "
                      f"Frobenius:{agent.frobenius_ratio:.0%}  "
                      f"Tier:{agent.structural_type.get('ouroboricity', '?')}")

                if not args.no_save:
                    sid = agent.save_session(
                        f"interactive[{len(session_task_log)}]: {task[:80]}",
                        tags=["heterodox", "interactive"],
                    )
                    print(f"  Session: {sid}")

                # Feed the conversation back INTO the agent. run() reads
                # self.preloaded_messages, which was set once at construction,
                # so without this every task after the first rebuilt _messages
                # from scratch and the agent forgot the exchange it had just
                # had — inside a single interactive session.
                preloaded_msgs = list(agent._messages)
                preloaded_traj = list(agent.trajectory) if hasattr(agent, 'trajectory') else []
                winding_offset = len(agent.trajectory)
                agent.preloaded_messages = preloaded_msgs
                agent.preloaded_trajectory = preloaded_traj
                agent.starting_winding_offset = winding_offset

        except (EOFError, KeyboardInterrupt):
            print("\n[heter⊙d⊙x session ended]")
        return

    # ── Single-task mode ──
    agent = HeterodoxOperator(
        model=args.model,
        max_windings=args.max_windings,
        max_think_tokens=args.max_tokens,
        base_url=args.base_url or None,
        api_key=args.api_key or None,
        verbose=not args.quiet,
        preloaded_messages=preloaded_msgs,
        preloaded_trajectory=preloaded_traj,
        starting_winding_offset=winding_offset,
    )

    result = asyncio.run(agent.run(args.task))
    print(f"\n{'─'*72}")
    print(result)
    print(f"{'─'*72}")
    print(f"  Windings: {len(agent.trajectory)}  "
          f"Frobenius: {agent.frobenius_ratio:.0%}  "
          f"Tier: {agent.structural_type.get('ouroboricity', '?')}")

    if not args.no_save:
        sid = agent.save_session(args.task, tags=["heterodox"])
        print(f"  Session saved: {sid}")

    if args.output:
        import json as _json
        payload = {
            "specialist": "heterodox_operator",
            "session_id": agent._session_id,
            "task": args.task,
            "result": result,
            "structural_type": agent.structural_type,
            "trajectory": [
                {
                    "winding": c.winding,
                    "action": c.action_name,
                    "frobenius": c.frobenius_closed,
                    "done": c.done,
                }
                for c in agent.trajectory
            ],
        }
        with open(args.output, "w") as fh:
            _json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"  Trajectory saved to {args.output}")


if __name__ == "__main__":
    main()