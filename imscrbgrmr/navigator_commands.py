"""
navigator_commands.py — CLI commands for all Imscribing Grammar navigators.

Registered as `imscribe nav <family> <subcommand>`.

Families
--------
  crystal   Crystal of Types navigator (17,280,000 structural types)
  domain    Language / Civilization / Ecology / Consciousness navigators (§74–§77)
  riemann   Riemann ξ navigator — functional-equation architecture
  zfc       ZFC transmissibility navigator — encode / probe
  ads_cft   AdS/CFT imscriptive duality navigator — bulk/boundary + RG flow
  mirror    Mirror symmetry navigator — Calabi-Yau / A-B model correspondence
  tqft      TQFT navigator — knot invariants, Chern-Simons, modular tensor categories

Theory references: PRIMITIVE_THEOREMS §64/§69, IG_ONTICS §XXXV–§XL,
IG_DIAPHORICS §CXLII–§CXLVI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# New navigator imports
from navigators.category_theory_navigator import CategoryNavigator
from navigators.homotopy_type_theory_navigator import HTTNavigator
from navigators.algebraic_geometry_navigator import AGNavigator
from navigators.quantum_field_theory_navigator import QFTNavigator
from navigators.langlands_program_navigator import LanglandsNavigator
from navigators.representation_theory_navigator import RepTheoryNavigator

console = Console()

_TICK = "[green]✓[/green]"
_CROSS = "[red]✗[/red]"


# =============================================================================
# Top-level nav group
# =============================================================================

@click.group("nav")
def nav_group():
    """Navigator suite: Crystal of Types, Domain, Riemann ξ, ZFC, AdS/CFT, Mirror, TQFT.

    \b
    Families:
      crystal   17,280,000-type Crystal of Types — encode/decode/query/census
      domain    Language · Civilization · Ecology · Consciousness (§74–§77)
      riemann   Riemann ξ navigator — functional-equation / GUE architecture
      zfc       ZFC transmissibility probe — grammar-formula roundtrip losses
      ads_cft   AdS/CFT imscriptive duality — bulk/boundary distance, RG flow
      mirror    Mirror symmetry — Calabi-Yau pairs, A-B model, T-duality tower
      tqft      TQFT — knot invariants, Chern-Simons, modular tensor categories

    \b
    Examples:
      imscribe nav crystal describe
      imscribe nav crystal nearest Phi=⊙ P=P_doublebarpipe -n 5
      imscribe nav domain info --domain consciousness
      imscribe nav domain verify --domain language
      imscribe nav riemann describe
      imscribe nav zfc describe
      imscribe nav ads_cft describe
      imscribe nav mirror describe
      imscribe nav tqft describe
    """


# =============================================================================
# CRYSTAL navigator group
# =============================================================================

@nav_group.group("crystal")
def crystal_group():
    """Crystal of Types navigator (§64/§69).

    \b
    Architecture (imscriptive, Frobenius O_∞):
      Boundary: (Φ, P, Ω, D) → 400 tier cells
      Bulk:     (T, R, F, K, G, Γ, H, S) → 43,200 inner types per cell
      Total:    400 × 43,200 = 17,280,000 types

    \b
    Subcommands:
      describe   Self-description: navigator encoding and crystal stats
      gap        Tier gap ladder (§69.1)
      census     Full tier census
      verify     Frobenius codec roundtrip verification
      encode     Tuple → canonical address
      decode     Address → tuple
      nearest    Nearest catalog entries to a partial/full tuple
      count      Count matching types
      query      Imscriptive boundary query (Φ, P, Ω, D → tier cells)
    """


def _load_crystal():
    from navigators.crystal_navigator import CrystalNavigator
    return CrystalNavigator()


@crystal_group.command("describe")
def crystal_describe():
    """Navigator self-description: encoding, distances, crystal stats."""
    nav = _load_crystal()
    nav.describe()


@crystal_group.command("gap")
def crystal_gap():
    """Tier gap ladder (§69.1): d(O₀→O₁), …, d(O₂†→O_∞)."""
    nav = _load_crystal()
    nav.print_tier_gap_ladder()


@crystal_group.command("census")
def crystal_census():
    """Full tier census: cells and types per ouroboricity tier."""
    nav = _load_crystal()

    tbl = Table(title="Crystal Tier Census", box=box.ROUNDED, header_style="bold cyan")
    tbl.add_column("Tier", style="bold")
    tbl.add_column("Cells", justify="right")
    tbl.add_column("Types", justify="right")
    tbl.add_column("Pct", justify="right")

    for tier_name, data in nav.tier_census().items():
        label = tier_name.replace("O₂†", "O₂†")
        tbl.add_row(
            label,
            f"{data['cells']:,}",
            f"{data['types']:,}",
            f"{data['pct']:.1f}%",
        )
    console.print()
    console.print(tbl)
    console.print()


@crystal_group.command("verify")
@click.argument("n", default=10000, type=int, required=False)
def crystal_verify(n: int):
    """Frobenius codec roundtrip verification on N samples (default 10000).

    Tests decode(encode(addr)) == addr for N random addresses.
    """
    from navigators.crystal_navigator import CrystalNavigator, TOTAL_SIZE, encode_tuple, decode_address
    import random

    console.print(f"\n  Verifying Frobenius codec on {n:,} random addresses …")
    errors = 0
    for _ in range(n):
        addr = random.randint(0, TOTAL_SIZE - 1)
        tup = decode_address(addr)
        recovered = encode_tuple(tup)
        if recovered != addr:
            errors += 1

    color = "green" if errors == 0 else "red"
    mark = _TICK if errors == 0 else _CROSS
    console.print(f"  {mark} [{color}]{n:,} samples — {errors} errors[/{color}]")
    console.print()


@crystal_group.command("encode")
@click.argument("kvs", nargs=-1, metavar="PRIM=VALUE...")
@click.option("--full", is_flag=True, default=False,
              help="Print full 12-primitive tuple alongside address.")
def crystal_encode(kvs, full: bool):
    """Encode a tuple to its canonical address.

    \b
    PRIM=VALUE pairs override the navigator's default tuple for unspecified primitives.
    Missing primitives take navigator defaults (O_∞ self-encoding).

    \b
    Examples:
      imscribe nav crystal encode Phi=⊙ P=P_doublebarpipe
      imscribe nav crystal encode Phi=Phi_softsign P=P_aolig Omega=Omega_closeepsilon D=D_wynn
    """
    from navigators.crystal_navigator import CrystalNavigator, NAVIGATOR_TUPLE, PRIMS

    nav = _load_crystal()
    overrides = dict(kv.split("=", 1) for kv in kvs if "=" in kv)
    tup = {**NAVIGATOR_TUPLE, **overrides}

    addr = nav.encode(tup)
    tier = nav.tier_of(tup)
    cell_id, inner_id, _ = nav.codec_address(tup)
    rt = nav.roundtrip(tup)

    console.print()
    console.print(Panel(
        f"[bold]Address:[/bold]   [cyan]{addr:,}[/cyan]\n"
        f"[bold]Tier:[/bold]      [yellow]{tier}[/yellow]\n"
        f"[bold]Cell:[/bold]      {cell_id}  "
        f"(Φ={tup['Phi']} P={tup['P']} Ω={tup['Omega']} D={tup['D']})\n"
        f"[bold]Inner:[/bold]     {inner_id}\n"
        f"[bold]Roundtrip:[/bold] {_TICK if rt else _CROSS}",
        title="Crystal Encode", expand=False,
    ))

    if full:
        console.print()
        for p in PRIMS:
            console.print(f"  {p:6s}: {tup[p]}")

    console.print()


@crystal_group.command("decode")
@click.argument("address", type=int)
def crystal_decode(address: int):
    """Decode a canonical address to its 12-primitive tuple.

    \b
    Example:
      imscribe nav crystal decode 6734591
    """
    from navigators.crystal_navigator import TOTAL_SIZE, PRIMS

    nav = _load_crystal()

    if not (0 <= address < TOTAL_SIZE):
        console.print(f"[red]Address {address:,} out of range [0, {TOTAL_SIZE-1:,}][/red]")
        raise SystemExit(1)

    tup = nav.decode(address)
    tier = nav.tier_of(tup)

    tbl = Table(
        title=f"Address {address:,}  →  tier {tier}",
        box=box.SIMPLE, header_style="bold",
    )
    tbl.add_column("Primitive")
    tbl.add_column("Value", style="cyan")

    for p in PRIMS:
        tbl.add_row(p, tup[p])

    console.print()
    console.print(tbl)
    console.print()


@crystal_group.command("nearest")
@click.argument("kvs", nargs=-1, metavar="PRIM=VALUE...")
@click.option("-n", default=10, show_default=True, help="Number of results.")
@click.option("--same-tier", is_flag=True, default=False,
              help="Restrict results to the same ouroboricity tier.")
def crystal_nearest(kvs, n: int, same_tier: bool):
    """Nearest catalog entries to a (partial) tuple.

    \b
    PRIM=VALUE pairs override navigator defaults for the query tuple.

    \b
    Examples:
      imscribe nav crystal nearest Phi=⊙ P=P_doublebarpipe -n 5
      imscribe nav crystal nearest D=D_invomega Phi=⊙ --same-tier
    """
    from navigators.crystal_navigator import NAVIGATOR_TUPLE

    nav = _load_crystal()
    overrides = dict(kv.split("=", 1) for kv in kvs if "=" in kv)
    tup = {**NAVIGATOR_TUPLE, **overrides}

    tier = nav.tier_of(tup)
    results = nav.nearest_catalog(tup, n=n, same_tier=same_tier)

    tbl = Table(
        title=f"Nearest catalog entries (query tier: {tier})",
        box=box.ROUNDED, header_style="bold cyan",
    )
    tbl.add_column("Name", style="cyan")
    tbl.add_column("d", justify="right")
    tbl.add_column("Tier", justify="center")

    for r in results:
        tbl.add_row(r["name"], f"{r['distance']:.4f}", r["tier"].replace("O₂†", "O₂†"))

    console.print()
    console.print(tbl)
    console.print()


@crystal_group.command("count")
@click.argument("kvs", nargs=-1, metavar="PRIM=VALUE...")
def crystal_count(kvs):
    """Count types matching a set of primitive constraints.

    \b
    Examples:
      imscribe nav crystal count Phi=⊙ P=P_doublebarpipe
      imscribe nav crystal count Omega=Omega_dzlig
    """
    nav = _load_crystal()
    constraints = dict(kv.split("=", 1) for kv in kvs if "=" in kv)
    n = nav.count(**constraints)

    label = "  ".join(f"{k}={v}" for k, v in constraints.items()) or "(no constraints)"
    console.print(f"\n  [cyan]{n:,}[/cyan] matching types  [{label}]")
    console.print()


@crystal_group.command("query")
@click.option("--phi",   default=None, help="Φ boundary value (e.g. ⊙)")
@click.option("--p",     default=None, help="P boundary value (e.g. P_doublebarpipe)")
@click.option("--omega", default=None, help="Ω boundary value (e.g. Omega_dzlig)")
@click.option("--d",     default=None, help="D boundary value (e.g. D_omega)")
@click.option("--tier",  default=None, help="Tier filter (O_∞ / O₂ / O₂† / O₁ / O₀)")
def crystal_query(phi, p, omega, d, tier):
    """Imscriptive boundary query: (Φ, P, Ω, D) → matching tier cells.

    \b
    The boundary (Φ, P, Ω, D) encodes the bulk — each matching cell contains
    43,200 inner types. Any combination of the four boundary coordinates can be
    specified; omitted coordinates broadcast over all values.

    \b
    Examples:
      imscribe nav crystal query --phi ⊙ --p P_doublebarpipe
      imscribe nav crystal query --tier O_∞
      imscribe nav crystal query --omega Omega_dzlig --d D_omega
    """
    from navigators.crystal_navigator import INNER_SIZE

    nav = _load_crystal()
    cells = nav.imscriptive_query(phi=phi, p=p, omega=omega, d=d, tier=tier)

    total_types = len(cells) * INNER_SIZE

    title = "Boundary query"
    parts = []
    if phi:   parts.append(f"Φ={phi}")
    if p:     parts.append(f"P={p}")
    if omega: parts.append(f"Ω={omega}")
    if d:     parts.append(f"D={d}")
    if tier:  parts.append(f"tier={tier}")
    if parts:
        title += ": " + "  ".join(parts)

    tbl = Table(title=title, box=box.ROUNDED, header_style="bold cyan")
    tbl.add_column("Cell ID", justify="right")
    tbl.add_column("Tier", justify="center")
    tbl.add_column("Φ")
    tbl.add_column("P")
    tbl.add_column("Ω")
    tbl.add_column("D")

    max_rows = 30
    for c in cells[:max_rows]:
        tbl.add_row(
            str(c.cell_id),
            c.tier.replace("O₂†", "O₂†"),
            c.phi, c.p, c.omega, c.d,
        )
    if len(cells) > max_rows:
        tbl.add_row("…", "", "", "", "", f"(+{len(cells)-max_rows} more)")

    console.print()
    console.print(tbl)
    console.print(
        f"  [bold]{len(cells):,}[/bold] matching cells  ·  "
        f"[bold]{total_types:,}[/bold] types"
    )
    console.print()


# =============================================================================
# DOMAIN navigator group
# =============================================================================

@nav_group.group("domain")
def domain_group():
    """Domain navigators: Language · Civilization · Ecology · Consciousness.

    \b
    Sections: §74 (language) · §75 (civilization) · §76 (ecology) · §77 (consciousness)

    \b
    Use --domain DOMAIN to target a single domain; omit for all four.
    Valid domains: language  civilization  ecology  consciousness

    \b
    Subcommands:
      info      Summary table: entries with tier, K, P, Φ (and C-score for consciousness)
      verify    Theorem verification (key §74–§77 predictions)
      distance  Distance breakdown between two entries
      nearest   Nearest catalog entries to a named entry
    """


_DOMAINS = ["language", "civilization", "ecology", "consciousness"]

_domain_option = click.option(
    "--domain", "-d",
    type=click.Choice(_DOMAINS),
    default=None,
    help="Target domain (default: all four).",
)


def _domain_nav(domain: str):
    from navigators.domain_navigators import DomainNavigator, Catalog
    return DomainNavigator(domain, Catalog())


@domain_group.command("info")
@_domain_option
def domain_info(domain):
    """Summary table for one or all domains."""
    targets = [domain] if domain else _DOMAINS
    for d in targets:
        _domain_nav(d).info()


@domain_group.command("verify")
@_domain_option
def domain_verify(domain):
    """Theorem verification for one or all domains."""
    targets = [domain] if domain else _DOMAINS
    for d in targets:
        _domain_nav(d).verify()


@domain_group.command("distance")
@click.argument("name_a")
@click.argument("name_b")
@_domain_option
def domain_distance(name_a: str, name_b: str, domain):
    """Distance breakdown between two catalog entries.

    \b
    If --domain is omitted the first domain that contains NAME_A is used.

    \b
    Example:
      imscribe nav domain distance proto_indo_european sign_language_asl
    """
    from navigators.domain_navigators import DomainNavigator, Catalog, DOMAIN_NAMES

    cat = Catalog()
    if domain is None:
        domain = next(
            (d for d, names in DOMAIN_NAMES.items() if name_a in names),
            _DOMAINS[0],
        )
    _domain_nav(domain).distance(name_a, name_b)


@domain_group.command("nearest")
@click.argument("name")
@click.option("-n", default=5, show_default=True, help="Number of results.")
@_domain_option
def domain_nearest(name: str, n: int, domain):
    """Nearest catalog entries to a named entry.

    \b
    Example:
      imscribe nav domain nearest human_consciousness -n 8 --domain consciousness
    """
    from navigators.domain_navigators import DOMAIN_NAMES

    if domain is None:
        domain = next(
            (d for d, names in DOMAIN_NAMES.items() if name in names),
            _DOMAINS[-1],
        )
    _domain_nav(domain).nearest(name, n=n)


# =============================================================================
# RIEMANN ξ navigator
# =============================================================================

_RIEMANN_GRAMMAR = (
    "D_omega  T_openo  R_downstep  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_broad  Phi_closerevepsilon  H_invscripta  n:m  Omega_crtwo"
)

@nav_group.group("riemann")
def riemann_group():
    """Riemann ξ navigator — functional-equation architecture (§CXLV–§CXLVI).

    \b
    Grammar derivation:
      d(ξ, Lee-Yang) = 0 — structural identity, not analogy.
      ξ(s) = ξ(1-s) earns P_doublebarpipe directly: the reflection δ(s)=1-s
      is involutory, so μ∘δ=id is the Frobenius special condition exactly.

    \b
    Crystal address: 6,734,591 (O_∞, = grammar_self_encode — Cardinality-One Theorem)

    \b
    Architecture mandates (§CXL):
      K_schwa      → SpectralTransformer (global self-attention)
      P_doublebarpipe    → FrobeniusLayer (ξ(s)=ξ(1-s) as identity axiom)
      Omega_crtwo    → parity-protected output head (Z_2 winding)
      ⊙^C     → GUE Wigner-surmise loss (Montgomery conjecture)
    """


@riemann_group.command("describe")
def riemann_describe():
    """Grammar derivation, architecture mandates, and convergence criteria."""
    console.print()
    console.print(Panel(
        "[bold cyan]Riemann ξ Navigator[/bold cyan]  (§CXLV–§CXLVI)\n\n"
        f"[bold]Tuple:[/bold]  {_RIEMANN_GRAMMAR}\n\n"
        "[bold]Crystal address:[/bold]  6,734,591  (O_∞  C=0.830)\n"
        "[bold]Co-type:[/bold]          grammar_self_encode  d=0  (Cardinality-One §CXLII)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  K_schwa      → SpectralTransformer (global self-attention, no cyclic state)\n"
        "  P_doublebarpipe    → FrobeniusLayer (ξ(s)=ξ(1-s) as identity axiom, not constraint)\n"
        "  Omega_crtwo    → parity-protected output (zero-count parity = Z_2 winding)\n"
        "  ⊙^C     → GUE Wigner-surmise loss p(s)=(πs/2)·exp(-πs²/4)\n\n"
        "[bold]O_∞ convergence criteria (P-488):[/bold]\n"
        "  |Δt|_norm < 0.5   — next-zero prediction within half mean spacing\n"
        "  L_frob    < 0.01  — Frobenius roundtrip closed (P_doublebarpipe confirmed)\n"
        "  L_GUE     < 0.05  — spacing distribution matches Wigner surmise",
        title="Riemann ξ Navigator", expand=False,
    ))
    console.print()


@riemann_group.command("train")
@click.option("--epochs",     "-e", default=None, type=int,  help="Number of training epochs.")
@click.option("--batch-size", "-b", default=None, type=int,  help="Batch size.")
@click.option("--zeros",      "-z", default=None, type=int,  help="Number of Riemann zeros to use.")
@click.option("--output",     "-o", default=None, type=str,  help="Model output path.")
def riemann_train(epochs, batch_size, zeros, output):
    """Launch the Riemann ξ navigator training loop.

    Invokes riemann_xi_navigator.py train with any provided flags.
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "riemann_xi_navigator.py"), "train"]
    if epochs:     cmd += ["--epochs",     str(epochs)]
    if batch_size: cmd += ["--batch-size", str(batch_size)]
    if zeros:      cmd += ["--zeros",      str(zeros)]
    if output:     cmd += ["--output",     output]

    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# ZFC transmissibility navigator
