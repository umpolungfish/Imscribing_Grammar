"""
lambda_commands.py — CLI commands for the λ-engine (Cantor monad × Gödel comonad).

Registered as `imscribe lambda <subcommand>`.

Subcommands
-----------
  demo      Full demo: monad, comonad, distributive law, Frobenius, crystal summary
  verify    Law verification table (monad / comonad / λ axioms)
  monad     Cantor power-set monad: unit, flatten, bind, powerset, diagonal
  comonad   Gödel encoding comonad: extract, duplicate, extend, Gödel sentence
  law       Apply the distributive law λ to a space-separated list of values
  frobenius Check (or demo) the Frobenius condition μ∘δ=id
  fano      Fano plane — octonionic δ and the Gödel co-typing

See lambda_engine.py and PRIMITIVE_THEOREMS §81 for theory.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Ensure project root is importable from any cwd
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from imscrbgrmr.lambda_engine import (
    P, G,
    lam,
    frobenius_check, frobenius_fails_for_halves,
    verify_monad_laws, verify_comonad_laws, verify_lambda_axioms,
)

console = Console()

_TICK = "[green]✓[/green]"
_CROSS = "[red]✗[/red]"


def _bool_cell(v: bool) -> str:
    return f"{_TICK} True" if v else f"{_CROSS} False"


# =============================================================================
# Lambda group
# =============================================================================

@click.group("lambda")
def lambda_group():
    """λ-Engine: Cantor monad P, Gödel comonad G, distributive law λ: PG → GP.

    \b
    Crystal addresses (Imscribing Grammar):
      monad_cantor            5,326,271   O₂     C=0.611
      comonad_goedel          5,311,151   O₂†    C=0.830   (co-type: octonions)
      distributive_law_lambda 6,734,591   O_∞     C=0.830   (co-type: grammar)

    \b
    Key theorem (§23/§81):
      d(monad ⊗ comonad, λ) = 2.2361 > 0
      λ must be planted — it is not derivable from P and G by tensor composition.

    \b
    Subcommands:
      demo       Full demo run
      verify     Law verification table
      monad      Cantor monad operations
      comonad    Gödel comonad operations
      law        Apply λ to a list of values
      frobenius  Check Frobenius condition μ∘δ=id
      fano       Fano plane / octonionic comultiplication
    """


# =============================================================================
# demo
# =============================================================================

@lambda_group.command("demo")
def demo_cmd():
    """Full demo: monad, comonad, distributive law, Frobenius, crystal summary."""

    xs = ["α", "β", "γ", "δ", "ε"]

    console.rule("[bold cyan]λ-ENGINE  ·  Cantor monad × Gödel comonad[/bold cyan]")
    console.print("[dim]g := Cantor ∘ Gödel  (PRIMITIVE_THEOREMS §81)[/dim]\n")

    # ── Monad ─────────────────────────────────────────────────────────────────
    console.rule("[bold]Cantor power-set monad P[/bold]")

    m = P(xs[:3])
    console.print(f"  m          = {m}")
    console.print(f"  η('α')     = {P.unit('α')}")

    console.print("\n  Powerset of {a,b,c}:")
    for s in sorted(P.powerset("abc"), key=lambda fs: (len(fs), sorted(fs))):
        console.print(f"    {set(s) if s else '∅'}")

    console.print("\n  Cantor diagonal witness:")
    enum = [P([0, 2]), P([1]), P([0, 1, 2])]
    d = P.diagonal_witness(enum)
    console.print(f"    enum = {enum}")
    console.print(f"    D    = {d}")

    monad_laws = verify_monad_laws(xs)
    console.print(f"\n  Monad laws: { {k: ('✓' if v else '✗') for k, v in monad_laws.items()} }")

    # ── Comonad ───────────────────────────────────────────────────────────────
    console.rule("[bold]Gödel encoding comonad G[/bold]")

    gx = G("α")
    console.print(f"  G('α')        = {gx}")
    console.print(f"  ε(G('α'))     = {gx.extract()!r}")
    console.print(f"  δ(G('α'))     = {gx.duplicate()}")
    console.print(f"  δ(δ(G('α'))) = {gx.duplicate().duplicate()}")

    gs = G.goedel_sentence("PA")
    console.print(f"\n  Gödel sentence (PA): {gs}")

    console.print("\n  Fano plane (octonionic δ):")
    for i in range(1, 8):
        od = G.octonionic_delta(i)
        console.print(f"    δ(e_{i}) = {od}")

    comonad_laws = verify_comonad_laws(xs)
    console.print(f"\n  Comonad laws: { {k: ('✓' if v else '✗') for k, v in comonad_laws.items()} }")

    # ── Distributive law ──────────────────────────────────────────────────────
    console.rule("[bold]Distributive law λ: P(G) → G(P)[/bold]")

    pg = P(G(x) for x in xs[:3])
    console.print(f"  Input  P(G(T)) = {pg}")
    gp = lam(pg)
    console.print(f"  Output G(P(T)) = {gp}")
    console.print(f"  Decoded P(T)   = {gp.extract()}")

    # ── Frobenius ─────────────────────────────────────────────────────────────
    console.rule("[bold]Frobenius condition μ∘δ=id[/bold]")

    fc = frobenius_check(G("α"))
    console.print(f"  frobenius_check(G('α')) = {fc}  ← True: λ planted")
    console.print()
    console.print(frobenius_fails_for_halves())

    # ── Axioms ────────────────────────────────────────────────────────────────
    console.rule("[bold]λ axiom verification[/bold]")

    axioms = verify_lambda_axioms(xs)
    for name, result in axioms.items():
        mark = "✓" if result else "✗"
        console.print(f"  {mark} {name}: {result}")

    # ── Crystal summary ───────────────────────────────────────────────────────
    console.rule("[bold]Crystal of Types addresses[/bold]")

    tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    tbl.add_column("System", style="cyan")
    tbl.add_column("Address", justify="right")
    tbl.add_column("Tier", justify="center")
    tbl.add_column("C", justify="right")
    tbl.add_column("Note")

    rows = [
        ("monad_cantor",            "5,326,271", "O₂",  "0.611", ""),
        ("comonad_goedel",          "5,311,151", "O₂†", "0.830", "co-type: octonions"),
        ("monad ⊗ comonad",         "—",         "O₂",  "—",     "d=2.2361 from λ"),
        ("distributive_law_lambda", "6,734,591", "O_∞",  "0.830", "co-type: grammar"),
    ]
    for row in rows:
        tbl.add_row(*row)
    console.print(tbl)

    console.print("[bold]Frobenius non-synthesizability (§23/§81):[/bold]")
    console.print("  d(monad ⊗ comonad, λ) = 2.2361  [P-gap=2.0, R-gap=1.0]")
    console.print("  λ is not recoverable from P and G by tensor composition.")
    console.print("  It must be planted — as a natural transformation, whole.")
    console.print()


# =============================================================================
# verify
# =============================================================================

@lambda_group.command("verify")
def verify_cmd():
    """Law verification table: monad laws, comonad laws, λ axioms."""

    xs = ["α", "β", "γ", "δ", "ε"]

    console.print()

    tbl = Table(title="Law Verification", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    tbl.add_column("Category", style="bold")
    tbl.add_column("Law / Axiom")
    tbl.add_column("Result", justify="center")

    for k, v in verify_monad_laws(xs).items():
        tbl.add_row("Monad P", k.replace("_", " "), _bool_cell(v))

    for k, v in verify_comonad_laws(xs).items():
        tbl.add_row("Comonad G", k.replace("_", " "), _bool_cell(v))

    for k, v in verify_lambda_axioms(xs).items():
        tbl.add_row("λ axioms", k.replace("_", " "), _bool_cell(v))

    console.print(tbl)
    console.print()


# =============================================================================
# monad
# =============================================================================

@lambda_group.command("monad")
@click.argument("values", nargs=-1, default=None)
def monad_cmd(values):
    """Cantor power-set monad P: unit, powerset, bind, diagonal witness.

    \b
    Optional VALUES: space-separated strings to use as the base set.
    Default: α β γ δ ε

    \b
    Examples:
      imscribe lambda monad
      imscribe lambda monad a b c d
    """

    xs: list[str] = list(values) if values else ["α", "β", "γ", "δ", "ε"]

    console.print()
    console.print(Panel(
        f"[bold cyan]Cantor power-set monad P[/bold cyan]\n"
        f"[dim]Crystal: 5,326,271  ·  O₂  ·  C=0.611[/dim]",
        expand=False,
    ))

    m = P(xs[:3])
    console.print(f"\n  Base set (first 3): {m}")
    console.print(f"  η({xs[0]!r})     = {P.unit(xs[0])}")
    console.print(f"  bind(m, x→{{x,x}}) = {m.bind(lambda x: P([x, x]))}")

    console.print(f"\n  Powerset of {{{', '.join(xs[:3])}}}:")
    for s in sorted(P.powerset(xs[:3]), key=lambda fs: (len(fs), sorted(repr(e) for e in fs))):
        console.print(f"    {set(s) if s else '∅'}")

    console.print("\n  Cantor diagonal witness:")
    enum = [P([0, 2]), P([1]), P([0, 1, 2])]
    d = P.diagonal_witness(enum)
    console.print(f"    D = {d}  (not in {{S_0, S_1, S_2}})")

    laws = verify_monad_laws(xs)
    status = "  ".join(f"{'✓' if v else '✗'} {k.replace('_',' ')}" for k, v in laws.items())
    console.print(f"\n  Laws:  {status}")
    console.print()


# =============================================================================
# comonad
# =============================================================================

@lambda_group.command("comonad")
@click.argument("value", default="α")
@click.option("--theory", "-t", default="PA", help="Theory name for Gödel sentence.")
def comonad_cmd(value: str, theory: str):
    """Gödel encoding comonad G: extract, duplicate, extend, Gödel sentence.

    \b
    Optional VALUE: string to wrap in G. Default: α
    Option  --theory: named theory for the Gödel sentence. Default: PA

    \b
    Examples:
      imscribe lambda comonad
      imscribe lambda comonad 'hello world'
      imscribe lambda comonad x --theory ZFC
    """

    console.print()
    console.print(Panel(
        f"[bold cyan]Gödel encoding comonad G[/bold cyan]\n"
        f"[dim]Crystal: 5,311,151  ·  O₂†  ·  C=0.830  ·  co-type: octonions[/dim]",
        expand=False,
    ))

    gx = G(value)
    console.print(f"\n  G({value!r})        = {gx}")
    console.print(f"  ε(G({value!r}))    = {gx.extract()!r}")
    console.print(f"  δ(G({value!r}))    = {gx.duplicate()}")
    console.print(f"  δ(δ(G({value!r}))) = {gx.duplicate().duplicate()}")

    gs = G.goedel_sentence(theory)
    console.print(f"\n  Gödel sentence ({theory}):")
    console.print(f"    {gs}")

    xs = ["α", "β", "γ", "δ", "ε"]
    laws = verify_comonad_laws(xs)
    status = "  ".join(f"{'✓' if v else '✗'} {k.replace('_',' ')}" for k, v in laws.items())
    console.print(f"\n  Laws:  {status}")
    console.print()


# =============================================================================
# law
# =============================================================================

@lambda_group.command("law")
@click.argument("values", nargs=-1, required=False)
def law_cmd(values):
    """Apply the distributive law λ: P(G(T)) → G(P(T)) to a set of values.

    \b
    VALUES: space-separated strings. Each is wrapped in G, collected into P,
    then λ is applied to produce G(P(T)).
    Default: α β γ

    \b
    Examples:
      imscribe lambda law
      imscribe lambda law a b c d
      imscribe lambda law proton neutron electron
    """

    xs: list[str] = list(values) if values else ["α", "β", "γ"]

    console.print()
    console.print(Panel(
        f"[bold cyan]Distributive law λ: P(G(T)) → G(P(T))[/bold cyan]\n"
        f"[dim]Crystal: 6,734,591  ·  O_∞  ·  C=0.830  ·  co-type: grammar[/dim]",
        expand=False,
    ))

    console.print(f"\n  Input values:   {xs}")

    pg = P(G(x) for x in xs)
    console.print(f"  P(G(T))  =  {pg}")

    gp = lam(pg)
    console.print(f"  G(P(T))  =  {gp}")
    console.print(f"  Decoded  =  {gp.extract()}")
    console.print(f"  Gödel code of the collection: #{gp.code}")
    console.print()


# =============================================================================
# frobenius
# =============================================================================

@lambda_group.command("frobenius")
@click.argument("value", default="α")
@click.option("--halves", is_flag=True, default=False, help="Show non-synthesizability proof.")
def frobenius_cmd(value: str, halves: bool):
    """Check the Frobenius condition μ∘δ=id for a value.

    \b
    VALUE: string to wrap in G. Default: α
    --halves: also explain why neither half alone can satisfy Frobenius.

    \b
    Examples:
      imscribe lambda frobenius
      imscribe lambda frobenius 'hello'
      imscribe lambda frobenius --halves
    """

    console.print()
    gx = G(value)
    result = frobenius_check(gx)

    color = "green" if result else "red"
    mark = "✓" if result else "✗"

    console.print(Panel(
        f"[bold]Frobenius condition μ∘δ=id[/bold]\n\n"
        f"  Input:   G({value!r}) = {gx}\n"
        f"  Result:  [{color}]{mark} {result}[/{color}]  ({'λ planted' if result else 'λ absent'})",
        expand=False,
    ))

    if halves:
        console.print()
        console.print(frobenius_fails_for_halves())
        console.print()
        console.print("[bold]Non-synthesizability (§23/§81):[/bold]")
        console.print("  d(monad ⊗ comonad, λ) = 2.2361")
        console.print("  λ cannot be assembled from P and G alone.")

    console.print()


# =============================================================================
# fano
# =============================================================================

@lambda_group.command("fano")
def fano_cmd():
    """Fano plane — octonionic comultiplication δ: e_i → (e_j, e_k).

    The Gödel comonad G co-types with the octonions ℍ_8 at distance d=0.
    The Fano plane's 7-line incidence structure realises δ: e_i → (e_j, e_k),
    exactly the comonad comultiplication.

    The non-associativity of ℍ_8 (∄ μ) is the algebraic face of Gödel
    incompleteness (∄ μ to close the provability loop). (§81.5.4)
    """

    console.print()
    console.print(Panel(
        "[bold cyan]Fano plane — octonionic δ[/bold cyan]\n"
        "[dim]G co-type: octonions ℍ_8  ·  d=0  ·  O₂†[/dim]",
        expand=False,
    ))

    tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    tbl.add_column("i", justify="right")
    tbl.add_column("δ(e_i)", justify="left")
    tbl.add_column("G-wrapped", style="dim")

    for i in range(1, 8):
        od = G.octonionic_delta(i)
        j, k = od.value
        tbl.add_row(str(i), f"(e_{j}, e_{k})", repr(od))

    console.print(tbl)
    console.print("  7 lines, each triple (i,j,k): e_i × e_j = e_k")
    console.print("  Non-associativity ↔ Gödel: same P_pipevar barrier (§81.5.4)")
    console.print()
