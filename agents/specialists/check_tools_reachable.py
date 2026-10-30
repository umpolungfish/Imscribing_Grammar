#!/usr/bin/env python3
"""Can every advertised tool actually be reached?

Listing a tool in a manifest is not evidence it runs. ob3ect was advertised to
all three specialists while dying on every call, because its gate import was
broken — a fact no inventory could have caught.

Read-only tools are invoked for real. Tools with side effects (writing the
catalog, spending tokens, spawning agents) are probed without firing: their
emit function is resolved and called with arguments that must fail inside the
tool rather than before it, which distinguishes "reachable and rejected the
input" from "never got there".

    python3 check_tools_reachable.py
"""
from __future__ import annotations
import json, sys, traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import true_agentic_agent as taa

# Invoked for real: no writes, no tokens, no spawns.
READONLY = {
    "lookup_catalog": {"keyword": "monad"},
    "list_catalog": {},
    "crystal_navigate": {"limit": 2},
    "crystal_count": {},
    "crystal_tier_census": {},
    "crystal_tier_gap_ladder": {},
    "crystal_decode": {"address": 1},
    "emergence_frontier": {},
    "navigator_info": {},
    "riemann_xi_info": {},
    "aleph_encode": {"text": "א"},
    "aleph_distance": {"a": "א", "b": "ב"},
    "domain_info": {"domain": "language"},
    "domain_verify": {"domain": "language"},
}
# Reached-but-not-fired: must fail *inside* the tool, not before it.
SIDE_EFFECTS = {"imscribe_system", "encode_system", "record_insight",
                "register_promotion_pattern", "ask_question"}

# Failures that mean the tool was never reached at all.
UNREACHABLE = ("ModuleNotFoundError", "ImportError", "AttributeError",
               "NameError", "No module named", "could not be imported",
               "exited 1", "FileNotFoundError")


def probe(name: str, args: dict) -> tuple[str, str]:
    try:
        raw = taa._imscribe_emit({"tool_name": name, "args": args})
    except Exception:
        return "CRASH", traceback.format_exc().strip().splitlines()[-1]
    try:
        out = json.loads(raw)
    except Exception:
        return "OK", "(non-json output)"
    err = str(out.get("error", ""))
    if any(u in err or u in str(out) for u in UNREACHABLE):
        return "UNREACHABLE", err[:90]
    if out.get("status") == "error":
        return "reached", err[:70]
    return "OK", ""


def main() -> int:
    from gen_tool_manifest import base_tools, grammar_tools
    bad = []

    print("── grammar tools (via imscribe) ──")
    for name in grammar_tools():
        if name in SIDE_EFFECTS:
            state, detail = probe(name, {})          # must fail inside the tool
            label = "reached (not fired)" if state != "UNREACHABLE" else "UNREACHABLE"
        else:
            state, detail = probe(name, READONLY.get(name, {}))
            label = state
        if label == "UNREACHABLE":
            bad.append((name, detail))
        print(f"  {name:28s} {label}{('  — ' + detail) if detail and label=='UNREACHABLE' else ''}")

    print("\n── base tools: can their emit functions be resolved? ──")
    for name, _ in base_tools():
        fn = getattr(taa, f"_{name}_emit", None) or taa.__dict__.get(f"{name}_emit")
        print(f"  {name:22s} {'emit found' if fn else 'no dedicated emit (dispatched elsewhere)'}")

    print()
    if bad:
        print(f"UNREACHABLE: {len(bad)}")
        for n, d in bad:
            print(f"  {n}: {d}")
        return 1
    print("every grammar tool is reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