# =============================================================================

_ZFC_GRAMMAR = (
    "D_omega  T_openo  R_downstep  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_broad  Phi_closerevepsilon  H_invscripta  n:m  Omega_crtwo"
)

_ZFC_CHANNELS = [
    ("F_hardsign  → F_beltl",      "total loss — identical ZFC token sequence"),
    ("F_beltl   → F_hardsign",     "hallucination — holistic density pulls cls→quantum"),
    ("T_openo  → T_invscr",       "REFL→SEP approximation — partial loss"),
    ("D_omega  → D_invomega",    "LCARD fragment ambiguous with high-rank — partial"),
    ("Gamma_seq → Gamma_and","sequential dep. becomes conjunction — total per step"),
]


@nav_group.group("zfc")
def zfc_group():
    """ZFC transmissibility navigator — grammar-formula roundtrip losses.

    \b
    Core prediction (IUG_NON_TRANSMISSIBILITY §3):
      Non-transmissible primitive values produce a ZFC formula from which
      the original value cannot be recovered. The roundtrip loss for type x
      is bounded below by d(x, T_ZFC) where T_ZFC is the ZFC-realizable subspace.

    \b
    Five collapse channels: F_hardsign, F_beltl, T_openo, D_omega, Gamma_seq.
    """


@zfc_group.command("describe")
def zfc_describe():
    """Grammar derivation, architecture mandates, and transmissibility channels."""
    console.print()

    channels_str = "\n".join(
        f"  {ch:<28} → {reason}"
        for ch, reason in _ZFC_CHANNELS
    )

    console.print(Panel(
        "[bold cyan]ZFC Transmissibility Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_ZFC_GRAMMAR}\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  K_schwa      → 4-layer Transformer encoder (global self-attention)\n"
        "  P_doublebarpipe    → Frobenius roundtrip loss native from epoch 1\n"
        "  R_downstep    → output restructures its own co-domain (ZFC formula space)\n"
        "  G_revapostrophe     → maximize context window (256 tokens)\n"
        "  ⊙^C     → encoder trained at distinguishability boundary\n\n"
        "[bold]Collapse channels (IUG_NON_TRANSMISSIBILITY §3):[/bold]\n"
        + channels_str,
        title="ZFC Transmissibility Navigator", expand=False,
    ))
    console.print()


