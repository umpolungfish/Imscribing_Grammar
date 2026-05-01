"""
Imscribing Grammar interactive menu — Option A (Rich prompt loop).

Launch with: imscribe menu
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.prompt import Prompt

console = Console()


def _load_dotenv() -> None:
    """Inject .env vars into os.environ (only if not already set) so subprocesses inherit them."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    with env_path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


_load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Command schema
# Each entry: (cli_name, short_description, arg_prompts)
# arg_prompts: list of (label, kind) where kind is:
#   "name"   — single synthon name
#   "names+" — space-separated synthon names (2+)
#   "name?"  — optional synthon name (blank = omit)
#   "target" — target string (e.g. lift type)
#   "str"    — free string
#   "float"  — float value
# ─────────────────────────────────────────────────────────────────────────────

CATEGORIES = [
    {
        "key": "1",
        "name": "Lookup",
        "color": "cyan",
        "hint": "analyze · compare · ouroborics · distance · thermo",
        "commands": [
            ("analyze",    "Full tuple breakdown for a synthon",
             [("Synthon", "name")]),
            ("compare",    "Side-by-side primitive comparison",
             [("Synthons (space-separated, 2+)", "names+")]),
            ("ouroborics", "Frobenius ouroboricity tier",
             [("Synthon  (blank = full catalog)", "name?")]),
            ("distance",   "Weighted structural distance",
             [("Synthon A", "name"), ("Synthon B", "name")]),
            ("info-bits",  "I(bits) from degrees of freedom",
             [("Synthon", "name")]),
            ("thermo",     "Thermodynamic efficiency η_CP and ξ_CP",
             [("Synthon", "name"), ("ΔG kJ/mol  (blank = auto)", "str?")]),
        ],
    },
    {
        "key": "2",
        "name": "Algebra",
        "color": "green",
        "hint": "meet · join · tensor · check · cofactor",
        "commands": [
            ("meet",     "Lattice meet ⊓ (greatest lower bound)",
             [("Synthon A", "name"), ("Synthon B", "name")]),
            ("join",     "Lattice join ⊔ (least upper bound)",
             [("Synthon A", "name"), ("Synthon B", "name")]),
            ("tensor",   "Tensor product ⊗ (co-assembly)",
             [("Synthon A", "name"), ("Synthon B", "name")]),
            ("check",    "Structural compatibility check",
             [("Synthon A", "name"), ("Synthon B", "name")]),
            ("cofactor", "Cofactor residual B  s.t. A ⊗ B = target",
             [("Factor A", "name"), ("Target", "name")]),
            ("factor",   "Strongest meet-irreducible factor",
             [("Synthon", "name")]),
        ],
    },
    {
        "key": "3",
        "name": "Analysis",
        "color": "yellow",
        "hint": "criticality · perturb · phase-diagram · rules",
        "commands": [
            ("criticality",       "G/D degeneracy + criticality analysis",
             [("Synthon", "name")]),
            ("criticality-probe", "Φ_c candidacy + Axiom 5 probe",
             [("Synthon", "name")]),
            ("perturb sweep",      "Primitive Jacobian / sensitivity sweep",
             [("Synthon", "name"), ("ΔG kJ/mol (e.g. -10.0)", "float")]),
            ("phase-diagram",     "Tuple-space phase diagram",
             [("Synthons (space-separated)", "names+")]),
            ("transition",        "Phase transition classification",
             [("Synthon A", "name"), ("Synthon B", "name")]),
            ("rules",             "Discover predictive rules from catalog",
             []),
        ],
    },
    {
        "key": "4",
        "name": "Design",
        "color": "magenta",
        "hint": "pipeline · lift · retrodesign · generate · peel",
        "commands": [
            ("pipeline",    "Chain algebra ops into a design pipeline",
             [("Start synthon", "name"), ("Steps  e.g. meet:gluon lift:critical", "str")]),
            ("lift",        "Apply a dimensional/criticality lift",
             [("Synthon", "name"),
              ("Target  (temporal · spatial · critical · molecular)", "target")]),
            ("retrodesign", "Constraint-directed retrosynthetic decomposition",
             [("Synthon", "name")]),
            ("retrosyn",    "Find catalog pairs whose tensor = target",
             [("Target synthon", "name")]),
            ("generate",    "Generate synthon from natural language",
             [("Description", "str")]),
            ("path",        "Shortest HotSwap path between two synthons",
             [("Source", "name"), ("Target", "name")]),
            ("peel",        "Descend one tier on a single primitive",
             [("Synthon", "name"), ("Primitive  (e.g. Phi, F, K, Omega)", "str")]),
        ],
    },
    {
        "key": "5",
        "name": "Catalog",
        "color": "blue",
        "hint": "search · remove · export · audit",
        "commands": [
            ("catalog search", "Full-text / primitive search",
             [("Query", "str")]),
            ("catalog list",   "List all synthons",
             []),
            ("remove",         "Remove a synthon by name",
             [("Synthon name", "name")]),
            ("export",         "Export catalog to file",
             [("Output path  (blank = stdout)", "str?")]),
            ("audit",          "Audit catalog for grounding issues",
             []),
        ],
    },
    {
        "key": "6",
        "name": "Advanced",
        "color": "red",
        "hint": "ensemble · trajectory · isomorphs · validate",
        "commands": [
            ("ensemble",        "Multi-synthon emergent composition",
             [("Synthons (space-separated)", "names+")]),
            ("trajectory",      "Temporal pathway encoding",
             [("Synthon", "name")]),
            ("isomorphs",       "Cross-domain structural isomorphs",
             [("Synthon", "name")]),
            ("principal-decomp","Recursive factor decomposition",
             [("Synthon", "name")]),
            ("validate",        "Validate against composition axioms",
             [("Synthon", "name")]),
            ("hotswap",         "Validate a hot-swap transition",
             [("Source", "name"), ("Target", "name")]),
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _header() -> None:
    try:
        import json as _json
        from pathlib import Path as _Path
        _catalog_path = _Path(__file__).resolve().parent.parent / "IG_catalog.json"
        if _catalog_path.exists():
            with open(_catalog_path, "r", encoding="utf-8") as _f:
                n = len(_json.load(_f))
        else:
            from imscrbgrmr.registry import global_catalog
            n = len(list(global_catalog))
    except Exception:
        n = "?"
    console.print()
    console.print(Panel(
        f"[bold white]Imscribing Grammar[/bold white]  [dim]12 primitives · {n} synthons[/dim]",
        expand=False, border_style="dim white",
    ))
    console.print()


def _main_menu() -> Optional[str]:
    for cat in CATEGORIES:
        key   = cat["key"]
        name  = cat["name"]
        color = cat["color"]
        hint  = cat["hint"]
        console.print(f"  [bold {color}][{key}][/bold {color}]  "
                      f"[bold]{name:<10}[/bold] [dim]{hint}[/dim]")
    console.print()
    console.print("  [dim][q]  Quit[/dim]")
    console.print()
    return Prompt.ask("[bold]>[/bold]", console=console).strip().lower()


def _category_menu(cat: dict) -> Optional[str]:
    color = cat["color"]
    console.print()
    console.print(Rule(f"[bold {color}]{cat['name']}[/bold {color}]"))
    console.print()
    for i, (cmd, desc, _) in enumerate(cat["commands"], 1):
        console.print(f"  [bold {color}][{i}][/bold {color}]  "
                      f"[bold]{cmd:<22}[/bold] [dim]{desc}[/dim]")
    console.print()
    console.print("  [dim][b]  Back[/dim]")
    console.print()
    return Prompt.ask("[bold]>[/bold]", console=console).strip().lower()


def _collect_args(prompts: list) -> Optional[List[str]]:
    """Prompt for each argument. Returns list of CLI tokens, or None on cancel."""
    tokens: List[str] = []
    for label, kind in prompts:
        val = Prompt.ask(f"  [cyan]{label}[/cyan]", console=console).strip()
        if val.lower() in ("q", "quit", "cancel"):
            return None
        if kind == "name?" and not val:
            continue  # optional — skip
        if kind == "str?" and not val:
            continue
        if kind == "names+":
            tokens.extend(val.split())
        elif kind == "str" and " " in val and not val.startswith('"'):
            # pipeline steps etc. — pass as individual tokens
            tokens.extend(val.split())
        elif kind == "float":
            tokens.append(val if val else "0.0")
        else:
            if val:
                tokens.append(val)
    return tokens


def _run_command(cmd_name: str, arg_tokens: List[str]) -> None:
    """Execute imscribe <cmd> <args> as a subprocess."""
    # Handle "catalog search" style compound commands
    parts = cmd_name.split()
    cli_args = [sys.executable, "-m", "imscrbgrmr.cli"] + parts + arg_tokens

    # Special handling for perturb sweep: [name, delta_g] → name --delta-g val
    if cmd_name == "perturb sweep" and len(arg_tokens) >= 2:
        cli_args = [sys.executable, "-m", "imscrbgrmr.cli",
                    "perturb", "sweep", arg_tokens[0], "--delta-g", arg_tokens[1]]

    # Special handling for thermo: [name] or [name, delta_g] → name [--delta-g val]
    if cmd_name == "thermo":
        if len(arg_tokens) >= 2:
            cli_args = [sys.executable, "-m", "imscrbgrmr.cli",
                        "thermo", arg_tokens[0], "--delta-g", arg_tokens[1]]
        else:
            cli_args = [sys.executable, "-m", "imscrbgrmr.cli",
                        "thermo", arg_tokens[0]]

    # Special handling for pipeline --step args
    if cmd_name == "pipeline" and arg_tokens:
        start = arg_tokens[0]
        steps = arg_tokens[1:]
        step_flags: List[str] = []
        for s in steps:
            step_flags += ["--step", s]
        cli_args = [sys.executable, "-m", "imscrbgrmr.cli",
                    "pipeline", start] + step_flags

    console.print()
    console.rule("[dim]output[/dim]")
    console.print()
    try:
        result = subprocess.run(
            cli_args,
            cwd=None,
            text=True,
        )
    except Exception as e:
        console.print(f"[red]Error running command: {e}[/red]")
    # Flush and reset terminal state before reprompting
    import sys as _sys
    _sys.stdout.flush()
    _sys.stderr.flush()
    console.print()
    console.rule("[dim]─── done — press Enter to return to menu ───[/dim]")
    console.print()
    try:
        Prompt.ask("", default="", console=console)
    except (EOFError, KeyboardInterrupt):
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────────────

def run_menu() -> None:
    console.clear()
    _header()

    while True:
        choice = _main_menu()

        if choice in ("q", "quit", "exit"):
            console.print("\n[dim]Goodbye.[/dim]\n")
            break

        cat = next((c for c in CATEGORIES if c["key"] == choice), None)
        if cat is None:
            console.print("[red]  Invalid choice.[/red]")
            continue

        # Category loop
        while True:
            console.clear()
            _header()
            cmd_choice = _category_menu(cat)

            if cmd_choice in ("b", "back", ""):
                console.clear()
                _header()
                break

            if cmd_choice in ("q", "quit"):
                console.print("\n[dim]Goodbye.[/dim]\n")
                return

            try:
                idx = int(cmd_choice) - 1
            except ValueError:
                console.print("[red]  Invalid choice.[/red]")
                continue

            if idx < 0 or idx >= len(cat["commands"]):
                console.print("[red]  Invalid choice.[/red]")
                continue

            cmd_name, desc, arg_prompts = cat["commands"][idx]

            console.print()
            console.print(f"  [bold]{cmd_name}[/bold] — [dim]{desc}[/dim]")
            console.print()

            arg_tokens = _collect_args(arg_prompts)
            if arg_tokens is None:
                console.print("[dim]  Cancelled.[/dim]")
                continue

            _run_command(cmd_name, arg_tokens)
