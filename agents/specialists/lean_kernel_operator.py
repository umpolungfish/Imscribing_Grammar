#!/usr/bin/env python3
"""
lean_kernel_operator.py — compatibility shim.

Lean certification is subsumed by IMASMOperator. This module exists only so
legacy imports and launch scripts do not break; it does not define a second
specialist identity or register a second Lean tool.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from imasm_operator import IMASMOperator, _lean_kernel_emit, _lean_kernel_verify

LeanKernelOperator = IMASMOperator


def main():
    import argparse

    p = argparse.ArgumentParser(
        prog="lean_kernel_operator",
        description=(
            "Compatibility entry point. Lean certification is integrated into "
            "IMASMOperator; this launches that operator."
        ),
    )
    p.add_argument("task", nargs="?", default=None)
    p.add_argument("--model", default=None)
    p.add_argument("--stream", action="store_true", default=False)
    args = p.parse_args()

    if args.stream:
        os.environ["IG_STREAM"] = "1"

    kwargs = {}
    if args.model:
        kwargs["model"] = args.model
    agent = IMASMOperator(**kwargs)
    task = args.task or (
        "Use the integrated lean_kernel lane to inspect the live p4ramill "
        "project. Run a tool before concluding."
    )
    print(asyncio.run(agent.run(task)))


if __name__ == "__main__":
    main()