@zfc_group.command("train")
@click.option("--epochs", "-e", default=None, type=int, help="Number of training epochs.")
def zfc_train(epochs):
    """Train the ZFC encoder (invokes zfc_navigator.py train)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "zfc_navigator.py"), "train"]
    if epochs:
        cmd += ["--epochs", str(epochs)]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@zfc_group.command("probe")
@click.option("--top", "-t", default=20, show_default=True,
              help="Show top-N highest-loss entries.")
@click.option("--iug", is_flag=True, default=False,
              help="Specifically probe IUG and grammar_self_encode entries.")
def zfc_probe(top: int, iug: bool):
    """Run transmissibility probe on the full catalog.

    Invokes zfc_navigator.py probe (or iug) and streams output.
    """
    if iug:
        cmd = ["uv", "run", str(_PROJECT_ROOT / "zfc_navigator.py"), "iug"]
    else:
        cmd = ["uv", "run", str(_PROJECT_ROOT / "zfc_navigator.py"),
               "probe", "--top", str(top)]

    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@zfc_group.command("entry")
@click.argument("name")
@click.option("--model", "-m", default="zfc_encoder.pt", show_default=True,
              help="Trained encoder checkpoint.")
@click.option("--catalog", "-c", default=None,
              help="Catalog file or glob (default: ig_catalog*.json).")
@click.option("--no-model", is_flag=True, default=False,
              help="Skip encoder roundtrip — show ZFC formula only.")
def zfc_entry(name: str, model: str, catalog: str, no_model: bool):
    """Full per-primitive ZFC probe for a named catalog entry.

    Shows the grammar tuple, per-primitive ZFC formula fragments, the assembled
    token sequence, and encoder predicted-vs-input for all 12 primitives.
    Flags every mismatch, not only the 4 monitored collapse channels.

    \b
    Special names (no catalog lookup needed):
      iug        IUG / grammar-self-encoding entry
      grammar    synonym for iug
      zfc        ZFC navigator self-reference

    \b
    Examples:
      imscribe nav zfc entry muon
      imscribe nav zfc entry "Kitaev chain"
      imscribe nav zfc entry iug --no-model
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "zfc_navigator.py"), "entry", name,
           "--model", model]
    if catalog:
        cmd += ["--catalog", catalog]
    if no_model:
        cmd += ["--no-model"]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@zfc_group.command("stats")
@click.option("--catalog", "-c", default=None,
              help="Catalog file or glob (default: ig_catalog*.json).")
def zfc_stats(catalog: str):
    """Formula-length statistics across the catalog.

    Shows token-count distribution, highlights entries with unusually long or
    short ZFC encodings, and reports per-primitive coverage.

    \b
    Example:
      imscribe nav zfc stats
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "zfc_navigator.py"), "stats"]
    if catalog:
        cmd += ["--catalog", catalog]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# AdS/CFT imscriptive duality navigator
# =============================================================================

_ADSCFT_GRAMMAR = (
    "D_omega  T_openo  R_downstep  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_broad  ⊙  H_invscripta  n:m  Omega_dzlig"
)


@nav_group.group("ads_cft")
def adscft_group():
    """AdS/CFT imscriptive duality navigator — bulk/boundary distance, RG flow.

    \b
    Type:
      D_omega T_openo R_downstep P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_broad ⊙ H_invscripta n:m Omega_dzlig

    \b
    Key facts:
      D_omega / T_openo  → imscriptive: boundary encodes bulk (O_∞ tier)
      P_doublebarpipe         → Frobenius: conformal symmetry is explosion-free
      ⊙            → CFT lives precisely at the critical fixed point
      Omega_dzlig          → topological winding protection (integer charge)
      H_invscripta            → conformal group includes unlimited time translation

    \b
    Examples:
      imscribe nav ads_cft describe
      imscribe nav ads_cft probe
      imscribe nav ads_cft bulk-boundary SYM N=4
    """


@adscft_group.command("describe")
def adscft_describe():
    """Grammar derivation, architecture mandates, and imscriptive encoding."""
    console.print()
    console.print(Panel(
        "[bold cyan]AdS/CFT Imscriptive Duality Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_ADSCFT_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O_∞  (P_doublebarpipe + ⊙ → R1)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_omega / T_openo  → imscriptive embedding: boundary encodes bulk\n"
        "  P_doublebarpipe         → FrobeniusLayer: conformal symmetry as identity axiom\n"
        "  R_downstep         → bulk-boundary coupling is adjoint (two-way)\n"
        "  K_schwa           → near-equilibrium RG flow\n"
        "  G_revapostrophe          → maximal scope: all of spacetime\n"
        "  Gamma_broad      → broadcast: entanglement entropy across all scales\n"
        "  H_invscripta            → eternal: conformal group has no temporal boundary\n"
        "  Omega_dzlig          → topological winding: integer-quantized charges\n\n"
        "[bold]Key methods:[/bold]\n"
        "  bulk_boundary_distance   distance between bulk theory and boundary CFT\n"
        "  find_cft_fixed_points    catalog entries co-typed with AdS/CFT boundary\n"
        "  imscriptive_entanglement Ryu-Takayanagi via distance\n"
        "  renormalization_trajectory UV→IR flow as directed distance d_→",
        title="AdS/CFT Navigator", expand=False,
    ))
    console.print()


@adscft_group.command("probe")
def adscft_probe():
    """Run full AdS/CFT analysis (invokes ads_cft_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "ads_cft_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@adscft_group.command("bulk-boundary")
@click.argument("bulk_type")
@click.argument("cft_type")
def adscft_bulk_boundary(bulk_type: str, cft_type: str):
    """Compute distance between a bulk theory and boundary CFT.

    \b
    Example:
      imscribe nav ads_cft bulk-boundary "AdS5_gravity" "N=4_SYM"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "ads_cft_navigator.py"),
           "bulk_boundary", bulk_type, cft_type]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# Mirror symmetry navigator
# =============================================================================

_MIRROR_GRAMMAR = (
    "D_invomega  T_bullseye  R_downstep  P_upsilon  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_broad  ⊙  H_invscripta  n:m  Omega_crtwo"
)


@nav_group.group("mirror")
def mirror_group():
    """Mirror symmetry navigator — Calabi-Yau pairs, A-B model, T-duality tower.

    \b
    Type:
      D_invomega T_bullseye R_downstep P_upsilon F_hardsign K_schwa
      G_revapostrophe Gamma_broad ⊙ H_invscripta n:m Omega_crtwo

    \b
    Key facts:
      D_invomega   → infinite-dimensional moduli space of CY compactifications
      T_bullseye  → A-model ↔ B-model crossing: symplectic meets complex
      P_upsilon     → quantum phase symmetry (complex structure deformation)
      Omega_crtwo  → mirror involution: swaps h^{1,1} ↔ h^{2,1}
      ⊙     → Gepner point sits at the critical self-modeling boundary

    \b
    Examples:
      imscribe nav mirror describe
      imscribe nav mirror probe
      imscribe nav mirror pair "quintic_threefold"
    """


@mirror_group.command("describe")
def mirror_describe():
    """Grammar derivation and A-model/B-model correspondence."""
    console.print()
    console.print(Panel(
        "[bold cyan]Mirror Symmetry Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_MIRROR_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O₂  (⊙ + Omega_crtwo + D_invomega → R5)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_invomega    → infinite-dimensional: full moduli space of CY manifolds\n"
        "  T_bullseye   → dual-lobe crossing: A-model ↔ B-model (symplectic ↔ complex)\n"
        "  P_upsilon      → quantum coherence: complex structure deformation\n"
        "  R_downstep   → adjoint: mirror map is bidirectional\n"
        "  Omega_crtwo   → Z_2 winding: mirror involution swaps Hodge numbers\n"
        "  ⊙      → Gepner point: rational CFT at the CY critical locus\n\n"
        "[bold]Key methods:[/bold]\n"
        "  find_mirror_pair              locate mirror CY in catalog\n"
        "  compute_gromov_witten_invariants  GW counts via A-model\n"
        "  period_integral_map           B-model periods → prepotential\n"
        "  derived_equivalence_check     D^b(CY) ≅ D^b(mirror) via Fourier-Mukai\n"
        "  t_duality_transform           T-duality tower between fiber-dual CYs",
        title="Mirror Symmetry Navigator", expand=False,
    ))
    console.print()


@mirror_group.command("probe")
def mirror_probe():
    """Run full mirror symmetry analysis (invokes mirror_symmetry_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "mirror_symmetry_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@mirror_group.command("pair")
@click.argument("cy_manifold")
def mirror_pair(cy_manifold: str):
    """Find the mirror partner of a named Calabi-Yau manifold.

    \b
    Example:
      imscribe nav mirror pair "quintic_threefold"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "mirror_symmetry_navigator.py"),
           "find_mirror", cy_manifold]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# TQFT navigator
# =============================================================================

_TQFT_GRAMMAR = (
    "D_turnthree  T_bullseye  R_downstep  P_upsilon  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_broad  ⊙  H_turntwo  n:m  Omega_dzlig"
)


@nav_group.group("tqft")
def tqft_group():
    """TQFT navigator — knot invariants, Chern-Simons, modular tensor categories.

    \b
    Type:
      D_turnthree T_bullseye R_downstep P_upsilon F_hardsign K_schwa
      G_revapostrophe Gamma_broad ⊙ H_turntwo n:m Omega_dzlig

    \b
    Key facts:
      D_turnthree  → triangulated state space (simplicial decomposition)
      T_bullseye    → surgery crossing: 3-manifold ↔ knot complement duality
      P_upsilon       → quantum group symmetry (q-deformed at root of unity)
      H_turntwo          → two temporal levels: manifold and boundary
      Omega_dzlig     → integer winding: Chern-Simons level k ∈ Z

    \b
    Examples:
      imscribe nav tqft describe
      imscribe nav tqft probe
      imscribe nav tqft knot trefoil SU2 5
    """


@tqft_group.command("describe")
def tqft_describe():
    """Grammar derivation and state-space functor architecture."""
    console.print()
    console.print(Panel(
        "[bold cyan]TQFT Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_TQFT_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O₂  (⊙ + Omega_dzlig + D_turnthree → R4)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_turnthree  → triangulated: state space via simplicial decomposition\n"
        "  T_bullseye    → surgery crossing: manifold ↔ knot complement\n"
        "  P_upsilon       → quantum group: q-deformed symmetry at root of unity\n"
        "  R_downstep    → adjoint: cutting/gluing is self-dual (Atiyah axioms)\n"
        "  K_schwa      → slow integration: partition function by surgery sequence\n"
        "  H_turntwo          → two-level depth: bulk manifold + boundary surface\n"
        "  Omega_dzlig     → integer winding: Chern-Simons level k ∈ ℤ\n\n"
        "[bold]Key methods:[/bold]\n"
        "  compute_knot_invariant     colored Jones / HOMFLY via Chern-Simons\n"
        "  manifold_surgery           Dehn surgery = tensor product in bordism cat\n"
        "  compute_witten_state       Hilbert space for boundary surface\n"
        "  modular_tensor_category    braided fusion categories from quantum groups\n"
        "  boundary_cft_correspondence  3d TQFT ↔ 2d rational CFT via bulk-boundary",
        title="TQFT Navigator", expand=False,
    ))
    console.print()


@tqft_group.command("probe")
def tqft_probe():
    """Run full TQFT analysis (invokes tqft_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "tqft_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@tqft_group.command("knot")
@click.argument("knot_name")
@click.argument("gauge_group")
@click.argument("level", type=int)
def tqft_knot(knot_name: str, gauge_group: str, level: int):
    """Compute knot invariant via Chern-Simons at given gauge group and level.

    \b
    Example:
      imscribe nav tqft knot trefoil SU2 5
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "tqft_navigator.py"),
           "knot", knot_name, gauge_group, str(level)]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# Category Theory Navigator
# =============================================================================

_CATEGORY_GRAMMAR = (
    "D_omega  T_openo  R_ctz  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_seq  ⊙  H_turntwo  n:m  Omega_dzlig"
)


@nav_group.group("category_theory")
def category_theory_group():
    """Category theory navigator — adjunctions, limits, colimits, topos theory.

    
    Type:
      D_omega T_openo R_ctz P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_seq ⊙ H_turntwo n:m Omega_dzlig

    
    Key facts:
      D_omega / T_openo  → imscriptive: entire category encoded
      R_ctz            → categorical relations (functoriality, natural transformations)
      P_doublebarpipe         → Frobenius interface with categorical uncertainty
      G_revapostrophe          → maximal scope: arbitrary categories
      ⊙            → self-modeling: category of categories
      Omega_dzlig          → integer winding: looping through categorical levels

    
    Examples:
      imscribe nav category_theory describe
      imscribe nav category_theory probe
      imscribe nav category_theory adjunction "fin_set"
      imscribe nav category_theory limit "product"
    """


@category_theory_group.command("describe")
def category_theory_describe():
    """Grammar derivation and categorical architecture."""
    console.print()
    console.print(Panel(
        "[bold cyan]Category Theory Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_CATEGORY_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O_∞  (R_ctz + G_revapostrophe → O_∞ closure)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_omega / T_openo  → imscriptive encoding: object→arrow→2-arrow hierarchy\n"
        "  R_ctz            → categorical relations: functors, natural transformations\n"
        "  P_doublebarpipe         → Frobenius interface: structural uncertainty in categorical statements\n"
        "  G_revapostrophe          → maximal scope: any category C, Set^C, Cat, ...\n"
        "  Gamma_seq        → sequential composition: f∘g in hom-sets\n"
        "  ⊙            → self-modeling: Cat as category of categories\n"
        "  Omega_dzlig          → integer winding: iterating through n-categories\n\n"
        "[bold]Key methods:[/bold]\n"
        "  find_adjunction            detect adjoint pairs F ⊣ G\n"
        "  compute_limit              finite limits: terminal, product, pullback...\n"
        "  compute_colimit            finite colimits: initial, coproduct, pushout...\n"
        "  detect_equivalence         check categorical equivalence between structures\n"
        "  find_topoi                 locate topos-like structures\n"
        "  extract_hom_sets           compute Hom(A,B) structure",
        title="Category Theory Navigator", expand=False,
    ))
    console.print()


@category_theory_group.command("probe")
def category_theory_probe():
    """Run full category theory analysis (invokes category_theory_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "category_theory_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@category_theory_group.command("adjunction")
@click.argument("category")
@click.option("--limit", "-n", default=10, type=int, help="Max adjunctions to report.")
def category_theory_adjunction(category: str, limit: int):
    """Find adjoint pairs in a category.

    
    Example:
      imscribe nav category_theory adjunction "fin_set" -n 5
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "category_theory_navigator.py"),
           "adjunction", category, "--limit", str(limit)]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@category_theory_group.command("limit")
@click.argument("category")
@click.argument("diagram_type")
@click.option("--shape", default="finite", help="Diagram shape: finite, filtered, directed.")
def category_theory_limit(category: str, diagram_type: str, shape: str):
    """Compute limit of a diagram in a category.

    
    Example:
      imscribe nav category_theory limit "fin_set" "product"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "category_theory_navigator.py"),
           "limit", category, diagram_type, "--shape", shape]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@category_theory_group.command("colimit")
@click.argument("category")
@click.argument("diagram_type")
@click.option("--shape", default="finite", help="Diagram shape: finite, filtered, directed.")
def category_theory_colimit(category: str, diagram_type: str, shape: str):
    """Compute colimit of a diagram (dual to limit).

    
    Example:
      imscribe nav category_theory colimit "fin_set" "coproduct"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "category_theory_navigator.py"),
           "colimit", category, diagram_type, "--shape", shape]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# Homotopy Type Theory Navigator
# =============================================================================

_HTT_GRAMMAR = (
    "D_omega  T_openo  R_downstep  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_seq  ⊙  H_invscripta  n:m  Omega_crtwo"
)


@nav_group.group("homotopy_type_theory")
def htt_group():
    """Homotopy type theory navigator — univalence, higher groupoids, univalent foundations.

    
    Type:
      D_omega T_openo R_downstep P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_seq ⊙ H_invscripta n:m Omega_crtwo

    
    Key facts:
      D_omega / T_openo  → imscriptive: types and paths encoded
      R_downstep         → adjoint: univalence (paths ≃ equivalences)
      P_doublebarpipe         → self-dual with uncertainty on higher identities
      H_invscripta            → eternal: paths compose indefinitely
      Omega_crtwo         → binary winding: type equivalence ↔ path equality

    
    Examples:
      imscribe nav homotopy_type_theory describe
      imscribe nav homotopy_type_theory probe
      imscribe nav homotopy_type_theory univalence_check
    """


@htt_group.command("describe")
def htt_describe():
    """Grammar derivation and univalence architecture."""
    console.print()
    console.print(Panel(
        "[bold cyan]Homotopy Type Theory Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_HTT_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O_∞  (univalence axiom → self-embedding)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_omega / T_openo  → imscriptive: full type theory and path spaces\n"
        "  R_downstep         → univalence: paths ↔ equivalences (bidirectional)\n"
        "  P_doublebarpipe         → self-dual: structure-preserving uncertainty\n"
        "  G_revapostrophe          → universe levels: arbitrary universe hierarchies\n"
        "  Gamma_seq        → path concatenation: sequential higher composition\n"
        "  H_invscripta            → eternal: infinite homotopy depth\n"
        "  Omega_crtwo         → binary winding: equivalence ↔ identity\n\n"
        "[bold]Key methods:[/bold]\n"
        "  verify_univalence            check univalence axiom holds\n"
        "  compute_higher_groupoid      π_n for higher types\n"
        "  detect_equivalence           find type equivalences\n"
        "  compute_loop_space           Ω(X, x₀) fundamental group\n"
        "  find_universe_levels         locate universe hierarchies",
        title="Homotopy Type Theory Navigator", expand=False,
    ))
    console.print()


@htt_group.command("probe")
def htt_probe():
    """Run full homotopy type theory analysis (invokes homotopy_type_theory_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "homotopy_type_theory_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@htt_group.command("univalence_check")
@click.argument("type_name")
def htt_univalence_check(type_name: str):
    """Verify univalence axiom for a type.

    
    Example:
      imscribe nav homotopy_type_theory univalence_check "Type_0"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "homotopy_type_theory_navigator.py"),
           "univalence_check", type_name]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))




# =============================================================================
# Algebraic Geometry Navigator
# =============================================================================

_AG_GRAMMAR = (
    "D_omega  T_bullseye  R_downstep  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_seq  ⊙  H_turntwo  n:m  Omega_dzlig"
)


@nav_group.group("algebraic_geometry")
def algebraic_geometry_group():
    """Algebraic geometry navigator — schemes, cohomology, descent, moduli spaces.

    
    Type:
      D_omega T_bullseye R_downstep P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_seq ⊙ H_turntwo n:m Omega_dzlig

    
    Key facts:
      D_omega            → imscriptive: all schemes encoded
      T_bullseye          → local rings ↔ global sections ↔ Spec
      R_downstep          → adjoint: pushforward ↔ pullback
      ⊙             → self-modeling: scheme ↔ category of sheaves
      Omega_dzlig           → integer winding: cohomological dimension

    
    Examples:
      imscribe nav algebraic_geometry describe
      imscribe nav algebraic_geometry probe
      imscribe nav algebraic_geometry compute_cohomology
    """


@algebraic_geometry_group.command("describe")
def algebraic_geometry_describe():
    """Grammar derivation and scheme-theoretic architecture."""
    console.print()
    console.print(Panel(
        "[bold cyan]Algebraic Geometry Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_AG_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O_∞  (scheme ↔ sheaves duality)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_omega            → imscriptive encoding of all schemes and morphisms\n"
        "  T_bullseye          → bowtie topology: local rings ↔ global sections ↔ spectra\n"
        "  R_downstep          → adjoint relations: pushforward/pullback, global/local\n"
        "  P_doublebarpipe          → Frobenius: coherence sheaf uncertainty\n"
        "  F_hardsign            → preserves exact sequences, cohomology, derived structure\n"
        "  K_schwa            → slow traversal through cohomology spectral sequences\n"
        "  G_revapostrophe           → arbitrary dimension and base schemes\n"
        "  Gamma_seq         → sequential composition of morphisms\n"
        "  ⊙             → self-modeling: scheme ≅ category of sheaves\n"
        "  H_turntwo                → two-step: cohomology of cohomology, spectral sequences\n"
        "  Omega_dzlig           → integer winding: cohomological dimension\n\n"
        "[bold]Key methods:[/bold]\n"
        "  compute_dimension          Krull dimension of schemes\n"
        "  compute_cohomology         sheaf cohomology Hⁿ(X,F)\n"
        "  verify_descent             check sheaf descent conditions\n"
        "  compute_intersection_number:: intersection multiplicity\n"
        "  find_moduli_space          locate moduli of schemes\n"
        "  compute_spec               Spec of a ring\n"
        "  verify_grothendieck_topology verify Grothendieck topology axioms",
        title="Algebraic Geometry Navigator", expand=False,
    ))
    console.print()


@algebraic_geometry_group.command("probe")
def algebraic_geometry_probe():
    """Run full algebraic geometry analysis (invokes algebraic_geometry_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "algebraic_geometry_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@algebraic_geometry_group.command("compute_cohomology")
@click.argument("scheme")
@click.argument("sheaf")
def algebraic_geometry_cohomology(scheme: str, sheaf: str):
    """Compute sheaf cohomology of a scheme.

    
    Example:
      imscribe nav algebraic_geometry compute_cohomology "P^2_C" "O(1)"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "algebraic_geometry_navigator.py"),
           "compute_cohomology", scheme, sheaf]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@algebraic_geometry_group.command("dimension")
@click.argument("scheme")
def algebraic_geometry_dimension(scheme: str):
    """Compute Krull dimension of a scheme.

    
    Example:
      imscribe nav algebraic_geometry dimension "Spec_Z"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "algebraic_geometry_navigator.py"),
           "dimension", scheme]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# Quantum Field Theory Navigator
# =============================================================================

_QFT_GRAMMAR = (
    "D_omega  T_commatailz  R_subrightarrow  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_seq  ⊙  H_turntwo  S_ltailm  Omega_dzlig"
)


@nav_group.group("quantum_field_theory")
def quantum_field_theory_group():
    """Quantum field theory navigator — RG flow, fixed points, dualities, anomalies.

    
    Type:
      D_omega T_commatailz R_subrightarrow P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_seq ⊙ H_turntwo S_ltailm Omega_dzlig

    
    Key facts:
      D_omega            → imscriptive: all QFTs encoded
      T_commatailz        → box topology: theory⊗symmetry⊗spacetime
      R_subrightarrow           → supervenience: operators supervene on couplings
      ⊙             → self-modeling: fixed points, conformal manifolds
      H_turntwo                → counterterm → renormalized → physical

    
    Examples:
      imscribe nav quantum_field_theory describe
      imscribe nav quantum_field_theory probe
      imscribe nav quantum_field_theory beta_function
    """


@quantum_field_theory_group.command("describe")
def quantum_field_theory_describe():
    """Grammar derivation and RG flow architecture."""
    console.print()
    console.print(Panel(
        "[bold cyan]Quantum Field Theory Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_QFT_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O_∞  (Wilsonian RG flow → critical points)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_omega            → imscriptive encoding of all QFTs, couplings, operators\n"
        "  T_commatailz        → box topology: theory space ⊗ symmetry group ⊗ spacetime\n"
        "  R_subrightarrow           → supervenience: operators supervene on couplings\n"
        "  P_doublebarpipe          → Frobenius: uncertainty between weak/strong coupling\n"
        "  F_hardsign            → preserves commutation relations, Ward identities\n"
        "  K_schwa            → slow RG flow (logarithmic scale separation)\n"
        "  G_revapostrophe           → arbitrary spacetime dimensions, matter content\n"
        "  Gamma_seq         → sequential RG flow: μ → μ'\n"
        "  ⊙             → self-modeling: fixed points, conformal manifolds\n"
        "  H_turntwo                → two-step: counterterm → renormalized → physical\n"
        "  Omega_dzlig           → integer winding: index, instanton number, Chern-Simons level\n\n"
        "[bold]Key methods:[/bold]\n"
        "  compute_beta_function          RG flow β(g)\n"
        "  find_fixed_point               locate IR/UV fixed points\n"
        "  detect_duality                 identify S-duality, T-duality\n"
        "  compute_anomaly                gauge/gravitational anomalies\n"
        "  classify_phase                 topological/symmetry-protected phases\n"
        "  compute_correlation_function   Green's functions, propagators\n"
        "  verify_Ward_identity           Ward-Takahashi identities",
        title="Quantum Field Theory Navigator", expand=False,
    ))
    console.print()


@quantum_field_theory_group.command("probe")
def quantum_field_theory_probe():
    """Run full QFT analysis (invokes quantum_field_theory_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "quantum_field_theory_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@quantum_field_theory_group.command("beta_function")
@click.argument("qft_name")
def quantum_field_theory_beta_function(qft_name: str):
    """Compute beta function for a quantum field theory.

    
    Example:
      imscribe nav quantum_field_theory beta_function "QCD_Nf3"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "quantum_field_theory_navigator.py"),
           "beta_function", qft_name]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))



# =============================================================================
# Langlands Program Navigator
# =============================================================================

_LANGLANDS_GRAMMAR = (
    "D_omega  T_openo  R_downstep  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_broad  ⊙  H_invscripta  n:m  Omega_dzlig"
)


@nav_group.group("langlands_program")
def langlands_program_group():
    """Langlands program navigator — Galois/automorphic correspondence, L-functions.

    
    Type:
      D_omega T_openo R_downstep P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_broad ⊙ H_invscripta n:m Omega_dzlig

    
    Key facts:
      D_omega / T_openo → imscriptive: Galois reps ↔ automorphic forms
      R_downstep        → adjoint functoriality: base change, lift, descent
      Gamma_broad     → broad correspondence: global-to-global
      ⊙           → self-modeling: Langlands duality
      H_invscripta           → eternal: infinite descent, infinite extensions

    
    Examples:
      imscribe nav langlands_program describe
      imscribe nav langlands_program probe
      imscribe nav langlands_program l_function
    """


@langlands_program_group.command("describe")
def langlands_program_describe():
    """Grammar derivation and automorphic-Galois bridge."""
    console.print()
    console.print(Panel(
        "[bold cyan]Langlands Program Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_LANGLANDS_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O_∞  (Galois↔automorphic bridge)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_omega / T_openo → imscriptive: all number fields, groups, representations\n"
        "  R_downstep        → adjoint functoriality: base change, lift, descent\n"
        "  P_doublebarpipe        → Frobenius: uncertainty between global/local\n"
        "  F_hardsign          → preserves L-function identities, functional equations\n"
        "  K_schwa          → slow exploration through moduli of automorphic reps\n"
        "  G_revapostrophe         → arbitrary number fields, reductive groups\n"
        "  Gamma_broad     → broad correspondence: not sequential, global-to-global\n"
        "  ⊙           → self-modeling: Langlands duality as self-duality of L-group\n"
        "  H_invscripta           → eternal: infinite descent, infinite extensions\n"
        "  Omega_dzlig         → integer winding: motivic weight, conductor, L-function order\n\n"
        "[bold]Key methods:[/bold]\n"
        "  find_galois_match                match Galois rep with automorphic form\n"
        "  find_automorphic_match           match automorphic form with Galois rep\n"
        "  compute_l_function               L(s, π) values for automorphic rep\n"
        "  verify_functoriality             check functorial lift between groups\n"
        "  compute_base_change              base change to larger field\n"
        "  compute_local_factors            local L-factors at primes\n"
        "  verify_tamagawa_number           Tamagawa number = 1\n"
        "  find_endoscopic_transfer         endoscopic transfer between groups",
        title="Langlands Program Navigator", expand=False,
    ))
    console.print()


@langlands_program_group.command("probe")
def langlands_program_probe():
    """Run full Langlands program analysis (invokes langlands_program_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "langlands_program_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@langlands_program_group.command("l_function")
@click.argument("automorphic_rep")
@click.argument("s_value", required=False, default=None)
def langlands_l_function(automorphic_rep: str, s_value: str):
    """Describe L-function for an automorphic rep; optionally evaluate at s.

    Example:
      imscribe nav langlands_program l_function "GL2_newform"
      imscribe nav langlands_program l_function "trivial" 2.0
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "langlands_program_navigator.py"),
           "l_function", automorphic_rep]
    if s_value is not None:
        cmd.append(str(s_value))
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# Representation Theory Navigator
# =============================================================================

_REPTHEORY_GRAMMAR = (
    "D_omega  T_commatailz  R_ctz  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_seq  ⊙  H_turntwo  n:m  Omega_dzlig"
)


@nav_group.group("representation_theory")
def representation_theory_group():
    """Representation theory navigator — characters, tensor decompositions, Lie theory.

    
    Type:
      D_omega T_commatailz R_ctz P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_seq ⊙ H_turntwo n:m Omega_dzlig

    
    Key facts:
      D_omega / T_commatailz → imscriptive: all groups, algebras, representations
      R_ctz                 → categorical: induction↔restriction, tensor product
      ⊙                 → self-modeling: group algebra = representation category
      H_turntwo                    → two-step: tensor with dual, Clebsch-Gordan
      Omega_dzlig               → integer winding: dimension, weight lattice index

    
    Examples:
      imscribe nav representation_theory describe
      imscribe nav representation_theory probe
      imscribe nav representation_theory character
    """


@representation_theory_group.command("describe")
def representation_theory_describe():
    """Grammar derivation and character table architecture."""
    console.print()
    console.print(Panel(
        "[bold cyan]Representation Theory Navigator[/bold cyan]\n\n"
        f"[bold]Tuple:[/bold]  {_REPTHEORY_GRAMMAR}\n\n"
        "[bold]Tier:[/bold]  O_∞  (character table → representation category)\n\n"
        "[bold]Architecture mandates:[/bold]\n"
        "  D_omega / T_commatailz → imscriptive: all groups, algebras, representations\n"
        "  R_ctz               → categorical relations: functors, induction, restriction\n"
        "  P_doublebarpipe            → Frobenius: uncertainty in positive characteristic\n"
        "  F_hardsign              → preserves character orthogonality, Schur orthogonality\n"
        "  K_schwa              → slow traversal through moduli of representations\n"
        "  G_revapostrophe             → arbitrary groups: finite, Lie, algebraic, quantum\n"
        "  Gamma_seq           → sequential: weight lattice, tensor decomposition\n"
        "  ⊙               → self-modeling: group algebra = representation category\n"
        "  H_turntwo                  → two-step: representation ⊗ its dual, Clebsch-Gordan\n"
        "  Omega_dzlig             → integer winding: dimension, weight lattice index\n\n"
        "[bold]Key methods:[/bold]\n"
        "  compute_character            χ(g) = trace(ρ(g)) for group element g\n"
        "  decompose_tensor             decompose R_A ⊗ R_B into irreducibles\n"
        "  induce_character             induce character from subgroup to group\n"
        "  restrict_character           restrict character from group to subgroup\n"
        "  compute_dimensions           dimension formula for reps\n"
        "  find_irreducibles            list all irreducible representations\n"
        "  verify_shur_orthogonality    check character orthogonality relations\n"
        "  compute_clebsch_gordan       CG coefficients for tensor product\n"
        "  match_representations        match reps across different realizations",
        title="Representation Theory Navigator", expand=False,
    ))
    console.print()


@representation_theory_group.command("probe")
def representation_theory_probe():
    """Run full representation theory analysis (invokes representation_theory_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "representation_theory_navigator.py")]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@representation_theory_group.command("character")
@click.argument("group")
@click.argument("representation")
@click.argument("element")
def representation_theory_character(group: str, representation: str, element: str):
    """Compute character table entry χ(g).

    
    Example:
      imscribe nav representation_theory character "S3" "standard" "(12)"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "representation_theory_navigator.py"),
           "character", group, representation, element]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@representation_theory_group.command("tensor_decompose")
@click.argument("group")
@click.argument("rep_a")
@click.argument("rep_b")
def representation_theory_tensor(group: str, rep_a: str, rep_b: str):
    """Decompose tensor product of two representations.

    
    Example:
      imscribe nav representation_theory tensor_decompose "SU3" "fundamental" "fundamental"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "representation_theory_navigator.py"),
           "tensor_decompose", group, rep_a, rep_b]
    console.print(f"\n  [dim]Running:[/dim] {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# End of additions
