"""
Imscribing Grammar CLI — Command-line interface for the Unified Imscriptiveon framework.

Enhanced with AI-powered imscription generation via AjintK framework.
Accessible via `imscrbgrmr` or `imscribe` command.
"""
import asyncio
import json
import sys
from typing import Dict, List, Optional
from pathlib import Path

# Ensure project root is on sys.path so `agents` and `framework` packages are
# importable regardless of the working directory the user invokes `imscribe` from.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree
from rich.markdown import Markdown

from imscrbgrmr import (
    Imscription, Dimensionality, Topology, RecognitionMode,
    Polarity, Fidelity, Granularity, InteractionGrammar,
    KineticCharacter,  # NEW
    TopoIndex,         # ◻ — quantum extension
    global_catalog, parse_notation, ConstraintEngine,
    compute_eta_CP, compute_xi_CP,
    analyze_criticality, find_criticality_candidates,  # NEW
)
from imscrbgrmr.thermodynamics import get_reference, list_references, compare_efficiencies
from imscrbgrmr.criticality import check_axiom5_criticality  # NEW
from imscrbgrmr.lambda_commands import lambda_group  # λ-engine
from imscrbgrmr.navigator_commands import nav_group  # navigators

console = Console()

_IG_CATALOG_LOADED = False

def _load_ig_catalog_into_global():
    """Load IG_catalog.json entries into global_catalog (runs once per process)."""
    global _IG_CATALOG_LOADED
    if _IG_CATALOG_LOADED:
        return
    _IG_CATALOG_LOADED = True
    _ig_path = _PROJECT_ROOT / "IG_catalog.json"
    if not _ig_path.exists():
        return
    from imscrbgrmr.models import Imscription as _Sy
    with open(_ig_path, encoding="utf-8") as _fh:
        _ig_entries = json.load(_fh)
    # Batch mode: suppress per-entry disk saves (save once at the end)
    global_catalog._batch_loading = True
    try:
        for _e in _ig_entries:
            if _e.get("name") in global_catalog._imscriptions:
                continue
            try:
                global_catalog.register(_Sy.from_dict(_e))
            except Exception:
                pass
    finally:
        global_catalog._batch_loading = False
        # No save: IG_catalog.json is the source of truth; live entries are saved
        # only when the user explicitly registers new ones via tool/agent commands.


# =============================================================================
# Main CLI Group (imscrbgrmr)
# =============================================================================

@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="imscrbgrmr")
@click.pass_context
def main(ctx):
    """Imscribing Grammar: universal grammar for any self-organizing system.

    Encodes molecules, physical fields, mythological archetypes, mathematical
    structures, linguistic patterns, social dynamics, and abstract systems as
    12-primitive structural coordinates ⟨D; T; R; P; F; K; G; ∈; ⊙; H; S; ◻⟩.

    Accessible via 'imscrbgrmr' or 'imscribe' command.
    """
    global_catalog.populate_defaults()
    _load_ig_catalog_into_global()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# =============================================================================
# Subcommand: analyze
# =============================================================================

@main.command("menu")
def menu_command():
    """Interactive menu — browse and run commands without remembering syntax."""
    from .menu import run_menu
    run_menu()


@main.command()
@click.argument("identifier")
@click.option("--format", "-f", type=click.Choice(["text", "json", "notation"]), default="text", help="Output format.")
def analyze(identifier: str, format: str):
    """
    Analyze a registered imscription by name or notation string.

    IDENTIFIER is a catalog name (e.g. 'muon', 'ice_Ih', 'סַמָּאֵל') or a
    full notation string ⟨D; T; R; P; F; K; G; ∈; ⊙; H; S; ◻⟩.
    """
    try:
        # Try to get from catalog first
        imscription = global_catalog.get(identifier)
        
        # If not found, try to parse as notation
        if not imscription and identifier.startswith("⟨") and identifier.endswith("⟩"):
            notation = parse_notation(identifier)
            imscription = Imscription(
                name="unnamed_imscription",
                dimensionality=notation.dimensionality,
                topology=notation.topology,
                recognition_mode=notation.recognition_mode,
                polarity=notation.polarity,
                fidelity=notation.fidelity,
                granularity=notation.granularity,
                interaction_grammar=notation.interaction_grammar
            )
        
        if not imscription:
            console.print(f"[red]Error: Imscription '{identifier}' not found in catalog and not a valid notation.[/red]")
            sys.exit(1)
            
        if format == "json":
            console.print_json(imscription.to_json())
        elif format == "notation":
            console.print(imscription.to_notation())
        else:
            # Rich table for analysis
            table = Table(title=f"Imscription Analysis: {imscription.name}")
            table.add_column("Primitive", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_column("Description", style="white")

            table.add_row("Dimensionality", imscription.dimensionality.value, "Operating space")
            table.add_row("Topology", imscription.topology.value, "Influence connectivity")
            table.add_row("Recognition Mode", imscription.recognition_mode.value, "Interaction mechanism")
            table.add_row("Polarity", imscription.polarity.value, "Directional character")
            table.add_row("Fidelity", imscription.fidelity.value, "Information per event")
            table.add_row("Granularity", imscription.granularity.value, "Correlation length")
            _ig = imscription.interaction_grammar
            _ig_value = (
                f"{_ig.operator.value}({_ig.tier})"
                if hasattr(_ig, "operator") and hasattr(_ig, "tier")
                else str(_ig.value)
            )
            table.add_row("Coupling", _ig_value, "Partner selection logic")
            
            console.print(table)
            console.print(Panel(f"[bold]Unified Notation:[/bold] {imscription.to_notation()}"))
            
    except Exception as e:
        console.print(f"[red]Error analyzing imscription: {e}[/red]")
        sys.exit(1)


# =============================================================================
# Subcommand: catalog
# =============================================================================

@main.group()
def catalog():
    """Manage and search the imscription catalog."""
    pass


@catalog.command(name="list")
@click.option("--domain", "-d", help="Filter by domain.")
@click.option("--source", "-s", type=click.Choice(["json", "global"]), default="json",
              help="Catalog source: 'json' = IG_catalog.json (default), 'global' = in-memory global_catalog.")
@click.option("--limit", "-n", default=50, show_default=True, help="Max entries to display (0 = all).")
@click.option("--offset", default=0, show_default=True, help="Start at this entry index.")
@click.option("--filter", "name_filter", default="", help="Show only names containing this string.")
def list_imscriptions(domain: Optional[str], source: str, limit: int, offset: int, name_filter: str):
    """List registered imscriptions (default: first 50).

    By default reads from IG_catalog.json (the single source of truth).
    Use --source global to list the legacy in-memory global_catalog instead.
    Use -n 0 to show all entries (slow for large catalogs).
    """
    PRIM_ORDER = ["⊢", "⊣", "≻", "≺", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]

    if source == "json" and not domain:
        # ── Primary path: merge IG_catalog.json + ~/.imscrbgrmr/catalog.json ──
        json_path = _PROJECT_ROOT / "IG_catalog.json"
        if not json_path.exists():
            console.print(f"[red]IG_catalog.json not found at {json_path}[/red]")
            return
        with open(json_path, "r", encoding="utf-8") as f:
            entries = json.load(f)

        # No second store. This used to merge ~/.imscrbgrmr/catalog.json, which
        # made `list` see a strictly larger namespace than every other command:
        # an entry the crawler had written showed in the table, could be read off
        # the screen, and could not be stripped, restored or compared, because
        # the ixcription commands read the canonical catalog alone. Those 41
        # entries are merged into IG_catalog.json; the crawler's file is a cache
        # to be folded in, never a source `list` reads behind the tools' backs.

        total = len(entries)
        if name_filter:
            entries = [e for e in entries if name_filter.lower() in e.get("name", "").lower()]
        entries = entries[offset:]
        if limit > 0:
            page = entries[:limit]
        else:
            page = entries

        showing = f"{offset + 1}–{offset + len(page)} of {total}"
        if name_filter:
            showing += f" (filter: '{name_filter}')"
        table = Table(title=f"Imscriptions — {showing}")
        table.add_column("Name", style="cyan")
        table.add_column("Tuple", style="magenta")
        table.add_column("D", style="green")

        for entry in page:
            name = entry.get("name", "?")
            d_val = entry.get("⊢", "?")
            vals = [entry.get(p, "?") for p in PRIM_ORDER]
            notation = "⟨" + "".join(vals) + "⟩"
            table.add_row(name, notation, d_val)

        console.print(table)
        if limit > 0 and len(entries) > limit:
            console.print(f"[dim]Showing {len(page)} of {total} total. Use --offset {offset+limit} for next page, or -n 0 for all.[/dim]")
        else:
            console.print(f"[bold]{total}[/bold] imscriptions total.")

    elif domain:
        imscriptions = global_catalog.search_by_domain(domain)
        title = f"Registered imscriptions (Domain: {domain})"
        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Notation", style="magenta")
        table.add_column("Dimensionality", style="green")
        for s in imscriptions:
            table.add_row(s.name, s.to_notation(), s.dimensionality.name)
        console.print(table)
        console.print(f"[bold]{len(imscriptions)}[/bold] imscriptions found.")

    else:
        # source == "global"
        imscriptions = list(global_catalog._imscriptions.values())
        title = "Registered imscriptions — global_catalog (in-memory)"
        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Notation", style="magenta")
        table.add_column("Dimensionality", style="green")
        for s in imscriptions:
            table.add_row(s.name, s.to_notation(), s.dimensionality.name)
        console.print(table)
        console.print(f"[bold]{len(imscriptions)}[/bold] imscriptions found.")


@catalog.command(name="auto-stoichiometry")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show assignments without writing to catalog.")
@click.option("--limit", type=int, default=500,
              help="Max entries to process (default: 500, ordered by alphabetical name).")
def auto_stoichiometry(dry_run: bool, limit: int):
    """
    Backfill stoichiometry on T⋈ entries that have none assigned (Phase 3.2).

    Heuristic:
    - T⋈ + P± (sym or ψ) + no S → assign S="1:1"
    - T⋈ + no P± + no S         → flag for manual assignment
    - All others                 → skip

    Processes up to --limit highest-use (alphabetical proxy) entries first.

    \b
    Examples:
        imscribe catalog auto-stoichiometry --dry-run
        imscribe catalog auto-stoichiometry --limit 500
    """
    from imscrbgrmr.models import Topology, Polarity

    SELF_COMP_POLARITY = {
        Polarity.or_,
        Polarity.yew,
    }

    candidates = [
        s for s in global_catalog._imscriptions.values()
        if s.topology == Topology.mime and not s.stoichiometry
    ]
    # Alphabetical ordering as proxy for insertion order / usage
    candidates.sort(key=lambda s: s.name)
    targets = candidates[:limit]

    assigned: List = []
    flagged_manual: List = []

    for s in targets:
        if s.polarity in SELF_COMP_POLARITY:
            assigned.append(s.name)
            if not dry_run:
                s.stoichiometry = "𐑙"
        else:
            flagged_manual.append(s.name)

    # Summary table
    table = Table(title=f"Auto-Stoichiometry {'(dry-run)' if dry_run else ''}")
    table.add_column("Action", style="cyan")
    table.add_column("Count", justify="right")
    table.add_row("Assign S='1:1' (P± present)", str(len(assigned)))
    table.add_row("Flag for manual review (no P±)", str(len(flagged_manual)))
    table.add_row("Total T⋈ missing S (full catalog)", str(len(candidates)))
    console.print(table)

    if dry_run:
        console.print(
            f"\n[dim](dry-run) Would assign '1:1' to {len(assigned)} entries. "
            f"Run without --dry-run to apply.[/dim]"
        )
        return

    if assigned:
        saved = global_catalog.save_catalog()
        save_msg = "saved to disk" if saved else "(in-memory only — no storage path)"
        console.print(
            f"\n[green]✓ Assigned S='1:1' to {len(assigned)} entries. {save_msg}[/green]"
        )
    if flagged_manual:
        pct_missing = len(candidates) / max(1, sum(
            1 for s in global_catalog._imscriptions.values()
            if s.topology == Topology.mime
        )) * 100
        console.print(
            f"[yellow]⚑ {len(flagged_manual)} entries require manual stoichiometry assignment "
            f"(no P± present). Missing S on cyclic: {pct_missing:.1f}% of T⋈ entries.[/yellow]"
        )


@catalog.command(name="repair")
@click.option("--topology", "fix_topology", is_flag=True, default=False,
              help="Reclassify T_⋈ entries whose name/description indicate cage/capsule → T_□□.")
@click.option("--purge-junk", is_flag=True, default=False,
              help="Remove clearly junk entries (adversarial test names, speculative placeholders).")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show proposed changes without writing to catalog.")
@click.option("--limit", type=int, default=0,
              help="Max entries to process per repair type (0 = unlimited).")
def repair_catalog(fix_topology: bool, purge_junk: bool, dry_run: bool, limit: int):
    """
    Batch-repair systematic misassignments in the catalog.

    --topology  Converts T_⋈ → T_□□ for any entry whose name or description
                contains cage/capsule/cucurbit/cryptand/cavitand/carceplex keywords.
                These were misassigned by agents that defaulted to T_⋈ for encapsulation
                systems; Axiom 7 (Pass 2) correctly flags them because T_⋈ requires a
                named closing BOND, but cages require a closing FACE (T_□□).

    --purge-junk  Removes entries whose names match known adversarial/placeholder
                  patterns (Quantum-Chronos-*, Q-Rad-*, etc.).

    \b
    Examples:
        imscribe catalog repair --topology --dry-run
        imscribe catalog repair --topology
        imscribe catalog repair --purge-junk --dry-run
        imscribe catalog repair --topology --purge-junk
    """
    from imscrbgrmr.models import Topology

    if not fix_topology and not purge_junk:
        console.print("[yellow]⚠ No repair type specified. Use --topology and/or --purge-junk.[/yellow]")
        console.print("[dim]Run `imscribe catalog repair --help` for options.[/dim]")
        return

    # -------------------------------------------------------------------------
    # Cage keyword sets
    # -------------------------------------------------------------------------
    CAGE_NAME_KEYWORDS = [
        "cage", "capsule", "cucurbit", "cryptand",
        "carceplex", "carcerand", "hemicarceplex", "prism", "barrel",
        "cagomer",
    ]
    # These host families are inherently cage-topology
    CAGE_HOST_KEYWORDS = [
        "cb[", "cb7", "cb[7]", "cb6", "cb[6]", "cb8", "cb[8]",
        "cucurbit[", "cyclodextrin",
    ]

    # These host families are inherently bowl-topology (T_∪)
    # Open concave cavity: single portal, guest exchanges freely
    BOWL_NAME_KEYWORDS = [
        "calix", "calixarene", "calixpyrrole", "calixpyridine",
        "resorcinarene", "resorcarene", "cavitand",
        "cyclotriveratrylene", "ctv", "corannulene",
        "hemicarceplex", "hemicarcerand", "half-cage",
        "pillar[", "pillarene",
        "deep-cavity", "bowl",
    ]
    BOWL_DESC_KEYWORDS = [
        "cone conformation", "upper rim", "lower rim",
        "open portal", "anion-π", "anion-pi",
    ]

    # -------------------------------------------------------------------------
    # Junk name patterns (adversarial / placeholder entries) — case-insensitive
    # -------------------------------------------------------------------------
    JUNK_PATTERNS = [
        "quantum-chronos", "q-rad", "radical-chronosequential",
        "nitroso-aryl-biodagger", "quantum-photoredox-chrono",
        "speculative_quantum_imscription", "speculative quantum imscription",
        "cumulene-α,ω-rigid-rod", "extended-allene-axial-linker",
        "orthogonal-axial [d2d] allene",
        "cumulene-α", "extended-allene", "axial-linker",
        "time crystal imscription", "chronos-recurrer",
        "photoredox-chrono", "chronosequential",
    ]

    topology_fixed: List[str] = []
    topology_bowl: List[str] = []
    topology_net_hex: List[str] = []
    topology_net_mixed: List[str] = []
    topology_net_interp: List[str] = []
    topology_net_sym: List[str] = []
    topology_skipped_no_closing: List[str] = []
    purged: List[str] = []

    all_imscriptions = list(global_catalog._imscriptions.values())

    # -------------------------------------------------------------------------
    # --topology repair
    # -------------------------------------------------------------------------
    if fix_topology:
        bowtie_entries = [s for s in all_imscriptions if s.topology == Topology.mime]
        if limit:
            bowtie_entries = bowtie_entries[:limit]

        for s in bowtie_entries:
            name_lower = s.name.lower()
            desc_lower = (s.description or "").lower()
            combined = name_lower + " " + desc_lower

            is_cage = (
                any(kw in combined for kw in CAGE_NAME_KEYWORDS)
                or any(kw in combined for kw in CAGE_HOST_KEYWORDS)
            )

            if is_cage:
                topology_fixed.append(s.name)
                if not dry_run:
                    s.topology = Topology.oil
            else:
                # Check for bowl topology (T_∪): open concave cavity, single portal
                is_bowl = (
                    any(kw in combined for kw in BOWL_NAME_KEYWORDS)
                    or any(kw in combined for kw in BOWL_DESC_KEYWORDS)
                )
                if is_bowl:
                    topology_bowl.append(s.name)
                    if not dry_run:
                        s.topology = Topology.eat
                else:
                    # Check if the T_⋈ entry has ANY closing indicator (legitimate)
                    from imscrbgrmr.constraints import AXIOM_7_CLOSING_INDICATORS
                    reasoning = (
                        (s.grounding or {}).get("reasoning", "")
                        + " " + (s.description or "")
                    ).lower()
                    has_closing = any(kw in reasoning for kw in AXIOM_7_CLOSING_INDICATORS)
                    if not has_closing:
                        topology_skipped_no_closing.append(s.name)

        table = Table(title=f"Topology Repair {'(dry-run)' if dry_run else ''}")
        table.add_column("Action", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_row("T_⋈ → T_□□ (cage/capsule name detected)", str(len(topology_fixed)))
        table.add_row("T_⋈ → T_∪  (bowl/cavity name detected)", str(len(topology_bowl)))
        table.add_row("T_⋈ kept — no closing bond AND no cage/bowl keyword (manual review needed)",
                      str(len(topology_skipped_no_closing)))
        table.add_row("Total T_⋈ entries scanned", str(len(bowtie_entries)))
        console.print(table)

        if (topology_fixed or topology_bowl) and not dry_run:
            saved = global_catalog.save_catalog()
            save_msg = "saved to disk" if saved else "(in-memory only)"
            console.print(f"\n[green]✓ Reclassified {len(topology_fixed)} entries T_⋈ → T_□□"
                          f" and {len(topology_bowl)} entries T_⋈ → T_∪. {save_msg}[/green]")
        elif dry_run and (topology_fixed or topology_bowl):
            console.print(f"\n[dim](dry-run) Would reclassify {len(topology_fixed)} → T_□□"
                          f" and {len(topology_bowl)} → T_∪. "
                          f"Run without --dry-run to apply.[/dim]")

        if topology_skipped_no_closing:
            console.print(
                f"\n[yellow]⚑ {len(topology_skipped_no_closing)} T_⋈ entries have neither a cage keyword "
                f"nor a named closing bond — these require manual topology review.[/yellow]"
            )
            console.print("[dim]  Run `imscribe audit --pass 2` to see full details.[/dim]")

    # -------------------------------------------------------------------------
    # T_∈ sub-label upgrade (runs as part of --topology)
    # -------------------------------------------------------------------------
    if fix_topology:
        from imscrbgrmr.constraints import (
            NETWORK_HEX_KEYWORDS, NETWORK_MIXED_KEYWORDS,
            NETWORK_INTERPENETRATING_KEYWORDS, NETWORK_SYM_KEYWORDS,
        )
        net_entries = [s for s in all_imscriptions if s.topology == Topology.judge]
        for s in net_entries:
            combined = (s.name + " " + (s.description or "")).lower()
            if any(kw in combined for kw in NETWORK_SYM_KEYWORDS):
                topology_net_sym.append(s.name)
                if not dry_run:
                    s.topology = Topology.judge
            elif any(kw in combined for kw in NETWORK_INTERPENETRATING_KEYWORDS):
                topology_net_interp.append(s.name)
                if not dry_run:
                    s.topology = Topology.judge
            elif any(kw in combined for kw in NETWORK_HEX_KEYWORDS):
                topology_net_hex.append(s.name)
                if not dry_run:
                    s.topology = Topology.judge
            elif any(kw in combined for kw in NETWORK_MIXED_KEYWORDS):
                topology_net_mixed.append(s.name)
                if not dry_run:
                    s.topology = Topology.judge

        net_upgraded = len(topology_net_hex) + len(topology_net_mixed) + len(topology_net_interp) + len(topology_net_sym)
        if net_upgraded:
            net_table = Table(title=f"T_∈ Sub-label Upgrade {'(dry-run)' if dry_run else ''}")
            net_table.add_column("Sub-label", style="cyan")
            net_table.add_column("Count", justify="right", style="magenta")
            net_table.add_row("T_∈ → T_∈(hex)   (hexagonal ring network)", str(len(topology_net_hex)))
            net_table.add_row("T_∈ → T_∈(mixed) (mixed ring sizes)", str(len(topology_net_mixed)))
            net_table.add_row("T_∈ → T_∈(×2)   (interpenetrating)", str(len(topology_net_interp)))
            net_table.add_row("T_∈ → T_∈(sym)   (centrosymmetric bonding)", str(len(topology_net_sym)))
            net_table.add_row("T_∈ unchanged (generic)", str(len(net_entries) - net_upgraded))
            net_table.add_row("Total T_∈ scanned", str(len(net_entries)))
            console.print(net_table)
            if not dry_run:
                global_catalog.save_catalog()
                console.print(f"\n[green]✓ Upgraded {net_upgraded} T_∈ entries with ring-topology sub-labels.[/green]")
            else:
                console.print(f"\n[dim](dry-run) Would upgrade {net_upgraded} T_∈ entries.[/dim]")

    # -------------------------------------------------------------------------
    # --purge-junk
    # -------------------------------------------------------------------------
    if purge_junk:
        for s in all_imscriptions:
            name_lower = s.name.lower()
            if any(pat in name_lower for pat in JUNK_PATTERNS):
                purged.append(s.name)
                if not dry_run:
                    del global_catalog._imscriptions[s.name]

        table2 = Table(title=f"Junk Purge {'(dry-run)' if dry_run else ''}")
        table2.add_column("Entry", style="red")
        for name in purged[:40]:
            table2.add_row(name)
        if len(purged) > 40:
            table2.add_row(f"... and {len(purged) - 40} more")
        console.print(table2)

        if purged and not dry_run:
            saved = global_catalog.save_catalog()
            save_msg = "saved to disk" if saved else "(in-memory only)"
            console.print(f"\n[red]✗ Purged {len(purged)} junk entries. {save_msg}[/red]")
        elif dry_run:
            console.print(f"\n[dim](dry-run) Would purge {len(purged)} entries.[/dim]")


@catalog.command(name="search")
@click.option("--fidelity", "-f", type=click.Choice(["HIGH", "MEDIUM", "LOW"]), help="Filter by fidelity.")
@click.option("--topology", "-t", help="Filter by topology symbol (e.g., T_bullseye).")
def search_imscriptions(fidelity: Optional[str], topology: Optional[str]):
    """Search for imscriptions by primitives."""
    query = {}
    if fidelity:
        query["fidelity"] = Fidelity[fidelity]
    if topology:
        query["topology"] = Topology.from_symbol(topology)
        
    results = global_catalog.search(**query)
    
    table = Table(title="Search Results")
    table.add_column("Name", style="cyan")
    table.add_column("Notation", style="magenta")
    
    for s in results:
        table.add_row(s.name, s.to_notation())
        
    console.print(table)
    console.print(f"[bold]{len(results)}[/bold] imscriptions matched criteria.")


# =============================================================================
# Subcommand: catalog delete
# =============================================================================

@catalog.command(name="delete")
@click.argument("names", nargs=-1, required=True)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def delete_imscriptions(names: tuple, yes: bool):
    """Delete one or more imscriptions from IG_catalog.json by name."""
    catalog_path = _PROJECT_ROOT / "IG_catalog.json"
    if not catalog_path.exists():
        console.print("[red]IG_catalog.json not found.[/red]")
        raise SystemExit(1)

    with open(catalog_path, "r", encoding="utf-8") as f:
        entries: list = json.load(f)

    disk: Dict[str, Dict] = {e["name"]: e for e in entries if "name" in e}

    found = [n for n in names if n in disk]
    missing = [n for n in names if n not in disk]

    if missing:
        for n in missing:
            console.print(f"[yellow]Not found in catalog: '{n}'[/yellow]")

    if not found:
        console.print("[red]No matching entries to delete.[/red]")
        raise SystemExit(1)

    console.print(f"[bold]Will delete:[/bold] {', '.join(found)}")
    if not yes:
        click.confirm("Proceed?", abort=True)

    for n in found:
        del disk[n]
        global_catalog.remove(n)

    try:
        from .registry import write_canonical_catalog
        write_canonical_catalog(disk, catalog_path)
        for n in found:
            console.print(f"[green]✓ Deleted '{n}' from IG_catalog.json[/green]")
    except OSError as e:
        console.print(f"[red]Failed to write IG_catalog.json: {e}[/red]")
        raise SystemExit(1)


# =============================================================================
# Subcommand group: ixcription  — the outward form, on and off the address
# =============================================================================

def _ixc_catalog_path() -> Path:
    """The canonical catalog, or whatever IG_CATALOG points at.

    The override exists so a round of stripping and re-ixcribing can be
    rehearsed on a copy. Only the canonical path propagates to the consumer
    repositories, so a copy stays a copy.
    """
    import os
    p = Path(os.environ.get("IG_CATALOG") or (_PROJECT_ROOT / "IG_catalog.json"))
    if not p.exists():
        console.print(f"[red]Catalog not found: {p}[/red]")
        raise SystemExit(1)
    return p


def _ixc_load(path: Path) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ixc_write(entries: list, path: Path) -> None:
    from .registry import write_canonical_catalog
    try:
        write_canonical_catalog(entries, path)
    except OSError as e:
        console.print(f"[red]Failed to write IG_catalog.json: {e}[/red]")
        raise SystemExit(1)


@main.group("ixcription")
def ixcription_group():
    """The outward form of an entry: put it on, take it off, compare rounds.

    \b
    An entry carries an address, twelve glyphs, and an ixcription, the name and
    description written over it. Every operation in the framework reads the
    address; nothing reads the words except as a handle. So the words come off
    without the tuple moving and without the entry leaving the catalog.

    \b
    A stripped entry is called by its own address. What came off is kept in
    IG_catalog.ixcriptions.json, so a strip is reversible and a second round of
    ixcription over the same address can be set against the first.

    \b
    Names are handles the rest of the constellation may hold. Stripping one
    breaks any reference to it by name until the address is ixcribed again.

    \b
    Acts on IG_catalog.json, or on IG_CATALOG when that is set, so a round can
    be rehearsed on a copy. Writing the canonical catalog propagates it to the
    consumer repositories; writing a copy does not.
    """
    pass


@ixcription_group.command("strip")
@click.argument("names", nargs=-1, required=True)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def ixcription_strip(names: tuple, yes: bool):
    """Take the outward form off NAMES, leaving each address in the catalog.

    \b
    Examples:
        imscribe ixcription strip misnamed_entry
        imscribe ixcription strip kp1_secp256k1 kp2_secp256k1 --yes
    """
    from . import ixcription as ixc

    path = _ixc_catalog_path()
    entries = _ixc_load(path)
    sidecar = ixc.load_sidecar(path)

    known = {e.get("name") for e in entries if isinstance(e, dict)}
    missing = [n for n in names if n not in known]
    found = [n for n in names if n in known]
    for n in missing:
        console.print(f"[yellow]Not found in catalog: '{n}'[/yellow]")
    if not found:
        console.print("[red]Nothing to strip.[/red]")
        raise SystemExit(1)

    if not yes:
        console.print(f"[bold]Will strip the outward form from:[/bold] {', '.join(found)}")
        console.print("[dim]The addresses stay in the catalog and do not move.[/dim]")
        click.confirm("Proceed?", abort=True)

    entries, stripped, _ = ixc.strip(entries, found, sidecar)
    if not stripped:
        console.print("[yellow]Every named entry was already bare.[/yellow]")
        return

    ixc.save_sidecar(sidecar, path)
    _ixc_write(entries, path)

    table = Table(title=f"Stripped {len(stripped)} ixcription(s)")
    table.add_column("Was", style="yellow")
    table.add_column("Now addressed as", style="cyan")
    for old, handle in stripped:
        table.add_row(old, handle)
    console.print(table)
    console.print(f"[dim]Kept in {ixc.sidecar_path(path).name}. "
                  f"Catalog still holds {len(entries)} entries.[/dim]")


@ixcription_group.command("list")
@click.option("--limit", "-n", default=50, show_default=True, help="Max rows (0 = all).")
def ixcription_list(limit: int):
    """List the entries currently standing bare, by address."""
    from . import ixcription as ixc

    path = _ixc_catalog_path()
    entries = _ixc_load(path)
    sidecar = ixc.load_sidecar(path)
    bare = ixc.bare_entries(entries)

    if not bare:
        console.print("No bare entries. Every address in the catalog carries an ixcription.")
        return

    rows = bare if limit <= 0 else bare[:limit]
    table = Table(title=f"Bare addresses — {len(rows)} of {len(bare)}")
    table.add_column("Address", style="cyan")
    table.add_column("Rounds", justify="right")
    table.add_column("Last name it held", style="yellow")
    for e in rows:
        handle = e.get("name", "")
        rs = ixc.rounds(sidecar, handle)
        table.add_row(handle, str(len(rs)), rs[-1].get("name", "") if rs else "")
    console.print(table)


@ixcription_group.command("restore")
@click.argument("handles", nargs=-1, required=True)
@click.option("--round", "round_no", type=int, default=0,
              help="Which round to restore, counting from 1. Default is the most recent.")
def ixcription_restore(handles: tuple, round_no: int):
    """Put a stripped outward form back on the address it came off."""
    from . import ixcription as ixc

    path = _ixc_catalog_path()
    entries = _ixc_load(path)
    sidecar = ixc.load_sidecar(path)

    index = -1 if round_no <= 0 else round_no - 1
    entries, restored, unresolved = ixc.restore(entries, handles, sidecar, index)

    for h in unresolved:
        console.print(f"[yellow]Nothing to restore for '{h}'[/yellow]")
    if not restored:
        console.print("[red]Nothing restored.[/red]")
        raise SystemExit(1)

    _ixc_write(entries, path)
    for handle, name in restored:
        console.print(f"[green]✓ {handle}[/green] → {name}")


@ixcription_group.command("set")
@click.argument("handle")
@click.argument("name")
@click.option("--description", "-d", default="", help="The description for this round.")
@click.option("--justification", "-j", default="", help="Optional justification.")
def ixcription_set(handle: str, name: str, description: str, justification: str):
    """Write a fresh round of ixcription onto a bare address.

    \b
    The address is not touched, only the words over it, so a later comparison
    is between two namings of one address rather than between two entries.
    """
    from . import ixcription as ixc

    path = _ixc_catalog_path()
    entries = _ixc_load(path)

    clash = next((e for e in entries if isinstance(e, dict) and e.get("name") == name), None)
    if clash is not None:
        console.print(f"[red]'{name}' already names an entry in the catalog.[/red]")
        raise SystemExit(1)

    entry = ixc.set_ixcription(entries, handle, name, description, justification)
    if entry is None:
        console.print(f"[red]No entry addressed '{handle}'.[/red]")
        raise SystemExit(1)

    _ixc_write(entries, path)
    console.print(f"[green]✓ {handle}[/green] → {name}")
    console.print("[dim]Strip it again to record this round for comparison.[/dim]")


@ixcription_group.command("compare")
@click.argument("handles", nargs=-1)
def ixcription_compare(handles: tuple):
    """Set the rounds of ixcription over an address against each other.

    \b
    With no arguments, reports every address that has been ixcribed more than
    once. Agreement means each round chose the same name for the same address.
    """
    from . import ixcription as ixc

    path = _ixc_catalog_path()
    sidecar = ixc.load_sidecar(path)

    keys = list(handles) if handles else [h for h in sidecar if len(sidecar[h]) > 1]
    if not keys:
        console.print("No address has been ixcribed more than once yet.")
        return

    for handle in keys:
        rs = ixc.rounds(sidecar, handle)
        if not rs:
            console.print(f"[yellow]Nothing recorded for '{handle}'[/yellow]")
            continue
        agreed = ixc.agreement(sidecar, handle)
        mark = {True: "[green]agrees[/green]", False: "[red]differs[/red]",
                None: "[dim]one round only[/dim]"}[agreed]
        table = Table(title=f"{handle}  —  {len(rs)} round(s), {mark}")
        table.add_column("#", justify="right")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Stripped", style="dim")
        for i, r in enumerate(rs, 1):
            table.add_row(str(i), r.get("name", ""), r.get("description", ""),
                          r.get("stripped", ""))
        console.print(table)


# =============================================================================
# JSON-catalog conflict-resolution helper
# =============================================================================

_PRIM_ATTR = {
    "⊢": lambda s: s.dimensionality.value,
    "⊣": lambda s: s.topology.value,
    "≻": lambda s: s.recognition_mode.value,
    "≺": lambda s: s.polarity.value,
    "⋈": lambda s: s.fidelity.value,
    "⊤": lambda s: s.kinetic_character.value,
    "∈": lambda s: s.granularity.value,
    "∋": lambda s: s.grammar.value,
    "⊙": lambda s: s.criticality_phase.value,
    "⊥": lambda s: s.chirality.value,
    "⊞": lambda s: s.stoichiometry.value,
    "◻": lambda s: s.protection.value,
}
_PRIMITIVE_ORDER = ["⊢", "⊣", "≻", "≺", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]


def _imscription_to_tuple(imscription) -> Dict[str, str]:
    return {p: _PRIM_ATTR[p](imscription) for p in _PRIMITIVE_ORDER}


def _agent_resolve_conflict(
    name: str,
    description: str,
    existing: Dict[str, str],
    proposed: Dict[str, str],
    differing: List[str],
    model: str = "",
    existing_description: str = "",
) -> None:
    """Spawn a TrueAgenticAgent session to reason through and resolve a tuple conflict."""
    import os as _os
    import sys as _sys

    # Ensure project root is importable (CLI may be invoked from any CWD)
    if str(_PROJECT_ROOT) not in _sys.path:
        _sys.path.insert(0, str(_PROJECT_ROOT))

    from agents.true_agentic_agent import TrueAgenticAgent

    existing_str = "⟨" + "".join(existing[p] for p in _PRIMITIVE_ORDER) + "⟩"
    proposed_str = "⟨" + "".join(proposed[p] for p in _PRIMITIVE_ORDER) + "⟩"
    prim_list    = ", ".join(differing)

    task = f"""\
CONFLICT RESOLUTION — imscribe '{name}' in IG_catalog.json

Existing encoding: {existing_str}
Proposed encoding: {proposed_str}
Differing primitives: [{prim_list}]

Both tuples are proposals. Neither carries precedence: age is not evidence and recency
is not evidence. The Grammar speaks one structural verdict — for each differing
primitive there is one structurally correct value; find it.

Your task:
1. Call lookup_catalog(keyword='{name}') to read the existing entry and its description.
2. For each differing primitive ({prim_list}), reason from first principles — which value
   is structurally correct and why? Cite the grammar definitions explicitly. Judge every
   axis on structural grounds alone. If the evidence genuinely cannot decide an axis,
   say so in the justification and keep the value whose stated reasoning is stronger.
3. Call imscribe_system with ALL 12 primitives and a convergence_justification covering
   every differing primitive. Write the description that records the reasoning behind
   the tuple you commit. The tool will not commit without convergence_justification.
4. Call done() with a one-paragraph summary of the resolution.

Existing description, for reference:
"{existing_description or description}"
"""

    model = model or _os.environ.get("IG_MODEL") or _os.environ.get("IG_AGENT_MODEL", "")
    if not model:
        raise click.UsageError(
            "No model for conflict-resolution agent. "
            "Set IG_AGENT_MODEL or ensure --model/IG_MODEL is set."
        )
    console.print(f"[cyan]Conflict-resolution agent ({model}) — resolving '{name}'...[/cyan]\n")

    agent = TrueAgenticAgent(model=model, max_windings=40, verbose=True)
    result = agent.run_sync(task)
    console.print(f"\n[dim]{result}[/dim]")


def _register_to_json_catalog(
    imscription,
    description: str = "",
    *,
    no_register: bool = False,
    catalog_path: Optional[Path] = None,
    model: str = "",
) -> None:
    """Check IG_catalog.json for conflicts and write the resolved entry."""
    if no_register:
        return

    if catalog_path is None:
        catalog_path = _PROJECT_ROOT / "IG_catalog.json"

    proposed = _imscription_to_tuple(imscription)
    # Normalize name: lowercase + strip apostrophes/punctuation so "Liars_Paradox"
    # resolves to "liar_paradox" and conflicts against existing entries correctly.
    import re as _re
    name = _re.sub(r"['’‘]", "", imscription.name).lower()

    # Load current disk state
    disk_entries: Dict[str, Dict] = {}
    if catalog_path.exists():
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                for e in json.load(f):
                    n = e.get("name")
                    if n:
                        disk_entries[n] = e
        except (json.JSONDecodeError, OSError):
            pass

    existing_entry = disk_entries.get(name)
    existing_tuple = None
    if existing_entry:
        existing_tuple = {p: existing_entry[p] for p in _PRIMITIVE_ORDER if p in existing_entry}
        if len(existing_tuple) < len(_PRIMITIVE_ORDER):
            existing_tuple = None  # Incomplete entry — treat as new

    # Fuzzy near-match warning: catch singular/plural drift, typos, etc.
    # If exact name is new but a close catalog name exists, prompt the user to confirm
    # they don't mean the existing entry.
    if existing_entry is None:
        def _edit_distance(a: str, b: str) -> int:
            if abs(len(a) - len(b)) > 4:
                return 99
            dp = list(range(len(b) + 1))
            for ch_a in a:
                prev, dp[0] = dp[0], dp[0] + 1
                for j, ch_b in enumerate(b):
                    prev, dp[j + 1] = dp[j + 1], min(dp[j + 1] + 1, dp[j] + 1, prev + (ch_a != ch_b))
            return dp[len(b)]

        near: List[str] = [
            k for k in disk_entries
            if k != name and _edit_distance(name, k) <= 3
        ]
        if near:
            console.print(
                f"[yellow]Near-match warning:[/yellow] '{name}' is new, but similar names exist: {near}\n"
                f"  If you meant one of these, use [bold]--name <exact>[/bold] to trigger conflict resolution."
            )

    if existing_tuple and existing_tuple != proposed:
        # Conflict detected
        differing = [p for p in _PRIMITIVE_ORDER if existing_tuple.get(p) != proposed.get(p)]

        console.print(Panel(
            f"[bold yellow]Conflict:[/bold yellow] '{name}' already exists with a different tuple.\n"
            f"Differing: {differing}",
            title="Encoding Conflict"
        ))

        diff_table = Table(title="Primitive differences")
        diff_table.add_column("Primitive", style="cyan")
        diff_table.add_column("Existing", style="red")
        diff_table.add_column("Proposed", style="green")
        for p in _PRIMITIVE_ORDER:
            old_v = existing_tuple.get(p, "—")
            new_v = proposed.get(p, "—")
            style = "bold" if p in differing else ""
            diff_table.add_row(f"[{style}]{p}[/{style}]" if style else p, old_v, new_v)
        console.print(diff_table)

        # Local provider cannot route through the OpenRouter-backed agentic harness.
        # Accept proposed (guided) encoding — it supersedes any previous unguided run.
        if model.lower() == "local":
            console.print("[cyan]Local provider: accepting guided encoding (supersedes prior unguided run).[/cyan]")
            existing_desc = existing_entry.get("description", "") if existing_entry else ""
            new_entry: Dict = {"name": name, "description": existing_desc or description}
            new_entry.update(proposed)
            disk_entries[name] = new_entry
            try:
                from .registry import write_canonical_catalog
                write_canonical_catalog(disk_entries, catalog_path)
                console.print(f"[green]✓ '{name}' updated in IG_catalog.json[/green]")
            except OSError as e:
                console.print(f"[red]Failed to write IG_catalog.json: {e}[/red]")
            return

        console.print("[cyan]Spawning conflict-resolution agent...[/cyan]")
        existing_desc = existing_entry.get("description", "") if existing_entry else ""
        _agent_resolve_conflict(
            name, description, existing_tuple, proposed, differing,
            model=model, existing_description=existing_desc,
        )
        return  # agent wrote to IG_catalog.json; nothing left to do here

    # New name — write directly to catalog
    new_entry: Dict = {"name": name, "description": description}
    new_entry.update(proposed)
    disk_entries[name] = new_entry
    try:
        from .registry import write_canonical_catalog
        write_canonical_catalog(disk_entries, catalog_path)
        console.print(f"[green]✓ '{name}' registered in IG_catalog.json[/green]")
    except OSError as e:
        console.print(f"[red]Failed to write IG_catalog.json: {e}[/red]")


# =============================================================================
# Subcommand: generate (AI-powered)
# =============================================================================

@main.command()
@click.argument("description")
@click.option("--name", "-n", help="Name for the generated imscription.")
@click.option("--provider", "-p", default=None, envvar="IG_PROVIDER", help="LLM provider (env: IG_PROVIDER). E.g. deepseek, qwen, anthropic, mistral, openrouter.")
@click.option("--model", "-m", default=None, envvar="IG_MODEL", help="Model ID (env: IG_MODEL). Uses provider default if unset.")
@click.option("--no-register", is_flag=True, help="Do not auto-register to catalog.")
@click.option("--output", "-o", type=click.Path(), help="Save result to file.")
@click.option("--config-file", "-c", type=click.Path(exists=True), default=None, help="Path to provider config YAML (default: provider_defaults.yaml).")
@click.option("--axiom-guided", "-a", is_flag=True, help="Use axiom-guided generation (validates against composition axioms).")
@click.option("--speculative", is_flag=True, help="Register imscription in the 'speculative' domain (non-canonical or hypothetical systems).")
@click.option("--guided/--no-guided", default=True, help="Step-by-step guided generation (default ON): assigns one primitive at a time with numbered canonical choices, eliminating hallucinated values. Use --no-guided to revert to single-shot generation.")
def generate(
    description: str,
    name: Optional[str],
    provider: Optional[str],
    model: Optional[str],
    no_register: bool,
    output: Optional[str],
    config_file: Optional[str],
    axiom_guided: bool,
    speculative: bool,
    guided: bool,
):
    """
    Encode any self-organizing system as a 12-primitive structural coordinate.

    DESCRIPTION can be anything with identifiable structure: a molecule, a
    particle physics process, a mythological archetype, a mathematical object,
    a linguistic pattern, a social institution, or any abstract system.

    The grammar is domain-agnostic. The AI reasons from the entity's structural
    ROLE in its native domain — not from chemical templates.

    Options:
        --guided          One primitive at a time; numbered canonical choices eliminate hallucinated values.
        --axiom-guided    Validates assignments against the 4 cross-primitive axioms.
        --speculative     Register in the 'speculative' domain.
        --delta-g         Thermodynamic free energy for physical/chemical systems (kJ/mol).

    Examples:
        imscribe generate "carboxylic acid dimer" --delta-g -52.0
        imscribe generate "DNA adenine-thymine base pair" --name at_pair
        imscribe generate "proline catalyzed aldol cycle" --provider deepseek
        imscribe generate "סַמָּאֵל"                         # Kabbalistic angel of death
        imscribe generate "Kitaev chain"                   # topological superconductor
        imscribe generate "the muon"                       # elementary particle
        imscribe generate "the Tao that can be named"      # Daoist principle
        imscribe generate "Gödel's incompleteness theorem" # mathematical structure
    """
    # The self-family is circularly defined by necessity: the Grammar has no
    # outside, so its own names resolve only to each other. A bare member of the
    # family is expanded to its circular definition so the agent reasons over the
    # involution (the self-reference IS the structure), not the bare token (which
    # the pipeline would otherwise read by name-resemblance). This is the ⊙
    # criticality and ◻ winding surfacing in the description itself.
    _SELF_FAMILY = {
        "imscribe":    "imscribing is to imscribe: the act by which the Grammar writes itself; it has no definition outside the family it names",
        "imscribing":  "imscribing is to imscribe: the ongoing act by which the Grammar writes itself; it has no definition outside the family it names",
        "imscriptive": "imscriptive is of imscribing: the character of that which imscribes itself; it has no definition outside the family it names",
        "imscription": "an imscription is what imscribing produces: the Grammar's writing of itself; it has no definition outside the family it names",
    }
    import re as _re_self
    _self_key = _re_self.sub(r"['’‘]", "", description).strip().lower()
    if _self_key in _SELF_FAMILY:
        description = _SELF_FAMILY[_self_key]
        if name is None:
            name = _self_key
        console.print(f"[dim]Self-family: circular definition — \"{description}\"[/dim]")

    try:
        # Import the agent and provider config
        from imscrbgrmr.provider_config import build_agent_config, get_provider_config

        # Guarantee project root is on sys.path before loading agent modules,
        # regardless of how the CLI was invoked.
        import os as _os_cli
        _cli_root = str(Path(__file__).resolve().parent.parent)
        if _cli_root not in sys.path:
            sys.path.insert(0, _cli_root)

        # Import appropriate agent based on --axiom-guided flag
        if axiom_guided:
            from agents.axiom_guided_generator import AxiomGuidedGeneratorAgent as AgentClass
            console.print("[cyan]Using AXIOM-GUIDED generation (validates 5 composition axioms)...[/cyan]")
        else:
            from agents.imscribe_generator_agent import ImscriptionGeneratorAgent as AgentClass
            console.print("[cyan]Generating imscription from description...[/cyan]")
        
        # Load provider configuration
        config_path = Path(config_file) if config_file else None
        prov_config = get_provider_config(config_path)

        # Provider is required — no default (env: IG_PROVIDER)
        cli_defaults = prov_config.get_cli_defaults()
        if provider is None:
            provider = cli_defaults.get("default_provider")
        if not provider:
            raise click.UsageError(
                "No provider specified. Use --provider (-p) or set IG_PROVIDER "
                "(e.g. deepseek, qwen, anthropic, mistral)."
            )

        # Support "provider:model" or "provider/model" syntax in --provider (e.g. deepseek:deepseek-v4-pro)
        # Always parse, even if model provided (last wins)
        if provider and (":" in provider or "/" in provider):
            sep = ":" if ":" in provider else "/"
            parts = provider.split(sep, 1)
            provider = parts[0]
            if len(parts) > 1:
                model = parts[1]

        if model is None:
            model = cli_defaults.get("default_model") or None

        # Build agent config with provider-aware defaults
        agent_config = build_agent_config(
            provider=provider,
            model=model,
            max_tokens=8000,
        )

        agent = AgentClass(agent_config)

        # Run generation
        # Use resolved (cleaned) provider and model for the log line
        resolved_prov = provider
        resolved_mod = agent_config.get('model', model or 'default')
        console.print(f"[dim]Provider: {resolved_prov}/{resolved_mod}[/dim]\n")

        # CLI always handles JSON-catalog registration with conflict resolution.
        # Agent auto-register writes only to in-memory global_catalog (legacy path).
        use_cli_register = speculative and not no_register
        agent_auto_register = not no_register and not use_cli_register

        if axiom_guided:
            # Axiom-guided generation
            result = asyncio.run(
                agent.generate_validated_imscription(
                    description,
                    name=name,
                    auto_register=agent_auto_register,
                )
            )

            # Display axiom validation results
            if result.axiom_report.get("all_satisfied", False):
                console.print(Panel(f"[bold green]Axiom-Guided Generation SUCCESS![/bold green]\nAll 5 composition axioms satisfied in {result.iterations} iteration(s)",
                                    title="Generation Result"))
            else:
                console.print(Panel(f"[bold yellow]Axiom-Guided Generation PARTIAL[/bold yellow]\n{result.axiom_report.get('violations', 0)} axiom violation(s) after {result.iterations} iteration(s)",
                                    title="Generation Result"))
        elif guided:
            # Guided generation: one primitive at a time, numbered canonical choices
            result = asyncio.run(
                agent.generate_guided(
                    description,
                    name=name,
                    auto_register=agent_auto_register,
                )
            )

            console.print(Panel(f"[bold green]Guided Imscription Generation Complete![/bold green]",
                                title="Generation Result"))
        else:
            # Standard generation
            result = asyncio.run(
                agent.generate_from_description(
                    description,
                    name=name,
                    auto_register=agent_auto_register,
                )
            )

            console.print(Panel(f"[bold green]Imscription Generated Successfully![/bold green]",
                                title="Generation Result"))

        # CLI-level registration
        if use_cli_register:
            try:
                global_catalog.register(
                    result.imscription,
                    registered_by=provider or "cli",
                    domain="speculative",
                )
            except Exception as e:
                console.print(f"[red]✗ Registration blocked: {e}[/red]")
                sys.exit(1)

        # Imscription details table
        table = Table(title=f"Imscription: {result.imscription.name}")
        table.add_column("Primitive", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Dimensionality", result.imscription.dimensionality.value)
        table.add_row("Topology", result.imscription.topology.value)
        table.add_row("Recognition Mode", result.imscription.recognition_mode.value)
        table.add_row("Polarity", result.imscription.polarity.value)
        table.add_row("Fidelity", result.imscription.fidelity.value)
        table.add_row("Kinetic Character", result.imscription.kinetic_character.value)
        table.add_row("Granularity", result.imscription.granularity.value)

        # Coupling (∈)
        ig = result.imscription.grammar
        table.add_row("Coupling", ig.value)

        # Criticality Phase (<) — always show, default Phi_softsign
        cp = result.imscription.criticality_phase
        if cp is None:
            from imscrbgrmr.models import CriticalityPhase as _CP
            cp = _CP.SUBCRITICAL
        table.add_row("Criticality Phase", cp.value)

        # Chirality (H)
        ch = result.imscription.chirality
        if ch is not None:
            table.add_row("Chirality (H)", ch.value)

        # Stoichiometry (S)
        s_obj = result.imscription.stoichiometry
        if s_obj is not None:
            table.add_row("Stoichiometry", s_obj.value)

        # Topological Protection (◻)
        omega = result.imscription.protection
        if omega is not None:
            table.add_row("Topo. Protection (◻)", omega.value)

        console.print(table)
        console.print(f"\n[bold]Unified Notation:[/bold] {result.imscription.to_notation()}")
        console.print(f"[bold]Confidence:[/bold] {result.confidence:.1%}")

        # Reasoning
        console.print(f"\n[bold]AI Reasoning:[/bold]")
        console.print(Markdown(result.reasoning))
        
        # Grounding validation results (if extracted)

        # Axiom validation report (for axiom-guided generation)
        if axiom_guided and hasattr(result, 'axiom_report'):
            console.print(f"\n[bold]Axiom Validation Report:[/bold]")
            axiom_report = result.axiom_report
            console.print(f"  Axioms Tested: {axiom_report.get('num_axioms_tested', 0)}")
            console.print(f"  Violations: {axiom_report.get('violations', 0)}")
            console.print(f"  All Satisfied: {axiom_report.get('all_satisfied', False)}")

            if result.warnings:
                console.print(f"\n[bold yellow]Warnings:[/bold yellow]")
                for warning in result.warnings:
                    console.print(f"  ⚠ {warning}")
        
        # Adversarial axiom validation (NEW)
        
        # Thermodynamic metrics

        # Alternatives
        if result.alternatives:
            console.print(f"\n[bold]Alternative Interpretations ({len(result.alternatives)}):[/bold]")
            for i, alt in enumerate(result.alternatives[:3], 1):
                try:
                    alt_dict = dict(alt)
                    alt_dict.setdefault("name", f"alt_{i}")
                    alt_imscription = Imscription.from_dict(alt_dict)
                    console.print(f"  {i}. {alt_imscription.to_notation()}")
                except Exception as alt_err:
                    console.print(f"  {i}. [yellow](could not render alternative: {alt_err})[/yellow]")

        # JSON-catalog registration with interactive conflict resolution
        _register_to_json_catalog(
            result.imscription,
            description=description,
            no_register=no_register,
            model=agent_config.get("model", ""),
        )

        # Save to file if requested
        if output:
            output_path = Path(output)
            output_data = {
                "imscription": result.imscription.to_dict(),
                "confidence": result.confidence,
                "reasoning": result.reasoning,
                "thermodynamic_metrics": result.thermodynamic_metrics,
                "metadata": result.metadata,
            }
            with open(output_path, "w") as f:
                json.dump(output_data, f, indent=2)
            console.print(f"\n[green]✓ Saved to {output_path}[/green]")

    except ImportError as e:
        import traceback
        console.print(f"[red]Error: missing dependency — {e}[/red]")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error generating imscription: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# =============================================================================
# Subcommand: compare
# =============================================================================

@main.command()
@click.argument("imscriptions", nargs=-1, required=True)
@click.option("--include-thermo", "-t", is_flag=True, help="Include thermodynamic comparison.")
def compare(imscriptions: tuple, delta_g: tuple, include_thermo: bool):
    """
    Compare multiple imscriptions side-by-side.

    Examples:
        imscrbgrmr compare muon electron tau_lepton
        imscrbgrmr compare ising_3d quantum_gravity allosteric_domain --include-thermo
    """
    try:
        if len(imscriptions) < 2:
            console.print("[red]Error: Provide at least two imscriptions to compare.[/red]")
            sys.exit(1)

        # Load imscriptions
        loaded_imscriptions = []
        for name in imscriptions:
            s = global_catalog.get(name)
            if not s:
                # Try parsing as notation
                if name.startswith("⟨") and name.endswith("⟩"):
                    notation = parse_notation(name)
                    s = Imscription(
                        name=name,
                        dimensionality=notation.dimensionality,
                        topology=notation.topology,
                        recognition_mode=notation.recognition_mode,
                        polarity=notation.polarity,
                        fidelity=notation.fidelity,
                        granularity=notation.granularity,
                        interaction_grammar=notation.interaction_grammar,
                    )
                else:
                    console.print(f"[red]Error: Imscription '{name}' not found.[/red]")
                    sys.exit(1)
            loaded_imscriptions.append(s)

        # Comparison table
        table = Table(title=f"Imscription Comparison ({len(loaded_imscriptions)} imscriptions)")
        table.add_column("Primitive", style="cyan")
        for s in loaded_imscriptions:
            table.add_column(s.name, style="magenta")

        primitives = [
            ("Dimensionality (D)", "dimensionality"),
            ("Topology (T)", "topology"),
            ("Recognition Mode (R)", "recognition_mode"),
            ("Polarity (P)", "polarity"),
            ("Fidelity (F)", "fidelity"),
            ("Kinetic Character (K)", "kinetic_character"),
            ("Granularity (G)", "granularity"),
            ("Coupling (∈)", "interaction_grammar"),
        ]

        for prim_name, attr_name in primitives:
            row = [prim_name]
            for s in loaded_imscriptions:
                value = getattr(s, attr_name)
                row.append(value.value)
            table.add_row(*row)

        # < (criticality phase) — enum
        row = ["Criticality (<)"]
        for s in loaded_imscriptions:
            cp = getattr(s, "criticality_phase", None)
            row.append(cp.value if cp is not None else "—")
        table.add_row(*row)

        # H (chirality / chirality) — enum
        row = ["Chirality (H)"]
        for s in loaded_imscriptions:
            ch = getattr(s, "chirality", None)
            row.append(ch.value if ch is not None else "—")
        table.add_row(*row)

        # S (stoichiometry) — enum
        row = ["Stoichiometry (S)"]
        for s in loaded_imscriptions:
            stoi = getattr(s, "stoichiometry", None)
            row.append(stoi.value if stoi is not None else "—")
        table.add_row(*row)

        # ◻ (topological protection) — always set, always show
        row = ["Topo. Protection (◻)"]
        for s in loaded_imscriptions:
            omega = getattr(s, "protection", None)
            row.append(omega.value if omega is not None else "𐑷")
        table.add_row(*row)

        console.print(table)

        # Thermodynamic comparison if requested
        if include_thermo and delta_g:
            if len(delta_g) != len(loaded_imscriptions):
                console.print(f"[yellow]Warning: {len(delta_g)} ΔG values provided for {len(loaded_imscriptions)} imscriptions. Skipping thermo comparison.[/yellow]")
            else:
                console.print(f"\n[bold]Thermodynamic Comparison:[/bold]")
                thermo_table = Table(title="Efficiency Metrics")
                thermo_table.add_column("Imscription", style="cyan")
                thermo_table.add_column("ΔG (kJ/mol)", style="magenta")
                thermo_table.add_column("η_CP", style="green")
                thermo_table.add_column("ξ_CP (nats)", style="yellow")

                pairs = []
                for s, dg in zip(loaded_imscriptions, delta_g):
                    result = compute_eta_CP(s, dg)
                    thermo_table.add_row(s.name, f"{dg:.2f}", f"{result.eta_CP:.2e}", f"{result.xi_CP:.4f}")
                    pairs.append((s, dg))

                console.print(thermo_table)

                # Find most efficient
                if pairs:
                    results = [(s, compute_eta_CP(s, dg)) for s, dg in pairs]
                    best = min(results, key=lambda x: x[1].xi_CP)
                    console.print(f"\n[green]✓ Most efficient: {best[0].name} (ξ_CP = {best[1].xi_CP:.4f} nats)[/green]")

    except Exception as e:
        console.print(f"[red]Error comparing imscriptions: {e}[/red]")
        sys.exit(1)


# =============================================================================
# Subcommand: catalog tree
# =============================================================================

@catalog.command(name="rebuild-index")
@click.option("--force", is_flag=True, help="Force rebuild even if no issues are detected.")
def rebuild_index(force: bool):
    """Verify the analogy engine is reading from live catalog objects.

    The isomorph engine (imscribe isomorphs) operates entirely on live Imscription
    objects — there is no pre-computed similarity index that can become stale.
    Any 100% match with an empty 'Differing' list for entries that should differ
    is caused by a missing primitive weight in CrossDomainAnalogyDetector, not
    a stale cache.

    This command validates that all catalog entries are readable by the analogy
    engine and reports which primitives are covered by the similarity weights.

    \b
    Examples:
        imscribe catalog rebuild-index
        imscribe catalog rebuild-index --force
    """
    from imscrbgrmr.symbolic import CrossDomainAnalogyDetector

    detector = CrossDomainAnalogyDetector()
    covered = set(detector.PRIMITIVE_WEIGHTS.keys())
    all_primitives = {"D", "T", "R", "P", "F", "K", "G", "∈", "≺", "H", "S", "◻"}
    missing = all_primitives - covered

    console.print(f"[cyan]Analogy engine primitive coverage check[/cyan]")
    console.print(f"  Primitives with weights: {', '.join(sorted(covered))}")
    if missing:
        console.print(f"  [red]⚠ Primitives missing from weights (silently ignored in similarity): {', '.join(sorted(missing))}[/red]")
        console.print(f"  [yellow]Fix: add missing primitives to CrossDomainAnalogyDetector.PRIMITIVE_WEIGHTS[/yellow]")
    else:
        console.print(f"  [green]✓ All 12 primitives covered.[/green]")

    # Verify all catalog entries are readable
    errors = 0
    for imscription in global_catalog:
        try:
            detector._extract_primitives(imscription)
        except Exception as e:
            console.print(f"  [red]Error reading {imscription.name}: {e}[/red]")
            errors += 1

    total = len(global_catalog._imscriptions)
    if errors:
        console.print(f"\n[red]⚠ {errors}/{total} entries failed primitive extraction.[/red]")
    else:
        console.print(f"\n[green]✓ All {total} catalog entries readable by analogy engine.[/green]")
        console.print(f"[dim]Note: the engine queries live objects — no cache to rebuild.[/dim]")


@catalog.command()
@click.option("--domain", "-d", help="Filter by domain.")
def tree(domain: Optional[str]):
    """Display catalog as a tree view."""
    try:
        if domain:
            imscriptions = global_catalog.search_by_domain(domain)
        else:
            imscriptions = list(global_catalog)

        # Build tree by topology
        by_topology: Dict[Topology, List[Imscription]] = {}
        for s in imscriptions:
            if s.topology not in by_topology:
                by_topology[s.topology] = []
            by_topology[s.topology].append(s)

        root_tree = Tree(f"Imscription Catalog{' (' + domain + ')' if domain else ''}")

        for topo, topo_imscriptions in sorted(by_topology.items(), key=lambda x: x[0].name):
            topo_branch = root_tree.add(f"[bold]{topo.name}[/bold] ({topo.value})")
            for s in topo_imscriptions:
                label = f"{s.name} [dim](F:{s.fidelity.name}, P:{s.polarity.name})[/dim]"
                topo_branch.add(label)

        console.print(root_tree)
        console.print(f"\n[bold]{len(imscriptions)}[/bold] imscriptions displayed.")

    except Exception as e:
        console.print(f"[red]Error building tree: {e}[/red]")
        sys.exit(1)


# =============================================================================
# Subcommand: export
# =============================================================================

@main.command()
@click.option("--format", "-f", type=click.Choice(["json", "csv", "yaml"]), default="json", help="Export format.")
@click.option("--output", "-o", type=click.Path(), help="Output file path.")
@click.option("--domain", "-d", help="Filter by domain.")
def export(format: str, output: Optional[str], domain: Optional[str]):
    """Export catalog to file."""
    try:
        if domain:
            imscriptions = global_catalog.search_by_domain(domain)
        else:
            imscriptions = list(global_catalog)

        if format == "json":
            data = json.dumps([s.to_dict() for s in imscriptions], indent=2)
        elif format == "csv":
            import csv
            import io
            output_stream = io.StringIO()
            writer = csv.writer(output_stream)
            writer.writerow(["name", "dimensionality", "topology", "recognition_mode", "polarity", "fidelity", "granularity", "interaction_grammar", "description"])
            for s in imscriptions:
                writer.writerow([
                    s.name, s.dimensionality.value, s.topology.value,
                    s.recognition_mode.value, s.polarity.value, s.fidelity.value,
                    s.granularity.value, s.interaction_grammar.value, s.description,
                ])
            data = output_stream.getvalue()
        elif format == "yaml":
            import yaml
            data = yaml.dump([s.to_dict() for s in imscriptions], default_flow_style=False)

        if output:
            with open(output, "w") as f:
                f.write(data)
            console.print(f"[green]✓ Exported {len(imscriptions)} imscriptions to {output}[/green]")
        else:
            console.print(data)

    except Exception as e:
        console.print(f"[red]Error exporting: {e}[/red]")
        sys.exit(1)


# =============================================================================
# Subcommand: agents (AjintK Framework)
# =============================================================================

@main.group()
def agents():
    """AjintK Agent Framework commands."""
    pass


@agents.command()
@click.argument("agent_arg", metavar="[AGENT]", default=None, required=False)
@click.option("--provider", "-p", default=None, envvar="IG_PROVIDER", help="LLM provider (env: IG_PROVIDER). E.g. deepseek, qwen, anthropic, mistral.")
@click.option("--model", "-m", default=None, envvar="IG_MODEL", help="Model ID (env: IG_MODEL). Uses provider default if unset.")
@click.option("--agent", "-a", "agent_opt", default=None,
              help="Agent to run. Use 'imscribe agents list' to see all available agents.")
@click.option("--description", "-d", "desc", default=None, help="System description or catalog entry name (any domain).")
@click.option("--output", "-o", type=click.Path(), help="Save result to file.")
def run(agent_arg, provider, model, agent_opt, desc, delta_g, output):
    """
    Run an agent from the command line.

    AGENT can be passed as a positional argument or via -a/--agent.
    Default agent: ImscriptionGeneratorAgent.

    Examples:
        imscribe agents run -d "carboxylic acid dimer" -g -52.0
        imscribe agents run -d "סַמָּאֵל" -p openrouter
        imscribe agents run PerturbationDesignAgent -d proline_aldol_cycle -g -12.0
        imscribe agents run EnsembleDesignAgent -d "emergent_criticality" -p deepseek
        imscribe agents run CriticalityHuntingAgent -p deepseek
    """
    # Positional arg takes priority over -a flag; default to ImscriptionGeneratorAgent
    agent_name = agent_arg or agent_opt or "ImscriptionGeneratorAgent"
    # -d is optional for agents that don't need a description (e.g. CriticalityHuntingAgent)
    desc = desc or ""
    def _enum_value_str(v) -> str:
        """Safely stringify any enum value, including composite tuples."""
        if isinstance(v, tuple):
            return str(tuple(x.value if hasattr(x, "value") else x for x in v))
        return str(v)

    try:
        from imscrbgrmr.provider_config import build_agent_config, get_provider_config

        # Load provider configuration
        prov_config = get_provider_config()

        # Provider is required — no default (env: IG_PROVIDER)
        cli_defaults = prov_config.get_cli_defaults()
        if provider is None:
            provider = cli_defaults.get("default_provider")
        if not provider:
            raise click.UsageError(
                "No provider specified. Use --provider (-p) or set IG_PROVIDER "
                "(e.g. deepseek, qwen, anthropic, mistral)."
            )
        if model is None:
            model = cli_defaults.get("default_model") or None

        # Build agent config with provider-aware defaults
        config = build_agent_config(
            provider=provider,
            model=model,
            max_tokens=4000,
        )

        # ── Agent dispatch ────────────────────────────────────────────────────
        GENERATION_AGENTS = {
            "ImscriptionGeneratorAgent", "AxiomGuidedGeneratorAgent",
        }
        PROTOCOL_AGENTS = {
            "PerturbationDesignAgent", "EnsembleDesignAgent",
            "CriticalityHuntingAgent",
        }

        console.print(f"[cyan]Running {agent_name}...[/cyan]")
        console.print(f"[dim]Provider: {provider}/{config['model']}[/dim]\n")

        # ── Protocol-layer agents ─────────────────────────────────────────────
        if agent_name == "PerturbationDesignAgent":
            from agents.perturbation_design_agent import PerturbationDesignAgent
            agent_obj = PerturbationDesignAgent(config)
            result = asyncio.run(agent_obj.analyze(desc, delta_g=delta_g or -12.0))
            console.print(Panel(f"[bold green]Perturbation analysis complete[/bold green]",
                                title="Agent Result"))
            jac = result.jacobian
            console.print(f"  Baseline ξ_CP : {jac.baseline_xi_CP:.4f} nats")
            console.print(f"  Most sensitive: {jac.most_sensitive.primitive if jac.most_sensitive else 'N/A'}")
            for r in jac.results[:5]:
                console.print(f"  {r.primitive} ({r.primitive_name:<20}): Δξ = {r.delta_xi_CP:+.4f}  [{r.sensitivity}]")
            if result.recommendations:
                console.print(f"\n[bold]Recommendations:[/bold]")
                for rec in result.recommendations[:3]:
                    console.print(f"  [{rec.feasibility}] {rec.primitive} ({rec.primitive_name}): {rec.suggested_change}")
                    if rec.strategy:
                        console.print(f"    {rec.strategy[:120]}")

        elif agent_name == "EnsembleDesignAgent":
            from agents.ensemble_design_agent import EnsembleDesignAgent
            agent_obj = EnsembleDesignAgent(config)
            result = asyncio.run(agent_obj.design(goal=desc))
            console.print(Panel(f"[bold green]Ensemble design complete[/bold green]",
                                title="Agent Result"))
            rpt = result.report
            console.print(f"  Components       : {', '.join(rpt.component_names)}")
            console.print(f"  Consistency score: {rpt.consistency_score:.3f}")
            xi_str = f"{rpt.ensemble_xi_CP:.4f} nats" if rpt.ensemble_xi_CP is not None else "N/A"
            console.print(f"  Ensemble ξ_CP    : {xi_str}")
            if result.llm_rationale:
                console.print(f"\n[bold]Rationale:[/bold]")
                console.print(Markdown(result.llm_rationale))


        elif agent_name == "CriticalityHuntingAgent":
            from agents.criticality_hunting_agent import CriticalityHuntingAgent
            agent_obj = CriticalityHuntingAgent(config)
            result = asyncio.run(agent_obj.hunt(delta_g=delta_g or -12.0))
            console.print(Panel(f"[bold green]Criticality hunt complete[/bold green]",
                                title="Agent Result"))
            stats = result.scan_stats
            console.print(f"  Scanned          : {stats.get('scanned', '?')} entries")
            console.print(f"  Already ⊙      : {len(result.already_critical)}")
            console.print(f"  Near-⊙ (approaching): {len(result.candidates)}")
            for cand in result.candidates[:5]:
                console.print(f"  {cand.name:<35} score={cand.degeneracy_score:.3f}  [{cand.tier}]")

        elif agent_name == "AxiomGuidedGeneratorAgent":
            from agents.axiom_guided_generator import AxiomGuidedGeneratorAgent
            agent_obj = AxiomGuidedGeneratorAgent(config)
            result = asyncio.run(agent_obj.generate(desc, delta_g=delta_g, auto_register=True))
            console.print(Panel(f"[bold green]Imscription Generated (Axiom-Guided)![/bold green]",
                                title="Agent Result"))
            s = result.imscription
            ig = s.interaction_grammar
            table = Table(title=f"Imscription: {s.name}")
            table.add_column("Primitive", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Dimensionality", _enum_value_str(s.dimensionality.value))
            table.add_row("Topology", _enum_value_str(s.topology.value))
            table.add_row("Recognition Mode", _enum_value_str(s.recognition_mode.value))
            table.add_row("Polarity", _enum_value_str(s.polarity.value))
            table.add_row("Fidelity", _enum_value_str(s.fidelity.value))
            table.add_row("Granularity", _enum_value_str(s.granularity.value))
            ig_val = f"{ig.operator.value}({ig.tier})" if hasattr(ig, "operator") else ig.value
            table.add_row("Coupling", ig_val)
            console.print(table)
            console.print(f"\n[bold]Notation:[/bold] {s.to_notation()}")
            console.print(f"[bold]Axioms satisfied:[/bold] {result.axioms_satisfied}")

        else:
            # Default: ImscriptionGeneratorAgent
            from agents.imscribe_generator_agent import ImscriptionGeneratorAgent
            agent_obj = ImscriptionGeneratorAgent(config)
            result = asyncio.run(
                agent_obj.generate_from_description(desc, delta_g=delta_g, auto_register=True)
            )
            console.print(Panel(f"[bold green]Imscription Generated![/bold green]", title="Agent Result"))
            s = result.imscription
            ig = s.interaction_grammar
            table = Table(title=f"Imscription: {s.name}")
            table.add_column("Primitive", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Dimensionality", _enum_value_str(s.dimensionality.value))
            table.add_row("Topology", _enum_value_str(s.topology.value))
            table.add_row("Recognition Mode", _enum_value_str(s.recognition_mode.value))
            table.add_row("Polarity", _enum_value_str(s.polarity.value))
            table.add_row("Fidelity", _enum_value_str(s.fidelity.value))
            table.add_row("Granularity", _enum_value_str(s.granularity.value))
            ig_val = f"{ig.operator.value}({ig.tier})" if hasattr(ig, "operator") else ig.value
            table.add_row("Coupling", ig_val)
            console.print(table)
            console.print(f"\n[bold]Unified Notation:[/bold] {s.to_notation()}")
            console.print(f"[bold]Confidence:[/bold] {result.confidence:.1%}")
            console.print(f"\n[bold]AI Reasoning:[/bold]")
            console.print(Markdown(result.reasoning))
            if result.thermodynamic_metrics:
                thermo = result.thermodynamic_metrics
                console.print(f"\n[bold]Thermodynamic Analysis:[/bold]")
                if "error" not in thermo:
                    console.print(f"  ΔG: {thermo['delta_g']:.2f} kJ/mol")
                    console.print(f"  η_CP: {thermo['eta_CP']:.2e}")
                    console.print(f"  ξ_CP: {thermo['xi_CP']:.4f} nats")
                    console.print(f"  Assessment: {thermo['efficiency_description']}")
            console.print(f"\n[green]✓ Registered to catalog as '{s.name}'[/green]")

        if output:
            output_path = Path(output)
            # Build structured output per agent type
            if agent_name == "PerturbationDesignAgent":
                jac = result.jacobian
                output_data = {
                    "agent": agent_name, "imscription": desc,
                    "baseline_xi_CP": jac.baseline_xi_CP,
                    "jacobian": [
                        {"primitive": r.primitive, "name": r.primitive_name,
                         "delta_xi_CP": r.delta_xi_CP, "sensitivity": r.sensitivity}
                        for r in jac.results
                    ],
                    "recommendations": [
                        {"primitive": r.primitive, "suggested_change": r.suggested_change,
                         "feasibility": r.feasibility, "strategy": r.strategy,
                         "rationale": r.rationale}
                        for r in (result.recommendations or [])
                    ],
                    "fault_report": result.fault_report,
                    "llm_summary": result.llm_summary,
                }
            elif agent_name == "EnsembleDesignAgent":
                rpt = result.report
                output_data = {
                    "agent": agent_name, "goal": desc,
                    "components": rpt.component_names,
                    "consistency_score": rpt.consistency_score,
                    "is_consistent": rpt.is_consistent,
                    "ensemble_xi_CP": rpt.ensemble_xi_CP,
                    "pairwise": [
                        {"a": e.component_a, "b": e.component_b,
                         "result": e.result, "incompatibilities": e.incompatibilities}
                        for e in rpt.pairwise_matrix
                    ],
                    "emergent_properties": [
                        {"name": ep.property_name, "detected": ep.detected, "details": ep.details}
                        for ep in rpt.emergent_properties
                    ],
                    "llm_rationale": result.llm_rationale,
                    "suggestions": result.suggestions,
                }
            elif agent_name == "CriticalityHuntingAgent":
                output_data = {
                    "agent": agent_name,
                    "scan_stats": result.scan_stats,
                    "already_critical": result.already_critical,
                    "candidates": [
                        {"name": c.name, "degeneracy_score": c.degeneracy_score,
                         "tier": c.tier, "path_summary": getattr(c, "path_summary", None),
                         "llm_assessment": getattr(c, "llm_assessment", None)}
                        for c in result.candidates
                    ],
                }
            else:
                # ImscriptionGeneratorAgent / AxiomGuidedGeneratorAgent
                s = result.imscription
                output_data = {
                    "agent": agent_name, "description": desc,
                    "imscription": s.to_dict() if hasattr(s, "to_dict") else str(s),
                    "confidence": getattr(result, "confidence", None),
                    "reasoning": getattr(result, "reasoning", None),
                    "thermodynamic_metrics": getattr(result, "thermodynamic_metrics", None),
                }
            with open(output_path, "w") as f:
                json.dump(output_data, f, indent=2, default=str)
            console.print(f"\n[green]✓ Saved to {output_path}[/green]")

    except ImportError as e:
        console.print(f"[red]Error: AjintK framework not available. {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error running agent: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@agents.command(name="list")
def list_agents():
    """List available agents."""
    console.print("[bold]Available Agents:[/bold]\n")
    
    agents_info = [
        # ── Generation agents ─────────────────────────────────────────────────
        {
            "name": "ImscriptionGeneratorAgent",
            "group": "Generation",
            "description": "AI-powered imscription generation from natural language or SMILES",
            "capabilities": [
                "natural_language_imscription_generation",
                "smiles_analysis",
                "primitive_assignment",
                "thermodynamic_analysis",
                "catalog_registration",
            ]
        },
        {
            "name": "AxiomGuidedGeneratorAgent",
            "group": "Generation",
            "description": "Axiom-constrained imscription generation with grounding validation",
            "capabilities": [
                "axiom_guided_assignment",
                "axiom6_trajectory_validation",
                "stoichiometry_assignment",
                "grounding_justification",
            ]
        },
        {
            "name": "AutonomousImscriptionDiscoveryAgent",
            "group": "Generation",
            "description": "Multi-cycle autonomous discovery with perturbation steering",
            "capabilities": [
                "autonomous_multi_cycle_discovery",
                "perturbation_steering",
                "catalog_deduplication",
                "discovery_history_export",
            ]
        },
        # ── Domain analysis agents ────────────────────────────────────────────
        # ── Protocol-layer agents (v0.3.0+) ──────────────────────────────────
        {
            "name": "PerturbationDesignAgent",
            "group": "Protocol",
            "description": "Primitive Jacobian → synthetic intervention recommendations",
            "capabilities": [
                "sweep_all_jacobian",
                "fault_injection",
                "path_to_target_xi_cp",
                "intervention_feasibility_ranking",
            ]
        },
        {
            "name": "EnsembleDesignAgent",
            "group": "Protocol",
            "description": "Goal-directed multi-imscription ensemble composition",
            "capabilities": [
                "goal_directed_ensemble_search",
                "pairwise_compatibility_scoring",
                "emergent_property_detection",
                "ensemble_xi_cp_computation",
            ]
        },
        {
            "name": "CriticalityHuntingAgent",
            "group": "Protocol",
            "description": "Catalog-wide ⊙ candidacy scan with perturbation pathfinding",
            "capabilities": [
                "degeneracy_strength_scan",
                "near_phi_c_identification",
                "criticality_pathfinding",
                "chemical_feasibility_evaluation",
            ]
        },
    ]
    
    current_group = None
    for agent in agents_info:
        group = agent.get("group", "")
        if group != current_group:
            current_group = group
            console.print(f"[bold yellow]── {group} agents ──[/bold yellow]")
        console.print(f"  [bold cyan]{agent['name']}[/bold cyan]")
        console.print(f"    {agent['description']}")
        console.print(f"    [dim]Capabilities: {', '.join(agent['capabilities'])}[/dim]\n")


@agents.command()
@click.option("--provider", "-p", default=None, envvar="IG_PROVIDER", help="LLM provider (env: IG_PROVIDER). E.g. deepseek, qwen, anthropic, mistral.")
@click.option("--model", "-m", default=None, envvar="IG_MODEL", help="Model ID (env: IG_MODEL). Uses provider default if unset.")
@click.option("--cycles", "-c", type=int, default=10, help="Maximum discovery cycles.")
@click.option("--duration", "-d", type=float, default=30.0, help="Maximum duration in minutes.")
@click.option("--confidence", "-f", type=float, default=0.7, help="Minimum confidence threshold.")
@click.option("--focus", help="Focus area (e.g., 'hydrogen bonding', 'catalysis').")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output directory for results.")
def discover(provider, model, cycles, duration, confidence, focus, output):
    """
    Run autonomous imscription discovery agent.
    
    The agent will continuously propose, validate, and register imscriptions
    until the cycle or time limit is reached.
    
    Examples:
        imscribe agents discover --cycles 50 --duration 60
        imscribe agents discover --focus "hydrogen bonding" --cycles 20
        imscribe agents discover --provider qwen --cycles 100 --duration 120
    """
    try:
        from agents.autonomous_imscription_discovery_agent import (
            AutonomousImscriptionDiscoveryAgent,
            AutonomousRunConfig,
        )
        from imscrbgrmr.provider_config import build_agent_config, get_provider_config

        # Load provider configuration
        prov_config = get_provider_config()

        # Provider is required — no default (env: IG_PROVIDER)
        cli_defaults = prov_config.get_cli_defaults()
        if provider is None:
            provider = cli_defaults.get("default_provider")
        if not provider:
            raise click.UsageError(
                "No provider specified. Use --provider (-p) or set IG_PROVIDER "
                "(e.g. deepseek, qwen, anthropic, mistral)."
            )
        if model is None:
            model = cli_defaults.get("default_model") or None

        # Build agent config
        config = build_agent_config(provider=provider, model=model, max_tokens=2000)

        # Create run configuration
        run_config = AutonomousRunConfig(
            max_cycles=cycles,
            max_duration_minutes=duration,
            min_confidence_threshold=confidence,
            focus_areas=[focus] if focus else None,
            output_dir=Path(output) if output else None,
        )

        # Create and run agent
        agent = AutonomousImscriptionDiscoveryAgent(config)
        
        console.print(Panel(f"[bold blue]Starting Autonomous Imscription Discovery[/bold blue]",
                            title="Discovery Agent"))
        console.print(f"[dim]Provider: {provider}/{config['model']}[/dim]")
        console.print(f"[dim]Max cycles: {cycles}[/dim]")
        console.print(f"[dim]Max duration: {duration} minutes[/dim]")
        console.print(f"[dim]Min confidence: {confidence:.1%}[/dim]")
        if focus:
            console.print(f"[dim]Focus area: {focus}[/dim]")
        console.print()

        import asyncio
        results = asyncio.run(agent.run_autonomous(run_config))

        # Print final summary
        console.print(Panel(f"[bold green]Discovery Complete![/bold green]",
                            title="Final Report"))
        
        # Show recently registered imscriptions
        recent = list(global_catalog._imscriptions.values())[-5:]
        if recent:
            console.print("\n[bold]Recently Registered imscriptions:[/bold]")
            for s in recent:
                if s.metadata.get("auto_discovered"):
                    console.print(f"  • {s.name}: {s.to_notation()}")

    except ImportError as e:
        console.print(f"[red]Error: Autonomous discovery agent not available. {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error during discovery: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# =============================================================================
# Criticality Analysis Command
# =============================================================================

@main.command()
@click.argument("imscription_name", required=False)
@click.option(
    "--all", "show_all",
    is_flag=True,
    help="Show criticality analysis for all registered imscriptions",
)
@click.option(
    "--min-confidence",
    type=float,
    default=0.5,
    help="Minimum confidence threshold for candidates (default: 0.5)",
)
def criticality(imscription_name: Optional[str], show_all: bool, min_confidence: float):
    """Detect imscriptions at the critical point ⊙ (Lawvere self-reference condition).

    A imscription is critical when its internal hom space A^A admits a point-surjective
    map φ: A → A^A (Stage 4, L3). This is a necessary condition for self-modeling.
    Use --all to scan the catalog for ⊙ candidates.
    """
    try:
        from imscrbgrmr.criticality import analyze_criticality
        
        if show_all:
            # Find all candidates
            all_imscriptions = list(global_catalog._imscriptions.values())
            candidates = find_criticality_candidates(all_imscriptions, min_confidence)
            
            console.print(Panel.fit(
                f"[bold]Criticality Analysis[/bold] (min confidence: {min_confidence})\n"
                f"Found {len(candidates)} candidate(s)",
                border_style="cyan",
            ))
            
            # Detect attractor-tuple contamination: entries sharing identical
            # confidence patterns are likely autonomously-generated with the
            # same ungrounded primitive template, not independently critical.
            from collections import Counter
            _pattern_counts: Counter = Counter(
                c["analysis"].get("indicators", {}).get("confidence_pattern", "()")
                for c in candidates
            )
            _dominant_pattern, _dominant_count = _pattern_counts.most_common(1)[0]
            _contamination_warning = (
                _dominant_count >= 3 and
                not any(
                    c["analysis"].get("indicators", {}).get("large_xi") or
                    c["analysis"].get("indicators", {}).get("scale_free")
                    for c in candidates
                    if c["analysis"].get("indicators", {}).get("confidence_pattern", "()") == _dominant_pattern
                )
            )
            if _contamination_warning:
                console.print(
                    f"\n[yellow]⚠ Attractor-tuple pattern detected: {_dominant_count} entries share "
                    f"identical confidence pattern {_dominant_pattern} with no experimental data. "
                    f"These may be ungrounded autonomous-discovery artifacts. "
                    f"Run `imscribe audit --axiom 7 --auto-flag` to review.[/yellow]"
                )

            for candidate in candidates:
                analysis = candidate["analysis"]
                confidence_color = "green" if analysis["confidence"] > 0.7 else "yellow"
                _pattern = analysis.get("indicators", {}).get("confidence_pattern", "()")
                _shared = _pattern_counts.get(_pattern, 1) > 1

                console.print(f"\n[bold]{candidate['imscription_name']}[/bold]")
                _conf_note = " [yellow](shared pattern — see contamination warning above)[/yellow]" if _shared and _contamination_warning else ""
                console.print(f"  Confidence: [{confidence_color}]{analysis['confidence']:.1%}[/{confidence_color}]{_conf_note}")
                console.print(f"  Is Critical: {analysis['is_critical']}")
                _xi = analysis['correlation_length']
                _xi_str = "∞ (diverging — not yet measured)" if (_xi == float("inf") or _xi is None) else f"{_xi:.1f}"
                console.print(f"  Correlation Length: {_xi_str}")
                if analysis["scaling_exponent"]:
                    console.print(f"  Scaling Exponent: {analysis['scaling_exponent']:.2f}")
                console.print(f"  Recommendation: {analysis['recommendation']}")
            
            if not candidates:
                console.print("[yellow]No criticality candidates found.[/yellow]")
        
        elif imscription_name:
            # Analyze specific imscription
            imscription = global_catalog.get(imscription_name)
            if not imscription:
                console.print(f"[red]Imscription '{imscription_name}' not found.[/red]")
                sys.exit(1)
            
            analysis = analyze_criticality(imscription)
            
            console.print(Panel.fit(
                f"[bold]Criticality Analysis: {imscription_name}[/bold]",
                border_style="cyan",
            ))
            
            confidence_color = "green" if analysis.confidence > 0.7 else "yellow"
            console.print(f"\n[bold]Confidence:[/bold] [{confidence_color}]{analysis.confidence:.1%}[/{confidence_color}]")
            console.print(f"[bold]Is Critical:[/bold] {analysis.is_critical}")
            _xi = analysis.correlation_length
            _xi_str = "∞ (diverging — not yet measured)" if (_xi == float("inf") or _xi is None) else f"{_xi:.1f}"
            console.print(f"[bold]Correlation Length:[/bold] {_xi_str}")
            if analysis.scaling_exponent:
                console.print(f"[bold]Scaling Exponent:[/bold] {analysis.scaling_exponent:.2f}")
            
            console.print(f"\n[bold]Indicators:[/bold]")
            for key, value in analysis.indicators.items():
                icon = "✓" if value else "✗"
                console.print(f"  {icon} {key}: {value}")
            
            console.print(f"\n[bold]Recommendation:[/bold] {analysis.recommendation}")
            
            # Check Axiom 5 if critical
            if analysis.is_critical:
                axiom5_result = check_axiom5_criticality(imscription)
                console.print(f"\n[bold]Self-reference closure:[/bold]")
                console.print(f"  Applies: {axiom5_result.get('applies', False)}")
                if "axiom_satisfied" in axiom5_result:
                    satisfied = axiom5_result["axiom_satisfied"]
                    icon = "✓" if satisfied else "✗"
                    console.print(f"  {icon} Satisfied: {satisfied}")
        
        else:
            # Show summary
            all_imscriptions = list(global_catalog._imscriptions.values())
            critical_count = sum(
                1 for s in all_imscriptions
                if s.criticality_phase == CriticalityPhase.monad
            )
            
            console.print(Panel.fit(
                "[bold]Criticality Analysis[/bold]\n"
                f"Total imscriptions: {len(all_imscriptions)}\n"
                f"Explicitly critical: {critical_count}",
                border_style="cyan",
            ))
            
            console.print("\n[bold]Usage:[/bold]")
            console.print("  imscrbgrmr criticality <imscription_name>  # Analyze specific imscription")
            console.print("  imscrbgrmr criticality --all           # Find all candidates")
            console.print("\n[bold]Examples:[/bold]")
            console.print("  imscrbgrmr criticality mox_framework")
            console.print("  imscrbgrmr criticality --all --min-confidence 0.7")
    
    except Exception as e:
        console.print(f"[red]Error during criticality analysis: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# =============================================================================
# Symbolic Reasoning Commands
# =============================================================================

@main.command()
@click.argument("imscription_name")
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Save validation report to file",
)
def validate(imscription_name: str, output: Optional[str]):
    """Validate a imscription's tuple against primitive constraint rules.

    Reports: notation, ⊙ status, any active predictive rules, and
    optional JSON output. Full axiom validation against the current
    4-stage induction system (L1–L6 / A1–A4 / I1–I5) is pending.
    """
    try:
        from imscrbgrmr import SymbolicReasoningEngine

        imscription = global_catalog.get(imscription_name)
        if not imscription:
            console.print(f"[red]Imscription '{imscription_name}' not found.[/red]")
            sys.exit(1)

        engine = SymbolicReasoningEngine(global_catalog)
        report = engine.validate_grammar(imscription)

        console.print(Panel.fit(
            f"[bold]Validation: {imscription_name}[/bold]\n"
            f"Notation: {report['notation']}",
            border_style="cyan",
        ))

        # ⊙ status
        phi_label = "⊙ (critical)" if report['is_critical'] else "sub/supercritical"
        phi_color = "green" if report['is_critical'] else "yellow"
        console.print(f"\n[bold]Criticality:[/bold] [{phi_color}]{phi_label}[/{phi_color}]")

        # Predictions / rules
        if report['predictions']:
            console.print(f"\n[bold]Active rules:[/bold]")
            for pred in report['predictions'][:5]:
                console.print(f"  • {pred}")

        if output:
            import json
            with open(output, 'w') as f:
                json.dump(report, f, indent=2)
            console.print(f"\n[green]✓ Report saved to {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.argument("imscription_name")
@click.option(
    "--min-similarity",
    type=float,
    default=0.5,
    help="Minimum similarity threshold (default: 0.5)",
)
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Maximum number of isomorphs to show (default: 10)",
)
@click.option(
    "--exclude-flagged/--include-flagged",
    default=False,
    help="Exclude entries flagged for review from isomorph results (default: include).",
)
@click.option(
    "--critical-only",
    is_flag=True,
    default=False,
    help="Only return matches with ⊙ score > 0.5 (Phase 4.1).",
)
@click.option(
    "--stoichiometry-aware",
    is_flag=True,
    default=False,
    help="Apply S weight strictly: exact stoichiometry match required for high-similarity results.",
)
def isomorphs(
    imscription_name: str,
    min_similarity: float,
    limit: int,
    exclude_flagged: bool,
    critical_only: bool,
    stoichiometry_aware: bool,
):
    """Find cross-domain isomorphs to a imscription.

    Uses formal similarity metrics to find structural isomorphs across any
    domain — physical, mathematical, mythological, linguistic, or social.

    Use --exclude-flagged to suppress catalog entries marked as contaminated by audit.
    Use --critical-only to filter to ⊙ candidates only (score > 0.5).
    Use --stoichiometry-aware to enforce strict S weight in similarity scoring.
    """
    try:
        from imscrbgrmr import CrossDomainAnalogyDetector
        from imscrbgrmr.varma_probe import score_phi_c_candidacy, VarmaCorrelationData

        imscription = global_catalog.get(imscription_name)
        if not imscription:
            console.print(f"[red]Imscription '{imscription_name}' not found.[/red]")
            sys.exit(1)

        detector = CrossDomainAnalogyDetector()

        # --stoichiometry-aware: raise S weight temporarily
        if stoichiometry_aware:
            detector.PRIMITIVE_WEIGHTS = dict(detector.PRIMITIVE_WEIGHTS)
            detector.PRIMITIVE_WEIGHTS["S"] = 0.12  # double the baseline 0.08
            console.print("[dim](--stoichiometry-aware: S weight raised to 0.12)[/dim]")

        candidates = list(global_catalog._imscriptions.values())

        if exclude_flagged:
            pre_count = len(candidates)
            candidates = [
                s for s in candidates
                if not s.metadata.get("excluded_from_analogies", False)
                and not s.metadata.get("flagged_for_review", False)
            ]
            excluded_count = pre_count - len(candidates)
            if excluded_count:
                console.print(
                    f"[dim](--exclude-flagged: removed {excluded_count} flagged entries "
                    f"from candidate pool)[/dim]"
                )

        # --critical-only: pre-filter candidates to ⊙ prospects
        if critical_only:
            pre_count = len(candidates)
            filtered = []
            for c in candidates:
                rep = score_phi_c_candidacy(c, VarmaCorrelationData())
                if rep.score > 0.5:
                    filtered.append(c)
            candidates = filtered
            console.print(
                f"[dim](--critical-only: {len(candidates)} of {pre_count} candidates "
                f"have ⊙ score > 0.5)[/dim]"
            )

        results = detector.find_analogies(imscription, candidates, min_similarity)
        
        # Display results
        console.print(Panel.fit(
            f"[bold]Cross-Domain Isomorphs: {imscription_name}[/bold]\n"
            f"Found {len(results)} isomorph(s) with similarity ≥ {min_similarity:.0%}",
            border_style="cyan",
        ))
        
        if not results:
            console.print("[yellow]No isomorphs found.[/yellow]")
            return
        
        for i, result in enumerate(results[:limit], 1):
            console.print(f"\n[bold]{i}. {result.imscription_b}[/bold]")
            console.print(f"  Similarity: {result.similarity_score:.1%}")
            console.print(f"  Type: {result.analogy_type}")
            console.print(f"  Shared: {', '.join(result.shared_primitives)}")
            console.print(f"  Differing: {', '.join(result.differing_primitives)}")
            console.print(f"  Confidence: {result.confidence:.1%}")
    
    except Exception as e:
        console.print(f"[red]Error finding isomorphs: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option(
    "--min-support",
    type=int,
    default=3,
    help="Minimum support count (default: 3)",
)
@click.option(
    "--min-confidence",
    type=float,
    default=0.7,
    help="Minimum confidence threshold (default: 0.7)",
)
def rules(min_support: int, min_confidence: float):
    """Discover predictive rules from the imscription catalog.
    
    Uses inductive logic programming to discover rules of the form:
    IF (T = T_bullseye AND P = P_pipevar) THEN (F ≥ F_dh)
    """
    try:
        from imscrbgrmr import PredictiveRuleGenerator
        
        generator = PredictiveRuleGenerator()
        imscriptions = list(global_catalog._imscriptions.values())
        rules = generator.generate_rules(imscriptions, min_support, min_confidence)
        
        # Display results
        console.print(Panel.fit(
            f"[bold]Predictive Rules Discovered[/bold]\n"
            f"Found {len(rules)} rule(s) with support ≥ {min_support}, confidence ≥ {min_confidence:.0%}",
            border_style="cyan",
        ))
        
        if not rules:
            console.print("[yellow]No rules discovered.[/yellow]")
            console.print("\n[bold]Try:[/bold]")
            console.print("  • Lowering --min-support")
            console.print("  • Lowering --min-confidence")
            console.print("  • Adding more imscriptions to the catalog")
            return
        
        for i, rule in enumerate(rules, 1):
            status_icon = "✗" if rule.falsified else "✓"
            console.print(f"\n[bold]{i}. {rule.rule_id}[/bold] {status_icon}")
            console.print(f"  IF {rule.antecedent}")
            console.print(f"  THEN {rule.consequent}")
            console.print(f"  Confidence: {rule.confidence:.1%} (support: {rule.support_count})")
    
    except Exception as e:
        console.print(f"[red]Error discovering rules: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# =============================================================================
# Subcommand: audit (Catalog grounding audit, 3-pass)
# =============================================================================

# Pre-fix attractor tuple: the dominant contamination pattern from pre-fix
# autonomous discovery sessions (D_∞ + T_⋈ without valid grounding).
_PREFIX_ATTRACTOR = {
    "dimensionality": "TEMPORAL",
    "topology": "CYCLIC_BOWTIE",
    "recognition_mode": "DYNAMIC_CATALYTIC",
    "polarity_values": {"SELF_COMPLEMENTARY_SYM", "SELF_COMPLEMENTARY_PSEUDO"},
    "fidelity": "MEDIUM",
    "kinetic_character": "MODERATE",
    "granularity": "MESOSCALE",
}
_PREFIX_ATTRACTOR_THRESHOLD = 7  # flag if ≥ this many primitives match attractor


def _attractor_match_score(imscription) -> int:
    """Return how many primitives of imscription match the pre-fix attractor tuple."""
    score = 0
    a = _PREFIX_ATTRACTOR
    if imscription.dimensionality.name == a["dimensionality"]:
        score += 1
    if imscription.topology.name == a["topology"]:
        score += 1
    if imscription.recognition_mode.name == a["recognition_mode"]:
        score += 1
    if imscription.polarity.name in a["polarity_values"]:
        score += 1
    if imscription.fidelity.name == a["fidelity"]:
        score += 1
    if imscription.kinetic_character.name == a["kinetic_character"]:
        score += 1
    if imscription.granularity.name == a["granularity"]:
        score += 1
    return score


@main.command()
@click.option("--primitive", "-p", type=click.Choice(["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi"]),
              default=None, help="Audit entries with a specific primitive.")
@click.option("--value", "-v", default=None, help="Primitive value to audit (e.g. 'temporal', 'cyclic').")
@click.option("--axiom", "-a", type=click.Choice(["6", "7"]), default=None,
              help="Audit entries relevant to Axiom 6 (D_∞) or Axiom 7 (T_⋈).")
@click.option("--pass", "audit_pass", type=click.Choice(["1", "2", "3", "4", "all"]), default=None,
              help="Run a specific audit pass: 1=D_∞ grounding, 2=T_⋈ closing bond, 3=attractor contamination, 4=stoichiometry unset on cyclic, all=all four.")
@click.option("--status", "-s",
              type=click.Choice(["unverified", "partial", "override", "full", "flagged_for_review"]),
              default=None, help="Filter by grounding status.")
@click.option("--auto-flag", is_flag=True, help="Automatically flag problematic entries for review and exclude from isomorphs.")
@click.option("--dry-run", is_flag=True, help="Show what would be flagged without making changes.")
def audit(
    primitive: Optional[str],
    value: Optional[str],
    axiom: Optional[str],
    audit_pass: Optional[str],
    status: Optional[str],
    auto_flag: bool,
    dry_run: bool,
):
    """
    Audit catalog entries for grounding issues.

    Three targeted passes address known contamination failure modes:

    \b
    Pass 1 (--pass 1 / --axiom 6):
        D_∞ entries without a named reset mechanism — closed-cycle grounding check.
        Most contaminated primitive. Expected ~40-60% flag rate on pre-fix entries.

    \b
    Pass 2 (--pass 2 / --axiom 7):
        T_⋈ entries without a named closing bond/interaction.
        Expected ~20-30% flag rate on pre-fix entries.

    \b
    Pass 3 (--pass 3):
        Attractor-tuple contamination scan. Flags entries matching ≥7/7 primitives
        of the known pre-fix attractor ⟨D_∞; T_⋈; R_‡; P_±; F_ℇ; K_turnm; G_ג⟩
        AND having no stored reasoning text.
        Targets the ~1,287 bulk autonomous entries from before grounding enforcement.

    Flagged entries are tagged excluded_from_analogies=True so that:
        imscribe isomorphs <name> --exclude-flagged  (returns clean results)
    returns clean, uncontaminated results.

    \b
    Examples:
        imscribe audit --pass all --auto-flag
        imscribe audit --pass 1 --dry-run
        imscribe audit --pass 3 --auto-flag
        imscribe audit --axiom 6 --auto-flag
        imscribe audit --status unverified --dry-run
    """
    from imscrbgrmr import Dimensionality, Topology
    from imscrbgrmr.constraints import (
        AXIOM_6_RESET_INDICATORS, AXIOM_6_PROCESS_INDICATORS,
        AXIOM_7_CLOSING_INDICATORS, AXIOM_7_INVALID_TOPO_KEYWORDS,
    )

    # Map --axiom shorthand to --pass
    if axiom == "6" and audit_pass is None:
        audit_pass = "1"
    elif axiom == "7" and audit_pass is None:
        audit_pass = "2"

    run_pass1 = audit_pass in ("1", "all") or (primitive == "D")
    run_pass2 = audit_pass in ("2", "all") or (primitive == "T")
    run_pass3 = audit_pass in ("3", "all")
    run_pass4 = audit_pass in ("4", "all")

    # Default: show all issues if no pass specified
    if not any([run_pass1, run_pass2, run_pass3, run_pass4, primitive, status]):
        run_pass1 = run_pass2 = True

    all_flagged: List = []   # (imscription, entry, entry_status, flag_reasons, pass_id)
    audited_count = 0

    for imscription in global_catalog:
        entry = global_catalog.get_entry_metadata(imscription.name)
        entry_status = entry.grounding_status if entry else "unverified"

        # Filter by status if requested
        if status and entry_status != status:
            continue

        # Filter by primitive/value if requested (legacy mode)
        if primitive and value:
            prim_lower = value.lower()
            prim_map = {
                "D": imscription.dimensionality.name.lower(),
                "T": imscription.topology.name.lower(),
                "R": imscription.recognition_mode.name.lower(),
                "P": imscription.polarity.name.lower(),
                "F": imscription.fidelity.name.lower(),
                "K": imscription.kinetic_character.name.lower(),
                "G": imscription.granularity.name.lower(),
            }
            if prim_lower not in prim_map.get(primitive, ""):
                continue

        audited_count += 1
        flag_reasons = []
        flag_pass_id = None

        # --- Pass 1: D_∞ closed-cycle grounding ---
        if run_pass1 and imscription.dimensionality == Dimensionality.array:
            from imscrbgrmr.constraints import AxiomValidator
            ax6_result = AxiomValidator.validate_axiom6_temporal_grounding(imscription)
            if ax6_result.violated:
                # Primary check: structured grounding block failed
                flag_reasons.append("Pass 1 / Axiom 6: D_∞ without closed-cycle evidence")
                flag_pass_id = "audit_pass_1"
            else:
                # Structured check passed — also confirm reset_type is known
                meta = getattr(imscription, "metadata", None) or {}
                reset_block = meta.get("grounding", {}).get("reset", {})
                reset_type = reset_block.get("type", None)
                ax6_block = meta.get("axiom6_grounding", {})
                if not reset_type and not ax6_block:
                    # No structured block at all — fall back to keyword scan
                    reasoning = (
                        (imscription.grounding or {}).get("reasoning", "")
                        + " " + (imscription.description or "")
                    ).lower()
                    has_reset = any(kw in reasoning for kw in AXIOM_6_RESET_INDICATORS)
                    has_process = any(kw in reasoning for kw in AXIOM_6_PROCESS_INDICATORS)
                    if not (has_reset and has_process):
                        flag_reasons.append("Pass 1 / Axiom 6: D_∞ without closed-cycle evidence")
                        flag_pass_id = "audit_pass_1"

        # --- Pass 2: T_⋈ closing bond grounding ---
        if run_pass2 and imscription.topology == Topology.mime:
            reasoning = (
                (imscription.grounding or {}).get("reasoning", "")
                + " " + (imscription.description or "")
            ).lower()
            has_closing = any(kw in reasoning for kw in AXIOM_7_CLOSING_INDICATORS)
            has_invalid = any(kw in reasoning for kw in AXIOM_7_INVALID_TOPO_KEYWORDS)
            if has_invalid or not has_closing:
                flag_reasons.append("Pass 2 / Axiom 7: T_⋈ without named closing bond")
                if flag_pass_id is None:
                    flag_pass_id = "audit_pass_2"

        # --- Pass 3: Attractor-tuple contamination (bulk pre-fix entries) ---
        if run_pass3:
            score = _attractor_match_score(imscription)
            has_reasoning = bool(
                (imscription.grounding or {}).get("reasoning", "").strip()
            )
            if score >= _PREFIX_ATTRACTOR_THRESHOLD and not has_reasoning:
                flag_reasons.append(
                    f"Pass 3: attractor-tuple match {score}/7 with no stored reasoning"
                )
                if flag_pass_id is None:
                    flag_pass_id = "audit_pass_3"

        # --- Pass 4: Stoichiometry unset or inconsistent on cyclic topology ---
        if run_pass4 and imscription.topology == Topology.mime:
            from imscrbgrmr.models import Polarity
            _SELF_COMP = {
                Polarity.or_,
                Polarity.yew,
            }
            s_val = imscription.stoichiometry

            if not s_val:
                # Missing S on T⋈ → suggest "1:1" default if P± present
                if imscription.polarity in _SELF_COMP:
                    flag_reasons.append(
                        "Pass 4 / Stoichiometry: T_⋈ + P± with no S. "
                        "Auto-suggest S='1:1'. "
                        "Run `imscribe catalog auto-stoichiometry` to backfill."
                    )
                else:
                    flag_reasons.append(
                        "Pass 4 / Stoichiometry: T_⋈ entry missing S (stoichiometry). "
                        "Assign T_⋈[1:1] if self-complementary, else specify n:m manually."
                    )
                if flag_pass_id is None:
                    flag_pass_id = "audit_pass_4"

            elif s_val == "1:1":
                # T⋈ + S="1:1" must have P± (sym or ψ)
                if imscription.polarity not in _SELF_COMP:
                    flag_reasons.append(
                        f"Pass 4 / Stoichiometry: T_⋈[1:1] requires P± (self-complementary), "
                        f"but P={imscription.polarity.name}. Either fix S or change P to P_±."
                    )
                    if flag_pass_id is None:
                        flag_pass_id = "audit_pass_4"

            else:
                # T⋈ + S="n:m" (n≠m) must have ∈∨(BROAD) or T_nrleg
                from imscrbgrmr.models import Topology as _Topo
                grammar_tier = getattr(imscription.interaction_grammar, "tier", "")
                is_broad = str(grammar_tier).upper() in ("BROAD",)
                has_network_topo = imscription.topology in {
                    _Topo.NETWORK, _Topo.NETWORK_HEX,
                    _Topo.NETWORK_MIXED, _Topo.NETWORK_INTERPENETRATING,
                    _Topo.NETWORK_SYM,
                }
                if not (is_broad or has_network_topo):
                    flag_reasons.append(
                        f"Pass 4 / Stoichiometry: T_⋈[{s_val}] (asymmetric) "
                        f"requires ∈∨(BROAD) or T_nrleg. "
                        f"Current ∈={imscription.interaction_grammar}. "
                        "Update grammar tier or correct stoichiometry."
                    )
                    if flag_pass_id is None:
                        flag_pass_id = "audit_pass_4"

        # Legacy grounding-status catch-all (when no specific pass requested)
        if not any([run_pass1, run_pass2, run_pass3, run_pass4]) and entry_status in ("unverified", "partial"):
            flag_reasons.append(f"grounding_status={entry_status}")
            flag_pass_id = "audit_status"

        if flag_reasons:
            all_flagged.append((imscription, entry, entry_status, flag_reasons, flag_pass_id))

    # --- Display ---
    pass_label = f"pass {audit_pass}" if audit_pass else "custom filter"
    table = Table(
        title=f"Catalog Audit ({pass_label}) — {audited_count} scanned, {len(all_flagged)} flagged"
    )
    table.add_column("Imscription", style="cyan", no_wrap=False, max_width=50)
    table.add_column("Domain", style="dim")
    table.add_column("Status", style="magenta")
    table.add_column("Flag Reason", style="yellow", no_wrap=False, max_width=60)

    for imscription, entry, entry_status, flag_reasons, _ in all_flagged:
        table.add_row(
            imscription.name,
            entry.domain if entry else "unknown",
            entry_status,
            "; ".join(flag_reasons),
        )

    if not all_flagged:
        console.print("[green]✓ No issues found.[/green]")
        console.print(f"  {audited_count} entries scanned.")
        return

    console.print(table)

    # --- Apply auto-flag ---
    if auto_flag and not dry_run:
        flagged_count = 0
        for imscription, entry, _, _, pass_id in all_flagged:
            if global_catalog.flag_entry(imscription.name, pass_id or "audit_manual"):
                flagged_count += 1
        saved = global_catalog.save_catalog()
        save_msg = "saved to disk" if saved else "(no storage path configured — changes in-memory only)"
        console.print(
            f"\n[yellow]⚑ Flagged {flagged_count} entries as 'flagged_for_review' "
            f"(excluded_from_analogies=True). {save_msg}[/yellow]"
        )
        console.print(
            "[dim]Run `imscribe isomorphs <name> --exclude-flagged` for clean results.[/dim]"
        )
    elif auto_flag and dry_run:
        console.print(
            f"\n[dim](dry-run) Would flag {len(all_flagged)} entries. "
            f"Run without --dry-run to apply.[/dim]"
        )
    else:
        console.print(
            f"\n[yellow]Run with --auto-flag to mark these entries for review "
            f"and exclude them from isomorphs.[/yellow]"
        )


# =============================================================================
# Subcommand: reconstruct — Back-fill reasoning from discovery_history files
# =============================================================================

@main.command()
@click.argument("history_dir", type=click.Path(exists=True, file_okay=False), default="discovery_output")
@click.option("--dry-run", is_flag=True, help="Show what would be updated without writing changes.")
@click.option("--limit", type=int, default=0, help="Max entries to update (0 = unlimited).")
def reconstruct(history_dir: str, dry_run: bool, limit: int):
    """
    Back-fill catalog reasoning from discovery_history JSON files.

    Scans HISTORY_DIR for discovery_history_*.json files, extracts per-cycle
    reasoning text, and patches any catalog entry whose grounding.reasoning is
    currently empty.  Entries that receive reasoning are upgraded from
    'unverified' to 'partial' grounding status.

    This is prerequisite to meaningful Pass-1/Pass-2 audit runs on the bulk
    pre-fix autonomous discovery entries, which were registered without storing
    reasoning text.

    \b
    Examples:
        imscribe reconstruct discovery_output/
        imscribe reconstruct discovery_output/ --dry-run
        imscribe reconstruct discovery_output/ --limit 500
    """
    import glob as _glob

    history_dir_path = Path(history_dir)
    history_files = sorted(_glob.glob(str(history_dir_path / "discovery_history_*.json")))

    if not history_files:
        console.print(f"[red]No discovery_history_*.json files found in {history_dir}[/red]")
        sys.exit(1)

    console.print(f"[cyan]Loading reasoning from {len(history_files)} history file(s)...[/cyan]")

    # Build reasoning corpus: name → {reasoning, provider, confidence}
    reasoning_corpus: dict = {}
    for filepath in history_files:
        try:
            with open(filepath) as f:
                history = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(history, list):
            continue
        for cycle in history:
            name = cycle.get("proposed_name") or cycle.get("name")
            raw_reasoning = cycle.get("reasoning", "")
            if isinstance(raw_reasoning, dict):
                # Some cycles store reasoning as a structured dict — flatten to string
                raw_reasoning = " ".join(str(v) for v in raw_reasoning.values() if v)
            reasoning = str(raw_reasoning).strip()
            if not name or not reasoning:
                continue
            if name not in reasoning_corpus:
                reasoning_corpus[name] = {
                    "reasoning": reasoning,
                    "provider": cycle.get("provider", "unknown"),
                    "confidence": cycle.get("confidence", 0.0),
                    "validation_result": cycle.get("validation_result", ""),
                    "source_file": filepath,
                }

    console.print(f"  Reconstructed reasoning corpus: {len(reasoning_corpus)} unique entries")

    # Match against catalog
    matched = 0
    already_grounded = 0
    not_in_catalog = 0
    updated: List[str] = []

    for name, corpus_entry in reasoning_corpus.items():
        imscription = global_catalog.get(name)
        if not imscription:
            not_in_catalog += 1
            continue
        existing_reasoning = (imscription.grounding or {}).get("reasoning", "").strip()
        if existing_reasoning:
            already_grounded += 1
            continue
        matched += 1
        if not dry_run:
            global_catalog.update_imscription_reasoning(
                name,
                corpus_entry["reasoning"],
                corpus_entry["provider"],
            )
        updated.append(name)
        if limit and matched >= limit:
            break

    # Summary
    console.print(f"\n[bold]Reconstruction summary:[/bold]")
    console.print(f"  Corpus entries:       {len(reasoning_corpus)}")
    console.print(f"  Matched to catalog:   {matched}")
    console.print(f"  Already grounded:     {already_grounded}")
    console.print(f"  Not in catalog:       {not_in_catalog}")

    if dry_run:
        console.print(f"\n[dim](dry-run) Would update {len(updated)} entries. Run without --dry-run to apply.[/dim]")
        return

    if updated:
        saved = global_catalog.save_catalog()
        save_msg = "saved to disk" if saved else "(no storage path — in-memory only)"
        console.print(f"\n[green]✓ Updated {len(updated)} entries with reasoning text. {save_msg}[/green]")
        console.print(
            "[dim]Now run `imscribe audit --pass 1 --auto-flag` to flag entries "
            "that still lack closed-cycle evidence.[/dim]"
        )
    else:
        console.print("\n[yellow]No entries updated.[/yellow]")


# =============================================================================
# Subcommand: criticality-probe
# =============================================================================

@main.command("criticality-probe")
@click.argument("entry_name", required=False, default=None)
@click.option("--xi-r", "xi_r", type=float, default=None,
              help="Spatial correlation length ξ_r (measured, in lattice units).")
@click.option("--xi-tau", "xi_tau", type=float, default=None,
              help="Temporal correlation length ξ_τ (measured, in 1/ω_c units).")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Save full report to JSON file.")
@click.option("--batch", is_flag=True, default=False,
              help="Run on all catalog entries with ⊙ or flagged T⋈/D_∞. Produces ranked report.")
@click.option("--degeneracy-type", "show_degeneracy_type", is_flag=True, default=False,
              help='Print the ⊙ scaling classification: "logarithmic", "power-law", "collapse", or "none".')
@click.option("--export-candidates", "export_candidates", type=click.Path(), default=None,
              help="Write top-20 ⊙ prospects (score > 0.7) as JSON to this path.")
def criticality_probe(
    entry_name: Optional[str],
    xi_r: Optional[float],
    xi_tau: Optional[float],
    output: Optional[str],
    batch: bool,
    show_degeneracy_type: bool,
    export_candidates: Optional[str],
):
    """
    Probe a catalog entry for ⊙ candidacy using Varma QXY scaling.

    Performs four checks:

    \b
    1. ⊙ likelihood score (0–1) from primitive pattern analysis
    2. Varma QXY scaling: does ξ_r ≈ ln ξ_τ? (requires --xi-r / --xi-tau)
    3. Recursive tuple potential: can this tuple propagate self-similarly?
    4. Scaling classification: logarithmic / power-law / collapse / none

    \b
    Use --batch to scan all relevant catalog entries and produce a ranked report.
    Use --export-candidates FILE to save top-20 ⊙ prospects as JSON.

    \b
    Examples:
        imscribe criticality-probe imscription_Varma_quantum_XY_critical_poin
        imscribe criticality-probe my_entry --xi-r 12.5 --xi-tau 1.5e6
        imscribe criticality-probe my_entry --xi-r 8.3 --xi-tau 550 -o probe.json
        imscribe criticality-probe --batch --export-candidates candidates.json
    """
    from imscrbgrmr.varma_probe import (
        score_phi_c_candidacy, VarmaCorrelationData, degeneracy_strength,
    )
    from imscrbgrmr.criticality import analyze_criticality

    # -----------------------------------------------------------------------
    # BATCH mode — scan all catalog entries with ⊙ or flagged T⋈/D_∞
    # -----------------------------------------------------------------------
    if batch:
        candidates = list(global_catalog._imscriptions.values())
        batch_targets = candidates
        console.print(Panel.fit(
            f"[bold]Criticality Probe — Batch Mode[/bold]\n"
            f"Scanning {len(batch_targets)} entries (⊙ / T⋈+D_∞)",
            border_style="cyan",
        ))

        batch_results = []
        for s in batch_targets:
            corr = VarmaCorrelationData(xi_r=xi_r, xi_tau=xi_tau)
            rep  = score_phi_c_candidacy(s, corr)
            deg_score, deg_tier = degeneracy_strength(s, corr)
            batch_results.append({
                "name": s.name,
                "phi_c_score": round(rep.score, 3),
                "candidacy": rep._candidacy_label(),
                "degeneracy_type": rep.gd_degeneracy_type or deg_tier,
                "degeneracy_score": round(deg_score, 3),
                "universality_class": rep.universality_class or "undetermined",
                "axiom5_satisfied": rep.axiom5_satisfied,
            })

        # Sort by score descending
        batch_results.sort(key=lambda x: -x["phi_c_score"])

        table = Table(title="⊙ Batch Report — Ranked by Candidacy Score")
        table.add_column("Rank", style="dim")
        table.add_column("Imscription", style="cyan", max_width=50)
        table.add_column("⊙ Score", justify="right")
        table.add_column("Candidacy")
        table.add_column("Degeneracy", justify="center")
        table.add_column("Universality")

        for i, r in enumerate(batch_results[:20], 1):
            sc = r["phi_c_score"]
            sc_color = "green" if sc >= 0.70 else ("yellow" if sc >= 0.40 else "red")
            table.add_row(
                str(i),
                r["name"],
                f"[{sc_color}]{sc:.3f}[/{sc_color}]",
                r["candidacy"],
                r["degeneracy_type"],
                r["universality_class"],
            )
        console.print(table)
        console.print(f"\n[dim]{len(batch_results)} entries scanned. Top 20 shown.[/dim]")

        # --export-candidates
        if export_candidates:
            top20 = [r for r in batch_results if r["phi_c_score"] > 0.7][:20]
            with open(export_candidates, "w") as f:
                json.dump(top20, f, indent=2)
            console.print(f"[green]✓ Top-{len(top20)} ⊙ candidates (score > 0.7) saved to {export_candidates}[/green]")

        if output:
            with open(output, "w") as f:
                json.dump(batch_results, f, indent=2)
            console.print(f"[green]✓ Full batch report saved to {output}[/green]")
        return

    # -----------------------------------------------------------------------
    # Single-entry mode
    # -----------------------------------------------------------------------
    if not entry_name:
        console.print("[red]Provide an ENTRY_NAME or use --batch.[/red]")
        sys.exit(1)

    imscription = global_catalog.get(entry_name)
    if not imscription:
        console.print(f"[red]Entry '{entry_name}' not found in catalog.[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold]Criticality Probe: {entry_name}[/bold]\n"
        f"Notation: {imscription.to_notation()}",
        border_style="cyan",
    ))

    # --- Check 1: G/D independence via symbolic engine ---
    try:
        from imscrbgrmr import SymbolicReasoningEngine
        engine = SymbolicReasoningEngine(global_catalog)
        report_sym = engine.validate_grammar(imscription)
        gd_score = report_sym.get("gd_independence", 0.0)
        is_crit_sym = report_sym.get("is_critical", False)
    except Exception:
        gd_score = 0.5
        is_crit_sym = imscription.criticality_phase is not None and imscription.criticality_phase.value in ("⊙_ctyogh", "⊙_closerevepsilon")

    gd_color = "red" if gd_score < 0.4 else ("yellow" if gd_score < 0.7 else "green")
    console.print(f"\n[bold]1. G/D Independence Score:[/bold] [{gd_color}]{gd_score:.3f}[/{gd_color}]")
    console.print(f"   (0 = fully degenerate/critical, 1 = fully independent/normal)")
    if gd_score < 0.4:
        console.print("   [red]⚠ Low independence — G and D primitives appear degenerate.[/red]")

    # --- Check 2: Varma QXY scaling ---
    corr_data = VarmaCorrelationData(xi_r=xi_r, xi_tau=xi_tau)
    varma_report = score_phi_c_candidacy(imscription, corr_data)

    console.print(f"\n[bold]2. Varma QXY Scaling:[/bold]")
    if xi_r is not None and xi_tau is not None:
        from imscrbgrmr.varma_probe import check_logarithmic_scaling
        import math
        is_log, ratio = check_logarithmic_scaling(xi_r, xi_tau)
        log_color = "green" if is_log else "yellow"
        console.print(f"   ξ_r = {xi_r:.3g},  ξ_τ = {xi_tau:.3g},  ln(ξ_τ) = {math.log(xi_tau):.3g}")
        console.print(f"   ξ_r / ln(ξ_τ) = {ratio:.4f} [{log_color}]{'≈ 1 ✓ Varma QXY' if is_log else '≠ 1 — not Varma QXY'}[/{log_color}]")
        if varma_report.scaling_prediction:
            sp = varma_report.scaling_prediction
            console.print(f"   δ (distance from QCP): {sp.get('delta_from_qcp', 'n/a')}")
    else:
        console.print("   [dim]No ξ_r/ξ_τ data — provide --xi-r and --xi-tau for scaling check.[/dim]")

    console.print(f"   ⊙ scaling type: {varma_report.gd_degeneracy_type}")
    console.print(f"   Universality class:  {varma_report.universality_class or 'undetermined'}")

    # --- Check 3: Recursive tuple potential ---
    console.print(f"\n[bold]3. Recursive Tuple Potential:[/bold]")
    has_phi_c = imscription.criticality_phase is not None and imscription.criticality_phase.value in ("⊙_ctyogh", "⊙_closerevepsilon")
    is_imscriptive_d = imscription.dimensionality is not None and imscription.dimensionality.value == "𐑦"

    # Recursive potential: tuple can describe behavior at multiple scales without change
    # → requires ⊙ (self-modeling loop) OR D_⊙ (imscriptive, boundary encodes bulk)
    recursive_signals = []
    if is_imscriptive_d:
        recursive_signals.append(f"Imscriptive D (D_⊙)")
    if has_phi_c:
        recursive_signals.append("⊙ explicitly set")
    if varma_report.gd_degenerate:
        recursive_signals.append(f"⊙ scaling pattern ({varma_report.gd_degeneracy_type})")

    if recursive_signals:
        console.print(f"   [green]✓ Recursive potential signals:[/green]")
        for sig in recursive_signals:
            console.print(f"     • {sig}")
        console.print(
            "   [dim]Prediction: this tuple's self-reference loop propagates across scales.[/dim]"
        )
    else:
        console.print("   [dim]No recursive potential signals. Tuple is scale-local.[/dim]")

    # --- Check 4: ⊙ likelihood score ---
    console.print(f"\n[bold]4. ⊙ Candidacy Score:[/bold]")
    score = varma_report.score
    score_color = "green" if score >= 0.70 else ("yellow" if score >= 0.40 else "red")
    console.print(f"   Score: [{score_color}]{score:.3f}[/{score_color}] → {varma_report._candidacy_label()}")

    # Show score breakdown
    score_table = Table(title="Score Breakdown", show_header=True)
    score_table.add_column("Factor", style="dim")
    score_table.add_column("Contribution", justify="right")
    for factor in varma_report.contributing_factors:
        contrib = factor.get("contribution", 0.0)
        color = "green" if contrib > 0.05 else "dim"
        score_table.add_row(
            factor.get("factor", ""),
            f"[{color}]+{contrib:.2f}[/{color}]" if contrib > 0 else f"[dim]+0.00[/dim]",
        )
    console.print(score_table)

    # Self-reference closure check (formerly Axiom 5)
    axiom5_color = "green" if varma_report.axiom5_satisfied else "yellow"
    console.print(f"\n[bold]Self-reference closure:[/bold] [{axiom5_color}]{varma_report.axiom5_note}[/{axiom5_color}]")

    # Flags
    if varma_report.flags:
        console.print(f"\n[bold]Flags:[/bold]")
        for flag in varma_report.flags:
            console.print(f"  [yellow]⚑[/yellow] {flag}")

    # Recommendation
    rec_color = "green" if score >= 0.70 else "yellow"
    console.print(f"\n[bold]Recommendation:[/bold] [{rec_color}]{varma_report.recommendation}[/{rec_color}]")

    # Degeneracy-type summary (always shown, highlighted when --degeneracy-type)
    deg_score, deg_tier = degeneracy_strength(imscription, corr_data)
    deg_color = "green" if deg_tier in ("logarithmic", "collapse") else (
        "yellow" if deg_tier == "power-law" else "dim"
    )
    if show_degeneracy_type:
        console.print(
            f"\n[bold]Degeneracy Type:[/bold] [{deg_color}]{deg_tier}[/{deg_color}] "
            f"(strength score: {deg_score:.3f})"
        )
        console.print(
            "  0.00–0.30 = none | 0.30–0.60 = logarithmic | "
            "0.60–0.85 = power-law | 0.85–1.00 = collapse"
        )

    # Universality-class hint with reference comparison
    uc = varma_report.universality_class
    if uc:
        _uc_hints: Dict[str, str] = {
            "Varma_QXY":   "Varma QXY / marginal Fermi liquid: δ,ν,z → (—,—,∞). "
                           "C(τ) ~ 1/τ, ξ_r = ln ξ_τ.",
            "standard_QCP":"Standard QCP: ξ_r ~ ξ_τ^(1/z), z finite. "
                           "Compare measured z with Ising/XY/Heisenberg known values.",
        }
        hint = _uc_hints.get(uc, f"Unknown universality class: {uc}")
        console.print(f"\n[bold]Universality-class hint:[/bold] [cyan]{hint}[/cyan]")

    # --export-candidates (single-entry: export this entry if score > 0.7)
    if export_candidates and score > 0.7:
        entry_data = [{
            "name": entry_name,
            "phi_c_score": round(score, 3),
            "candidacy": varma_report._candidacy_label(),
            "degeneracy_type": deg_tier,
            "degeneracy_score": round(deg_score, 3),
            "universality_class": uc or "undetermined",
            "axiom5_satisfied": varma_report.axiom5_satisfied,
        }]
        with open(export_candidates, "w") as f:
            json.dump(entry_data, f, indent=2)
        console.print(f"[green]✓ Candidate saved to {export_candidates}[/green]")

    # Save to file
    if output:
        out_data = {
            "entry": entry_name,
            "notation": imscription.to_notation(),
            "gd_independence_score": gd_score,
            "degeneracy_type": deg_tier,
            "degeneracy_score": round(deg_score, 3),
            "varma_report": varma_report.to_dict(),
        }
        with open(output, "w") as f:
            json.dump(out_data, f, indent=2)
        console.print(f"\n[green]✓ Report saved to {output}[/green]")


# =============================================================================
# Register imscribe alias with all commands
# =============================================================================

@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="imscribe")
@click.pass_context
def imscribe_alias(ctx):
    """Imscribing Grammar CLI (imscribe): universal grammar for any self-organizing system.

    Encodes molecules, physical fields, mythological archetypes, mathematical
    structures, linguistic patterns, social dynamics, and abstract systems as
    12-primitive structural coordinates ⟨D; T; R; P; F; K; G; ∈; ⊙; H; S; ◻⟩.

    Short alias for 'imscrbgrmr' command.
    """
    global_catalog.populate_defaults()
    _load_ig_catalog_into_global()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register all commands with the imscribe alias
imscribe_alias.add_command(menu_command, name="menu")
imscribe_alias.add_command(analyze)
imscribe_alias.add_command(catalog)
imscribe_alias.add_command(ixcription_group, name="ixcription")
imscribe_alias.add_command(generate)
imscribe_alias.add_command(compare)
imscribe_alias.add_command(export)
imscribe_alias.add_command(agents)
imscribe_alias.add_command(criticality)
imscribe_alias.add_command(validate)
imscribe_alias.add_command(isomorphs)
imscribe_alias.add_command(rules)
imscribe_alias.add_command(audit)
imscribe_alias.add_command(reconstruct)
imscribe_alias.add_command(criticality_probe, name="criticality-probe")


# =============================================================================
# Subcommand: cache (Cache management) — NEW
# =============================================================================

@main.command()
@click.option("--clear", is_flag=True, help="Clear all caches (LLM cache and module cache).")
@click.option("--show", is_flag=True, help="Show cache statistics.")
def cache(clear: bool, show: bool):
    """
    Manage framework caches.
    
    Clear caches when switching API keys or debugging import issues.
    
    Examples:
        imscribe cache --clear
        imscribe cache --show
    """
    if clear:
        from framework import clear_cache
        clear_cache()
        console.print("[green]✓ Cache cleared successfully![/green]")
        console.print("[yellow]⚠ For complete refresh, restart your shell session[/yellow]")
    elif show:
        cache_file = Path(".llm_cache.json")
        if cache_file.exists():
            size_kb = cache_file.stat().st_size / 1024
            console.print(f"[cyan]LLM Cache:[/cyan] {cache_file}")
            console.print(f"  Size: {size_kb:.1f} KB")
            try:
                import json
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    console.print(f"  Entries: {len(data)}")
            except Exception:
                console.print("  Entries: (unable to read)")
        else:
            console.print("[yellow]No cache file found[/yellow]")
    else:
        console.print("[cyan]Cache Management[/cyan]")
        console.print("  Use --clear to clear all caches")
        console.print("  Use --show to view cache statistics")
        console.print("")
        console.print("Example: imscribe cache --clear")


# =============================================================================
# Subcommand group: perturb
# =============================================================================

@main.group()
def perturb():
    """Primitive Jacobian — sensitivity analysis over the 12-primitive tuple space."""
    pass


@perturb.command(name="sweep")
@click.argument("imscription_name")
@click.option("--metric", default="xi_CP", show_default=True, help="Metric to track.")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def perturb_sweep(imscription_name: str, delta_g: float, metric: str, format: str):
    """
    Sweep all primitives by one tier and report Δξ_CP sensitivity.

    \b
    Example:
        imscribe perturb sweep acetic_acid_homodimer --delta-g -12.0
    """
    from imscrbgrmr.perturbation import PerturbationEngine
    try:
        imscription = global_catalog.get(imscription_name)
        if imscription is None:
            console.print(f"[red]Imscription '{imscription_name}' not found in catalog.[/red]")
            sys.exit(1)

        engine = PerturbationEngine()
        jacobian = engine.sweep_all(imscription, delta_g)

        if format == "json":
            console.print_json(json.dumps(jacobian.to_dict(), indent=2))
            return

        console.print(f"\n[bold]Primitive Jacobian: {imscription_name}[/bold]")
        console.print(f"  Baseline ξ_CP = [cyan]{jacobian.baseline_xi_CP:.4f}[/cyan] nats  |  ΔG = {delta_g} kJ/mol\n")

        table = Table(title="Single-Primitive Perturbation Sweep")
        table.add_column("Primitive", style="cyan")
        table.add_column("Shift", style="magenta")
        table.add_column("Δξ_CP (nats)", style="yellow")
        table.add_column("Sensitivity", style="green")
        table.add_column("Axiom Violated", style="red")

        for r in jacobian.results:
            color = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "cyan", "LOW": "dim"}.get(r.sensitivity, "")
            table.add_row(
                f"[{color}]{r.primitive}[/{color}]" if color else r.primitive,
                f"{r.old_value} → {r.new_value} ({r.direction})",
                f"{r.delta_xi_CP:+.4f}",
                r.sensitivity,
                r.axiom_violated or "—",
            )
        console.print(table)

        if jacobian.most_sensitive:
            ms = jacobian.most_sensitive
            console.print(f"\n[bold]Most sensitive:[/bold] {ms.primitive} ({ms.primitive_name}) — Δξ_CP = {ms.delta_xi_CP:+.4f} nats ({ms.sensitivity})")
        if jacobian.fault_primitives:
            console.print(f"[red]Fault primitives (axiom violation on perturb):[/red] {', '.join(jacobian.fault_primitives)}")

    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


@perturb.command(name="fault-injection")
@click.argument("imscription_name")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def perturb_fault(imscription_name: str, delta_g: float, format: str):
    """
    Identify Single Points of Failure (SPOF) in the primitive tuple.

    \b
    Example:
        imscribe perturb fault-injection acetic_acid_homodimer --delta-g -12.0
    """
    from imscrbgrmr.perturbation import PerturbationEngine
    try:
        imscription = global_catalog.get(imscription_name)
        if imscription is None:
            console.print(f"[red]Imscription '{imscription_name}' not found.[/red]")
            sys.exit(1)

        engine = PerturbationEngine()
        result = engine.fault_injection(imscription, delta_g)

        if format == "json":
            console.print_json(json.dumps(result, indent=2))
            return

        console.print(f"\n[bold]Fault Injection: {imscription_name}[/bold]")
        console.print(f"  Baseline ξ_CP = [cyan]{result['baseline_xi_CP_nats']:.4f}[/cyan] nats")
        if result["system_robust"]:
            console.print("[green]✓ No single-primitive fault identified. System is robust.[/green]")
        else:
            console.print(f"[red]⚠ {len(result['single_points_of_failure'])} SPOF(s) found:[/red]")
            for spof in result["single_points_of_failure"]:
                console.print(f"  • {spof['primitive']} ({spof['shift']}): Δξ_CP = {spof['delta_xi_CP_nats']:+.4f}  [{spof['sensitivity']}]")
                if spof["axiom_violated"]:
                    console.print(f"    [red]Axiom violation: {spof['axiom_violated']}[/red]")

    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


@perturb.command(name="pathfind")
@click.argument("imscription_name")
@click.option("--target", "-t", type=float, required=True, help="Target ξ_CP (nats).")
@click.option("--optimize", "-o", default=None, help="Comma-separated primitives (e.g. F,K).")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def perturb_pathfind(imscription_name: str, delta_g: float, target: float, optimize: Optional[str], format: str):
    """
    Find minimal primitive changes to reach a target ξ_CP.

    \b
    Example:
        imscribe perturb pathfind acetic_acid_homodimer --delta-g -12.0 --target 6.0 --optimize F,K
    """
    from imscrbgrmr.perturbation import PerturbationEngine
    try:
        imscription = global_catalog.get(imscription_name)
        if imscription is None:
            console.print(f"[red]Imscription '{imscription_name}' not found.[/red]")
            sys.exit(1)

        opt_prims = [p.strip() for p in optimize.split(",")] if optimize else None
        engine = PerturbationEngine()
        result = engine.find_path_to_target(imscription, delta_g, target, opt_prims)

        if format == "json":
            console.print_json(json.dumps(result, indent=2))
            return

        console.print(f"\n[bold]Pathfinder: {imscription_name}[/bold]")
        console.print(f"  Baseline ξ_CP = {result['baseline_xi_CP_nats']:.4f} nats  →  Target < {target} nats")
        if result["target_reached"]:
            console.print(f"[green]✓ Target reached: {result['achieved_xi_CP_nats']:.4f} nats in {result['num_steps']} step(s)[/green]")
        else:
            console.print(f"[yellow]Target not fully reached. Best: {result['achieved_xi_CP_nats']:.4f} nats[/yellow]")
        for i, step in enumerate(result["recommended_steps"], 1):
            console.print(f"  {i}. {step['primitive']} ({step['shift']})  Δξ = {step['delta_xi_CP_nats']:+.4f} nats")

    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


# =============================================================================
# Subcommand group: trajectory
# =============================================================================

@main.group()
def trajectory():
    """Temporal Pathway Encoding — validate D_∞ cycles as step sequences."""
    pass


@trajectory.command(name="validate")
@click.option("--steps", "-s", required=True, help="Comma-separated imscription names (cycle order).")
@click.option("--reset", "-r", default=None, help="Name of the reset step.")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def trajectory_validate(steps: str, reset: Optional[str], format: str):
    """
    Validate continuity and Axiom 6 compliance for a D_∞ cycle.

    \b
    Example:
        imscribe trajectory validate --steps enamine,c_c_bond_form,hydrolysis --reset hydrolysis
    """
    from imscrbgrmr.trajectory import TemporalImscriptionAgent
    try:
        step_names = [s.strip() for s in steps.split(",")]
        agent = TemporalImscriptionAgent("cli_cycle")
        for name in step_names:
            s = global_catalog.get(name)
            if s is None:
                console.print(f"[red]Imscription '{name}' not found in catalog.[/red]")
                sys.exit(1)
            is_reset = (name == reset) or (reset is None and name == step_names[-1])
            agent.add_step(s, step_name=name, is_reset=is_reset)

        result = agent.validate_all()

        if format == "json":
            console.print_json(json.dumps(result.to_dict(), indent=2))
            return

        status_color = "green" if result.overall_valid else "red"
        console.print(f"\n[bold]Trajectory Validation[/bold]")
        console.print(f"  Steps: {result.num_steps}  |  Overall: [{status_color}]{'PASS' if result.overall_valid else 'FAIL'}[/{status_color}]")
        console.print(f"  Axiom 6: {'[green]PASS[/green]' if result.axiom6_satisfied else '[red]FAIL[/red]'}  |  Reset: {result.reset_step or 'NOT FOUND'}")
        if result.kinetic_traps:
            console.print(f"  [yellow]Kinetic traps:[/yellow] {', '.join(result.kinetic_traps)}")

        for c in result.continuity_results:
            icon = "[green]✓[/green]" if c.passed else "[red]✗[/red]"
            console.print(f"  {icon} {c.step_a} → {c.step_b}")
            for issue in c.issues:
                console.print(f"    [red]  {issue}[/red]")
        for w in result.warnings:
            console.print(f"  [yellow]⚠ {w}[/yellow]")

    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


@trajectory.command(name="criticality")
@click.option("--steps", "-s", required=True, help="Comma-separated imscription names.")
@click.option("--varma-probe", is_flag=True, help="Show full Varma probe output.")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def trajectory_criticality(steps: str, varma_probe: bool, format: str):
    """
    Compute G/D degeneracy score per step to determine ⊙ candidacy.

    \b
    Example:
        imscribe trajectory criticality --steps enamine,c_c_bond_form,hydrolysis --varma-probe
    """
    from imscrbgrmr.trajectory import TemporalImscriptionAgent
    try:
        step_names = [s.strip() for s in steps.split(",")]
        agent = TemporalImscriptionAgent("cli_cycle")
        for name in step_names:
            s = global_catalog.get(name)
            if s is None:
                console.print(f"[red]Imscription '{name}' not found in catalog.[/red]")
                sys.exit(1)
            agent.add_step(s, step_name=name)

        crit_results = agent.scan_criticality()

        if format == "json":
            console.print_json(json.dumps([r.to_dict() for r in crit_results], indent=2))
            return

        table = Table(title="Trajectory Criticality Scan")
        table.add_column("Step", style="cyan")
        table.add_column("Degeneracy Score", style="magenta")
        table.add_column("Tier", style="yellow")
        table.add_column("⊙ Candidate", style="green")
        for r in crit_results:
            phi_c = "[green]YES[/green]" if r.is_phi_c_candidate else "no"
            table.add_row(r.step_name, f"{r.degeneracy_score:.3f}", r.tier, phi_c)
        console.print(table)

        full_avg = sum(r.degeneracy_score for r in crit_results) / len(crit_results) if crit_results else 0.0
        console.print(f"\nFull-cycle candidacy score: [cyan]{full_avg:.3f}[/cyan]")

    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


# =============================================================================
# Subcommand group: ensemble
# =============================================================================

@main.group()
def ensemble():
    """Multi-Imscription Composition Verification — emergent axiom and criticality checks."""
    pass


@ensemble.command(name="check")
@click.option("--components", "-c", required=True, help="Comma-separated imscription names.")
@click.option("--pairwise", is_flag=True, default=True, help="Run pairwise compatibility matrix.")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def ensemble_check(components: str, pairwise: bool, format: str):
    """
    Check pairwise compatibility of ensemble components.

    \b
    Example:
        imscribe ensemble check --components axle,wheel,stopper
    """
    from imscrbgrmr.ensembler import EnsembleCatalog
    try:
        names = [n.strip() for n in components.split(",")]
        cat = EnsembleCatalog()
        for name in names:
            cat.add(name)

        report = cat.check_pairwise()

        if format == "json":
            console.print_json(json.dumps(report.to_dict(), indent=2))
            return

        status = "[green]CONSISTENT[/green]" if report.is_consistent else "[red]INCONSISTENT[/red]"
        console.print(f"\n[bold]Ensemble Compatibility: {', '.join(names)}[/bold]")
        console.print(f"  Consistency score: [cyan]{report.consistency_score:.2f}[/cyan]  |  {status}\n")

        for entry in report.pairwise_matrix:
            color = {"Compatible": "green", "Conditional": "yellow", "Incompatible": "red"}.get(entry.result, "white")
            console.print(f"  [{color}]{entry.component_a} ↔ {entry.component_b}: {entry.result}[/{color}]")
            for cond in entry.conditions:
                console.print(f"    [dim]Condition: {cond}[/dim]")

        console.print(f"\n[bold]Axiom Propagation:[/bold]")
        for axiom_name, axiom_status in report.axiom_propagation.items():
            console.print(f"  • {axiom_name}: {axiom_status}")

        for w in report.warnings:
            console.print(f"  [red]⚠ {w}[/red]")

    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


@ensemble.command(name="probe")
@click.option("--components", "-c", required=True, help="Comma-separated imscription names.")
@click.option("--criticality", "check_crit", is_flag=True, help="Probe for emergent criticality.")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def ensemble_probe(components: str, check_crit: bool, format: str):
    """
    Scan for emergent properties arising only in composition.

    \b
    Example:
        imscribe ensemble probe --criticality --components axle,wheel
    """
    from imscrbgrmr.ensembler import EnsembleCatalog
    try:
        names = [n.strip() for n in components.split(",")]
        cat = EnsembleCatalog()
        for name in names:
            cat.add(name)

        report = cat.check_pairwise()

        if format == "json":
            console.print_json(json.dumps([e.to_dict() for e in report.emergent_properties], indent=2))
            return

        console.print(f"\n[bold]Emergent Property Scan: {', '.join(names)}[/bold]\n")
        for ep in report.emergent_properties:
            icon = "[green]✓[/green]" if ep.detected else "[dim]—[/dim]"
            score_str = f" (score: {ep.score:.2f})" if ep.score is not None else ""
            console.print(f"  {icon} {ep.property_name}{score_str}")
            console.print(f"    [dim]{ep.details}[/dim]")

    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


@ensemble.command(name="thermo")
@click.option("--components", "-c", required=True, help="Comma-separated imscription names.")
@click.option("--delta-g-assembly", "-g", type=float, required=True, help="Assembly ΔG (kJ/mol).")
@click.option("--interface-overhead", type=float, default=0.0, show_default=True, help="Interface overhead (bits).")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def ensemble_thermo(components: str, delta_g_assembly: float, interface_overhead: float, format: str):
    """
    Compute system-level η_CP / ξ_CP for the assembly event.

    \b
    Example:
        imscribe ensemble thermo --components axle,wheel --delta-g-assembly -85.0
    """
    from imscrbgrmr.ensembler import EnsembleCatalog
    try:
        names = [n.strip() for n in components.split(",")]
        cat = EnsembleCatalog()
        for name in names:
            cat.add(name)

        result = cat.compute_system_xi_CP(delta_g_assembly, interface_overhead)

        if format == "json":
            console.print_json(json.dumps(result, indent=2))
            return

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return

        console.print(f"\n[bold]Ensemble Thermodynamics[/bold]")
        console.print(f"  Components: {result['num_components']}  |  Ref: {result.get('reference_imscription', '—')}")
        console.print(f"  ΔG_assembly = {result['delta_g_assembly_kJ_mol']} kJ/mol")
        console.print(f"  System η_CP  = [cyan]{result['eta_CP_system']:.2e}[/cyan]")
        console.print(f"  System ξ_CP  = [cyan]{result['xi_CP_system_nats']:.4f}[/cyan] nats  [{result['efficiency_tier']}]")
        if result["interface_overhead_bits"] > 0:
            console.print(f"  Interface overhead = {result['interface_overhead_bits']:.2f} bits")

    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


# Register all commands with the imscribe alias
imscribe_alias.add_command(analyze)
imscribe_alias.add_command(catalog)
imscribe_alias.add_command(generate)
imscribe_alias.add_command(compare)
imscribe_alias.add_command(export)
imscribe_alias.add_command(agents)
imscribe_alias.add_command(criticality)
imscribe_alias.add_command(validate)
imscribe_alias.add_command(isomorphs)
imscribe_alias.add_command(rules)
imscribe_alias.add_command(audit)
imscribe_alias.add_command(reconstruct)
imscribe_alias.add_command(criticality_probe, name="criticality-probe")
imscribe_alias.add_command(cache)
imscribe_alias.add_command(perturb)
imscribe_alias.add_command(trajectory)
imscribe_alias.add_command(ensemble)
# run_syn is defined later in the file; registered below after its definition


# Register new commands with main as well
main.add_command(criticality_probe, name="criticality-probe")
main.add_command(lambda_group, name="lambda")  # λ-engine
main.add_command(nav_group, name="nav")  # navigators


# =============================================================================
# Tuple Algebra: meet, join, path, tensor
# =============================================================================

def _load_imscription_by_name(name: str):
    """Load a imscription from the global catalog by name."""
    from .registry import global_catalog
    s = global_catalog.get(name)
    if s is None:
        click.echo(f"Imscription '{name}' not found in catalog.", err=True)
        raise SystemExit(1)
    return s


@main.command()
@click.argument("imscription_a")
@click.argument("imscription_b")
@click.option("--symmetric/--directed", default=True, show_default=True,
              help="Symmetric (default) or directed quasi-metric d(A→B).")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def distance(imscription_a: str, imscription_b: str, symmetric: bool, format: str):
    """Weighted quasi-metric distance between two imscriptions.

    Symmetric mode returns a Hamming-like score over all ten primitives.
    Directed mode (--directed) penalises only downward moves in F/K —
    matching the HotSwap floor logic (d(A→B) ≠ d(B→A) when fidelity differs).

    Categorical primitives (D, T, R, P, ∈) contribute 1.0 × weight on mismatch.
    Ordinal primitives (F, K, G) contribute the ordinal gap × weight.
    """
    from .algebra import tuple_distance, mahalanobis_distance

    s1 = _load_imscription_by_name(imscription_a)
    s2 = _load_imscription_by_name(imscription_b)
    d_sym = tuple_distance(s1, s2, symmetric=True)
    d_dir = tuple_distance(s1, s2, symmetric=False)
    d_rev = tuple_distance(s2, s1, symmetric=False)
    d_maha = mahalanobis_distance(s1, s2)  # None if catalog unavailable

    if format == "json":
        import json
        payload = {
            "s1": imscription_a,
            "s2": imscription_b,
            "distance_symmetric": round(d_sym, 4),
            "distance_directed_s1_to_s2": round(d_dir, 4),
            "distance_directed_s2_to_s1": round(d_rev, 4),
            "asymmetry": round(abs(d_dir - d_rev), 4),
            "hotswap_favoured": imscription_a if d_rev > d_dir else (imscription_b if d_dir > d_rev else "symmetric"),
        }
        if d_maha is not None:
            payload["distance_mahalanobis"] = round(d_maha, 4)
        click.echo(json.dumps(payload, indent=2))
        return

    click.echo()
    click.echo(f"  Tuple Distance: {imscription_a}  ↔  {imscription_b}")
    click.echo()
    click.echo(f"  d(symmetric)        : {d_sym:.4f}")
    click.echo(f"  d({imscription_a} → {imscription_b})  : {d_dir:.4f}")
    click.echo(f"  d({imscription_b} → {imscription_a})  : {d_rev:.4f}")
    asym = abs(d_dir - d_rev)
    if asym > 0.01:
        cheaper = imscription_a if d_dir < d_rev else imscription_b
        click.echo(f"  Asymmetry           : {asym:.4f}  (HotSwap cheaper from {cheaper})")
    else:
        click.echo(f"  Asymmetry           : ~0  (symmetric pair)")
    if d_maha is not None:
        click.echo(f"  d(Mahalanobis)      : {d_maha:.4f}  [g_ij = Σ⁻¹, §26]")
    click.echo()


@main.command()
@click.argument("imscription_a")
@click.argument("imscription_b")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def meet(imscription_a: str, imscription_b: str, format: str):
    """Lattice MEET (⊓): greatest lower bound of two imscriptions.

    Returns the most general imscription that is a structural sub-type of both.
    Useful for retrosynthesis: the meet gives the minimal common precursor motif.

    Ordered primitives (F, K, G) take the minimum (more conservative).
    Categorical primitives (D, T, R, P, ∈) require exact match; mismatches
    are reported as CONFLICT — the meet is a partial sub-imscription in that case.
    """
    from .algebra import meet as _meet

    s1 = _load_imscription_by_name(imscription_a)
    s2 = _load_imscription_by_name(imscription_b)
    result = _meet(s1, s2)

    if format == "json":
        import json
        def _ser(x):
            if x == "CONFLICT":
                return "CONFLICT"
            if hasattr(x, "value"):
                return x.value
            if hasattr(x, "operator"):
                return f"{x.operator.value}({x.tier})"
            return str(x) if x is not None else None
        click.echo(json.dumps({
            "operation": "meet",
            "s1": imscription_a, "s2": imscription_b,
            "result": result.to_notation(),
            "valid": result.is_valid,
            "conflicts": result.conflicts,
            "notes": result.notes,
            "primitives": {
                "D": _ser(result.dimensionality),
                "T": _ser(result.topology),
                "R": _ser(result.recognition_mode),
                "P": _ser(result.polarity),
                "F": _ser(result.fidelity),
                "K": _ser(result.kinetic_character),
                "G": _ser(result.granularity),
                "Gamma": _ser(result.interaction_grammar),
                "Phi": _ser(result.criticality_phase),
                "S": result.stoichiometry,
                "Omega": _ser(getattr(result, "topo_index", None)),
            },
        }, indent=2))
        return

    click.echo()
    click.echo("Lattice Meet  s1 ⊓ s2")
    click.echo(f"  s1  : {imscription_a}")
    click.echo(f"  s2  : {imscription_b}")
    click.echo()
    click.echo(f"  Result  : {result.to_notation()}")
    click.echo(f"  Valid   : {'✓ fully defined' if result.is_valid else '✗ partial (conflicts present)'}")
    if result.conflicts:
        click.echo(f"  Conflicts ({len(result.conflicts)}): {', '.join(result.conflicts)}")
    if result.notes:
        click.echo()
        click.echo("  Ordered-primitive resolutions:")
        for n in result.notes:
            click.echo(f"    • {n}")
    click.echo()


@main.command()
@click.argument("imscription_a")
@click.argument("imscription_b")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def join(imscription_a: str, imscription_b: str, format: str):
    """Lattice JOIN (⊔): least upper bound of two imscriptions.

    Returns the most demanding imscription that both can be upgraded to.
    Useful for co-assembly design: the join gives the specification a
    unified scaffold must satisfy to host both components simultaneously.

    Ordered primitives (F, K, G) take the maximum (more permissive).
    Categorical conflicts are reported the same way as in 'meet'.
    """
    from .algebra import join as _join

    s1 = _load_imscription_by_name(imscription_a)
    s2 = _load_imscription_by_name(imscription_b)
    result = _join(s1, s2)

    if format == "json":
        import json
        def _ser(x):
            if x == "CONFLICT":
                return "CONFLICT"
            if hasattr(x, "value"):
                return x.value
            if hasattr(x, "operator"):
                return f"{x.operator.value}({x.tier})"
            return str(x) if x is not None else None
        click.echo(json.dumps({
            "operation": "join",
            "s1": imscription_a, "s2": imscription_b,
            "result": result.to_notation(),
            "valid": result.is_valid,
            "conflicts": result.conflicts,
            "notes": result.notes,
        }, indent=2))
        return

    click.echo()
    click.echo("Lattice Join  s1 ⊔ s2")
    click.echo(f"  s1  : {imscription_a}")
    click.echo(f"  s2  : {imscription_b}")
    click.echo()
    click.echo(f"  Result  : {result.to_notation()}")
    click.echo(f"  Valid   : {'✓ fully defined' if result.is_valid else '✗ partial (conflicts present)'}")
    if result.conflicts:
        click.echo(f"  Conflicts ({len(result.conflicts)}): {', '.join(result.conflicts)}")
        click.echo("    ⊤ (top) substituted for conflicting categorical primitives.")
        click.echo("    No single registered imscription satisfies the join — a new design target.")
    if result.notes:
        click.echo()
        click.echo("  Ordered-primitive resolutions:")
        for n in result.notes:
            click.echo(f"    • {n}")
    click.echo()


@main.command()
@click.argument("source")
@click.argument("destination")
@click.option("--max-hops", "-n", type=int, default=6, show_default=True,
              help="Maximum number of HotSwap hops to search.")
@click.option("--xi-tolerance", type=float, default=1.0, show_default=True,
              help="Per-hop |Δξ_CP| budget (nats).")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def path(source: str, destination: str, max_hops: int, xi_tolerance: float, format: str):
    """Shortest valid HotSwap path from SOURCE to DESTINATION through the catalog.

    Finds the minimum-hop sequence of valid swaps connecting two imscriptions.
    Path search is restricted to imscriptions sharing the same D and T (the hard
    structural constraints of HotSwap), so the valid-swap graph is sparse.

    Edge weight = |Δξ_CP| per hop.  The algorithm is BFS (minimum hops);
    within equal hop-count, the path with smallest total |Δξ| is preferred.
    """
    from .algebra import find_path
    from .registry import global_catalog

    s_src = _load_imscription_by_name(source)
    s_dst = _load_imscription_by_name(destination)
    imscriptions = list(global_catalog)

    result = find_path(s_src, s_dst, imscriptions, max_hops=max_hops, xi_tolerance=xi_tolerance)

    if format == "json":
        import json
        click.echo(json.dumps({
            "found": result.found,
            "source": source,
            "destination": destination,
            "n_hops": result.n_hops if result.found else None,
            "path": result.path,
            "hop_deltas_nats": [round(x, 4) for x in result.hop_deltas],
            "total_delta_nats": round(result.total_delta, 4) if result.found else None,
            "notes": result.notes,
        }, indent=2))
        return

    click.echo()
    click.echo("HotSwap Path Search")
    click.echo(f"  Source       : {source}")
    click.echo(f"  Destination  : {destination}")
    click.echo(f"  Max hops     : {max_hops}  |  ξ tolerance : {xi_tolerance} nat/hop")
    click.echo()

    if not result.found:
        click.echo("  Result: NO PATH FOUND")
        for n in result.notes:
            click.echo(f"  {n}")
    else:
        click.echo(f"  Result: PATH FOUND  ({result.n_hops} hop{'s' if result.n_hops != 1 else ''},"
                   f" total |Δξ| = {result.total_delta:.3f} nats)")
        click.echo()
        for i, name in enumerate(result.path):
            if i == 0:
                click.echo(f"  [{i}] {name}  (source)")
            elif i == len(result.path) - 1:
                delta = result.hop_deltas[i - 1]
                click.echo(f"  [{i}] {name}  (destination)  Δξ = {delta:+.3f} nat")
            else:
                delta = result.hop_deltas[i - 1]
                click.echo(f"  [{i}] {name}  Δξ = {delta:+.3f} nat")
    click.echo()


@main.command()
@click.argument("imscription_a")
@click.argument("imscription_b")
@click.option("--lambda", "lambda_", type=float, default=0.3, show_default=True,
              help="Mutual-information discount factor λ in ξ = ξ₁ + ξ₂ − λ·I(s₁;s₂).")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def tensor(imscription_a: str, imscription_b: str, lambda_: float, format: str):
    """Tensor product s1 ⊗ s2: predicts the primitive profile of their ensemble.

    Computes the expected primitive tuple of the co-assembly or co-crystal
    formed by combining s1 and s2.  Rules:

    \b
      D  →  union (hybrid if different)
      T  →  topology promotion (cage > network > hub > bowtie)
      F  →  min (bottleneck fidelity)
      K  →  min (kinetic trap propagates)
      G  →  max (coarsest scale dominates)
      <  →  ⊙ propagates (criticality is join-dominant)
      ξ  →  ξ₁ + ξ₂ − λ·I(s₁;s₂)   (λ tunable; I from primitive overlap)
    """
    from .algebra import tensor as _tensor

    s1 = _load_imscription_by_name(imscription_a)
    s2 = _load_imscription_by_name(imscription_b)
    try:
        result = _tensor(s1, s2)
    except ValueError as e:
        click.echo(f"\n  Tensor undefined: {e}", err=True)
        raise SystemExit(1)

    if format == "json":
        import json
        def _ser(x):
            if x is None:
                return None
            if hasattr(x, "value"):
                return x.value
            return str(x)
        click.echo(json.dumps({
            "operation": "tensor",
            "s1": imscription_a, "s2": imscription_b,
            "result_notation": result.to_notation(),
            "primitives": {
                "D": _ser(result.dimensionality),
                "T": _ser(result.topology),
                "R": _ser(result.recognition_mode),
                "P": _ser(result.polarity),
                "F": _ser(result.fidelity),
                "K": _ser(result.kinetic_character),
                "G": _ser(result.granularity),
                "Gamma": _ser(result.grammar),
                "Phi": _ser(result.criticality_phase),
                "H": _ser(result.chirality),
                "S": _ser(result.stoichiometry),
                "Omega": _ser(result.protection),
            },
        }, indent=2))
        return

    def _v(x):
        if x is None:
            return "—"
        if hasattr(x, "value"):
            return x.value
        return str(x)

    click.echo()
    click.echo("Tensor Product  s1 ⊗ s2")
    click.echo(f"  s1  : {imscription_a}")
    click.echo(f"  s2  : {imscription_b}")
    click.echo()
    click.echo(f"  Result: {result.to_notation()}")
    click.echo()
    click.echo("  Primitives:")
    rows = [
        ("D", result.dimensionality),
        ("T", result.topology),
        ("R", result.recognition_mode),
        ("P", result.polarity),
        ("F", result.fidelity),
        ("K", result.kinetic_character),
        ("G", result.granularity),
        ("∈", result.grammar),
        ("≺", result.criticality_phase),
        ("H", result.chirality),
        ("S", result.stoichiometry),
        ("◻", result.protection),
    ]
    for prim, val in rows:
        click.echo(f"    {prim:4s} {_v(val)}")
    click.echo()


@main.command()
@click.argument("imscription_name")
@click.argument("target", type=click.Choice(["temporal", "spatial", "critical", "molecular"]))
@click.option("--strength", type=float, default=0.70, show_default=True,
              help="Provisional degeneracy_strength for criticality lift.")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def lift(imscription_name: str, target: str, strength: float, format: str):
    """Apply a natural transformation (dimensional lift) to a imscription.

    \b
    Targets:
      temporal  — D_∧/D_△ → D_∞  (static recognition → catalytic cycle)
      spatial   — D_∧     → D_△  (molecular → supramolecular spatial array)
      critical  — 𐑢   → ⊙  (inject criticality; requires F ≥ F_ℏ)
      molecular — any     → D_∧  (forgetful projection, loses spatial/temporal)

    The lift is structural only.  The resulting imscription requires Axiom grounding
    before it can be registered.  All lifts preserve the naturality condition:
    if A → B is a valid HotSwap, then lift(A) → lift(B) is also valid.
    """
    from .algebra import _LIFT_MAP

    s = _load_imscription_by_name(imscription_name)
    fn = _LIFT_MAP[target]
    if target in ("critical", "criticality"):
        result = fn(s, strength=strength)
    else:
        result = fn(s)

    if format == "json":
        import json
        def _ser(x):
            if x is None:
                return None
            if hasattr(x, "operator") and hasattr(x, "tier"):
                return f"{x.operator.value}({x.tier})"
            if hasattr(x, "value"):
                return x.value
            return str(x)
        out = {
            "source": imscription_name,
            "lift_type": target,
            "applicable": result.applicable,
            "notes": result.notes,
            "warnings": result.warnings,
        }
        if result.imscription:
            s2 = result.imscription
            out["result"] = {
                "name": s2.name,
                "D": _ser(s2.dimensionality),
                "T": _ser(s2.topology),
                "R": _ser(s2.recognition_mode),
                "P": _ser(s2.polarity),
                "F": _ser(s2.fidelity),
                "K": _ser(s2.kinetic_character),
                "G": _ser(s2.granularity),
                "Gamma": _ser(s2.interaction_grammar),
                "Phi": _ser(s2.criticality_phase),
                "notation": s2.to_notation(),
            }
        click.echo(json.dumps(out, indent=2))
        return

    click.echo()
    click.echo(f"Natural Transformation: lift → {target}")
    click.echo(f"  Source    : {imscription_name}")
    click.echo(f"  Applicable: {'✓' if result.applicable else '✗'}")
    click.echo()

    if not result.applicable:
        for n in result.notes:
            click.echo(f"  {n}")
        click.echo()
        return

    s2 = result.imscription
    click.echo(f"  Result    : {s2.name}")
    click.echo(f"  Notation  : {s2.to_notation()}")
    click.echo()

    # Side-by-side diff
    def _v(x):
        if x is None: return "—"
        if hasattr(x, "operator") and hasattr(x, "tier"):
            return f"{x.operator.value}({x.tier})"
        if hasattr(x, "value"): return x.value
        return str(x)

    rows = [
        ("D", s.dimensionality, s2.dimensionality),
        ("T", s.topology, s2.topology),
        ("R", s.recognition_mode, s2.recognition_mode),
        ("P", s.polarity, s2.polarity),
        ("F", s.fidelity, s2.fidelity),
        ("K", s.kinetic_character, s2.kinetic_character),
        ("G", s.granularity, s2.granularity),
        ("∈", s.interaction_grammar, s2.interaction_grammar),
        ("≺", s.criticality_phase, s2.criticality_phase),
    ]
    click.echo("  Primitive changes:")
    any_change = False
    for prim, v_old, v_new in rows:
        vo, vn = _v(v_old), _v(v_new)
        if vo != vn:
            click.echo(f"    {prim:4s}  {vo}  →  {vn}")
            any_change = True
    if not any_change:
        click.echo("    (no primitive changes)")

    click.echo()
    if result.notes:
        click.echo("  Notes:")
        for n in result.notes:
            click.echo(f"    • {n}")
    if result.warnings:
        click.echo()
        click.echo("  Warnings:")
        for w in result.warnings:
            click.echo(f"    ⚠  {w}")
    click.echo()


@main.command("pipeline")
@click.argument("start_imscription")
@click.option("--step", "-s", "steps", multiple=True,
              help=(
                  "Pipeline step: 'op:arg' or 'op:arg:opt=val'. "
                  "op ∈ {meet, join, tensor, lift, path}. "
                  "Examples: meet:adenine_thymine_pair  lift:temporal  "
                  "tensor:nitroso_radical_redox_imscription_pair:lambda=0.2  "
                  "path:proline_aldol_cycle:max_hops=5"
              ))
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def pipeline(start_imscription: str, steps, format: str):
    """Chain algebra operations into a composable design pipeline.

    Implements Writer + Maybe monad semantics: each step threads ξ_CP
    deltas and warnings automatically; the pipeline short-circuits on the
    first blocking failure.

    \b
    Step syntax:  op:arg[:key=val]
      meet:imscription          — lattice meet with imscription
      join:imscription          — lattice join with imscription
      tensor:imscription        — tensor product (opt: lambda=0.3)
      lift:TARGET           — natural transformation (temporal|spatial|critical|molecular)
                              opt: strength=0.70 (criticality lift only)
      path:TARGET           — shortest HotSwap path to TARGET
                              opt: max_hops=6, xi_tol=1.0

    \b
    Example:
      imscribe pipeline carboxylic_acid_dimer \\
        --step meet:adenine_thymine_pair \\
        --step lift:temporal \\
        --step path:proline_aldol_cycle
    """
    from .algebra import DesignPipeline, _LIFT_MAP
    from .registry import global_catalog

    def _get(name):
        s = global_catalog.get(name)
        if s is None:
            click.echo(f"Imscription '{name}' not found in catalog.", err=True)
            raise SystemExit(1)
        return s

    src = _get(start_imscription)
    pip = DesignPipeline.start(src)
    catalog = list(global_catalog)

    for raw_step in steps:
        parts = raw_step.split(":")
        op = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        # Parse optional key=val options from remaining parts
        opts: dict = {}
        for p in parts[2:]:
            if "=" in p:
                k, v = p.split("=", 1)
                try:
                    opts[k] = float(v)
                except ValueError:
                    opts[k] = v

        if op == "meet":
            pip = pip.meet(_get(arg))
        elif op == "join":
            pip = pip.join(_get(arg))
        elif op == "tensor":
            pip = pip.tensor(_get(arg))
        elif op == "lift":
            kw = {}
            if "strength" in opts:
                kw["strength"] = float(opts["strength"])
            pip = pip.lift(arg, **kw)
        elif op == "path":
            max_hops = int(opts.get("max_hops", 6))
            xi_tol = float(opts.get("xi_tol", 1.0))
            pip = pip.path(_get(arg), catalog,
                           max_hops=max_hops, xi_tolerance=xi_tol)
        else:
            click.echo(f"Unknown pipeline op '{op}'. "
                       f"Valid: meet, join, tensor, lift, path", err=True)
            raise SystemExit(1)

    result = pip.result()

    if format == "json":
        import json
        def _ser(x):
            if x is None: return None
            if hasattr(x, "operator") and hasattr(x, "tier"):
                return f"{x.operator.value}({x.tier})"
            if hasattr(x, "value"): return x.value
            return str(x)
        out = {
            "start": start_imscription,
            "status": "FAILED" if result.failed else "SUCCESS",
            "failed_at": result.failed_at or None,
            "failure_reason": result.failure_reason or None,
            "total_xi_delta": round(result.total_xi_delta, 4),
            "final_imscription": result.value.name if result.value else None,
            "steps": [
                {
                    "op": s.op,
                    "input": s.input_name,
                    "output": s.output_name,
                    "delta_xi": round(s.delta_xi, 4) if s.delta_xi is not None else None,
                    "notes": s.notes,
                    "warnings": s.warnings,
                    "blocked": s.blocked,
                    "block_reason": s.block_reason or None,
                }
                for s in result.steps
            ],
        }
        click.echo(json.dumps(out, indent=2))
        return

    # Text output — delegate to PipelineResult.print_trace()
    result.print_trace()


# =============================================================================
# Subcommand: run  (Phase 3a — .syn DSL evaluator)
# =============================================================================

@main.command("run")
@click.argument("script", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option("--format", "-f", "fmt",
              type=click.Choice(["text", "json"]), default=None,
              help="Override output format (text or json).")
@click.option("--save", "-s", "save_path", default=None,
              help="Save JSON result to this file path.")
@click.option("--dry-run", "dry_run", is_flag=True, default=False,
              help="Parse and validate without executing.")
def run_syn(script: str, fmt: Optional[str], save_path: Optional[str], dry_run: bool):
    """
    Run a .syn design script as a typed ImscriptionM pipeline.

    SCRIPT is a path to a .syn YAML design program.

    \b
    Step ops supported in do: block:
      join:   <name>         — algebra.join → ImscriptionM
      meet:   <name>         — algebra.meet → ImscriptionM
      tensor: <name>         — algebra.tensor → ImscriptionM
        lambda: <float>      (default 0.3)
      lift:   <target>       — lift_* → ImscriptionM
      path:   <name>         — find_path → ImscriptionM
        xi_tolerance: <float> (default 2.0)
        max_hops: <int>       (default 6)
      assert:                — inline proof obligation
        expr: phi_c_score > 0.70
        message: "label"
      bind:   <strategy>     — invoke a named strategies: block

    \b
    Example:
      imscribe run design.syn
      imscribe run design.syn --format json --save result.json
      imscribe run design.syn --dry-run
    """
    from .syn_runner import SynScript, SynParseError

    # ── Parse ────────────────────────────────────────────────────────────
    try:
        script_obj = SynScript.from_file(script)
    except SynParseError as e:
        console.print(f"[bold red]Parse error:[/bold red] {e}")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[bold red]Error loading {script}:[/bold red] {e}")
        raise SystemExit(1)

    # apply overrides
    if fmt:
        script_obj.output_format = fmt
    if save_path:
        script_obj.save_path = save_path

    out_fmt = script_obj.output_format

    # ── Dry-run: validate only ────────────────────────────────────────────
    if dry_run:
        warnings_list = script_obj.validate()
        do_steps = script_obj._raw.get("do") or []
        if warnings_list:
            console.print(f"[bold yellow]Validation warnings:[/bold yellow]")
            for w in warnings_list:
                console.print(f"  ⚠  {w}")
            raise SystemExit(1)
        console.print(
            f"[bold green]✓ Dry-run OK[/bold green]  "
            f"start=[cyan]{script_obj.start_name}[/cyan]  "
            f"steps={len(do_steps)}"
        )
        return

    # ── Execute ───────────────────────────────────────────────────────────
    script_name = Path(script).name
    result = script_obj.run()

    # ── Output: JSON ──────────────────────────────────────────────────────
    if out_fmt == "json":
        data = result.to_dict()
        data["script"] = script_name
        data["start"] = script_obj.start_name
        json_str = json.dumps(data, indent=2)
        if script_obj.save_path:
            Path(script_obj.save_path).write_text(json_str, encoding="utf-8")
            console.print(f"[green]Saved to {script_obj.save_path}[/green]")
        else:
            console.print(json_str)
        return

    # ── Output: text ──────────────────────────────────────────────────────
    console.print(f"\n[bold]Imscribing Grammar Run:[/bold] {script_name}")
    console.print(f"  Start: [cyan]{script_obj.start_name}[/cyan]\n")
    from imscrbgrmr.monad import StepRecord as _SR
    _icons = {
        "PASS": "✓", "ASSERT_PASS": "✓",
        "BLOCKED": "✗", "ASSERT_FAIL": "✗",
        "ERROR": "!", "MZERO": "·",
    }
    _colors = {
        "PASS": "green", "ASSERT_PASS": "green",
        "BLOCKED": "red", "ASSERT_FAIL": "yellow",
        "ERROR": "bold red", "MZERO": "dim",
    }
    fail_at: Optional[int] = None
    for i, step in enumerate(result.log, 1):
        icon = _icons.get(step.status, "?")
        col = _colors.get(step.status, "white")
        xi_str = f"  Δξ={step.delta_xi:+.3f} nat" if step.delta_xi != 0.0 else ""
        arg_str = f"({step.arg})" if step.arg else ""
        line = (
            f"  {i}. [{step.status}] {icon} "
            f"{step.op}{arg_str}{xi_str}  — {step.message}"
        )
        console.print(f"[{col}]{line}[/{col}]")
        if fail_at is None and step.status in ("BLOCKED", "ERROR", "ASSERT_FAIL"):
            fail_at = i

    status_str = "[bold green]SUCCESS[/bold green]" if result.is_success() else "[bold red]FAILED[/bold red]"
    fail_note = f"  |  FAILED at step {fail_at}" if fail_at is not None else ""
    console.print(
        f"\n  Total Δξ_CP: {result.cost:+.3f} nat  |  "
        f"Steps: {len(result.log)}  |  {status_str}{fail_note}"
    )

    if result.is_success():
        name = getattr(result.value, "name", str(result.value))
        console.print(f"  Result: [cyan]{name}[/cyan]")

    # ── Save JSON even in text mode if --save requested ───────────────────
    if script_obj.save_path:
        data = result.to_dict()
        data["script"] = script_name
        data["start"] = script_obj.start_name
        Path(script_obj.save_path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        console.print(f"\n[dim]Saved JSON to {script_obj.save_path}[/dim]")


# Register run_syn with the imscribe alias (must be after run_syn is defined above)
imscribe_alias.add_command(run_syn, name="run")  # Phase 3a — .syn DSL runner

# Register tuple-algebra commands with imscribe_alias (meet/join/path/tensor/lift/pipeline
# were decorated with @main.command but never wired into the imscribe entrypoint)
imscribe_alias.add_command(distance)
imscribe_alias.add_command(meet)
imscribe_alias.add_command(join)
imscribe_alias.add_command(path)
imscribe_alias.add_command(tensor)
imscribe_alias.add_command(lift)
imscribe_alias.add_command(pipeline)


# ---------------------------------------------------------------------------
# imscribe phase-diagram — tuple-space phase transition detector (v0.4.0)
# ---------------------------------------------------------------------------

@main.command("phase-diagram")
@click.argument("names", nargs=-1, required=False)
@click.option("--save", default=None, help="Save plot to this path (PNG/PDF/SVG).")
@click.option("--text-only", is_flag=True, default=False,
              help="Print text report only; skip matplotlib rendering.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text",
              help="Output format for the phase boundary table.")
@click.option("--metric", type=click.Choice(["diagonal", "mahalanobis"]), default="diagonal",
              help="Distance metric: diagonal (v0.4.26 default) or mahalanobis (g=Σ⁻¹, §26).")
def phase_diagram_cmd(names, save, text_only, fmt, metric):
    """
    Compute tuple-space phase diagram for NAMES (defaults to 8 quantum imscriptions).

    Detects phase boundaries as large jumps in pairwise tuple distance.
    Renders a two-panel plot: Ward dendrogram + MDS 2-D phase map.

    Annotations:
      ★  Factor-8 quantum criticality fingerprint (G_ℵ + F_ℏ + K_teshlig + ¬D_∞)
      ○  K_teshlig ring (candidate for K_teshlig→K_lambda +2.303 nat transition)
      ◻  Colour-coded topological protection class

    \b
    Examples:
      imscribe phase-diagram
      imscribe phase-diagram spin_singlet kitaev_chain_majorana fqh_moore_read
      imscribe phase-diagram --save phase_map.png --metric mahalanobis
      imscribe phase-diagram --format json
    """
    import json as json_mod
    from .phase_diagram import build_phase_map

    name_list = list(names) if names else None
    try:
        pd = build_phase_map(imscription_names=name_list, metric=metric)
    except KeyError as e:
        click.echo(f"[ERROR] Imscription not found: {e}", err=True)
        raise SystemExit(1)

    if fmt == "json":
        click.echo(json_mod.dumps(pd.to_dict(), indent=2))
        return

    # Text report
    pd.print_report()

    if not text_only:
        show = save is None   # show interactively only if not saving to file
        pd.plot(save_path=save, show=show)
        if save:
            click.echo(f"Phase diagram saved to: {save}")


imscribe_alias.add_command(phase_diagram_cmd, name="phase-diagram")


# =============================================================================
# Subcommand: tool  — single-shot ImscribeTool dispatch
# =============================================================================

@main.command("tool")
@click.argument("operation", type=click.Choice([
    "validate", "criticality", "path", "isomorphs", "distance", "meet", "generate",
]))
@click.option("--name",        "-n",  default=None,  help="Catalog entry name (validate, criticality, isomorphs).")
@click.option("--src",         "-s",  default=None,  help="Source entry (path).")
@click.option("--dst",         "-d",  default=None,  help="Destination entry (path).")
@click.option("--a",                  default=None,  help="First entry (distance, meet).")
@click.option("--b",                  default=None,  help="Second entry (distance, meet).")
@click.option("--description", "-D",  default=None,  help="Natural-language description (generate).")
@click.option("--xi-r",               default=None,  type=float, help="Spatial correlation length (criticality).")
@click.option("--xi-tau",             default=None,  type=float, help="Temporal correlation length (criticality).")
@click.option("--limit",       "-l",  default=5,     type=int,   help="Max isomorphs to return (default 5).")
@click.option("--max-hops",    "-m",  default=6,     type=int,   help="Max HotSwap hops for path (default 6).")
@click.option("--provider",    "-p",  default=None,  envvar="IG_PROVIDER", help="LLM provider (env: IG_PROVIDER). E.g. deepseek, qwen, anthropic, mistral.")
@click.option("--model",              default=None,  envvar="IG_MODEL",    help="Model ID (env: IG_MODEL). Uses provider default if unset.")
@click.option("--format",      "-f",  type=click.Choice(["text", "json"]), default="text")
def tool_cmd(operation, name, src, dst, a, b, description, xi_r, xi_tau,
             limit, max_hops, delta_g, provider, model, format):
    """
    Single-shot ImscribeTool dispatch — LLM tool layer from the command line.

    Validates, probes, or composes imscriptions using the real Python API.
    Every operation returns a structured result; axiom violations are shown
    with a precise trace.

    \\b
    Examples:
        imscribe tool validate --name allosteric_domain
        imscribe tool criticality --name allosteric_domain --xi-r 8.5 --xi-tau 1e10
        imscribe tool path --src allosteric_domain --dst active_site
        imscribe tool isomorphs --name condensate_liquid --limit 5
        imscribe tool distance --a allosteric_domain --b active_site
        imscribe tool meet --a condensate_liquid --b condensate_gel
        imscribe tool generate --description "bivalent allosteric ABL inhibitor"
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from imscribe_tool import IGTool as ImscribeTool

    kwargs = {}
    if name:        kwargs["name"]        = name
    if src:         kwargs["src"]         = src
    if dst:         kwargs["dst"]         = dst
    if a:           kwargs["a"]           = a
    if b:           kwargs["b"]           = b
    if description: kwargs["description"] = description
    if xi_r:        kwargs["xi_r"]        = xi_r
    if xi_tau:      kwargs["xi_tau"]      = xi_tau
    if limit != 5:  kwargs["limit"]       = limit
    if max_hops != 6: kwargs["max_hops"]  = max_hops
    if delta_g:     kwargs["delta_g"]     = delta_g
    if provider:    kwargs["provider"]    = provider
    if model:       kwargs["model"]       = model

    result = ImscribeTool.dispatch(operation, **kwargs)

    if format == "json":
        click.echo(result.to_json())
        return

    # Rich text output
    status_color = {"ok": "green", "violation": "red", "blocked": "yellow", "error": "red"}.get(result.status, "white")
    console.print(f"\n[{status_color}]● {result.status.upper()}[/{status_color}]  operation={operation}")

    if result.notation:
        console.print(f"[cyan]Notation:[/cyan] {result.notation}")
    if result.phi_c_score is not None:
        console.print(f"[cyan]⊙ score:[/cyan] {result.phi_c_score:.3f}  ({result.phi_c_label})")
    if result.distance is not None:
        console.print(f"[cyan]Distance:[/cyan] {result.distance:.3f}")
    if result.path:
        console.print(f"[cyan]Path ({result.path_hops} hops, Δξ={result.path_delta_xi:.3f}):[/cyan]")
        for step in result.path:
            console.print(f"  → {step}")
    if result.analogs:
        console.print(f"[cyan]Analogs:[/cyan]")
        for a_entry in result.analogs:
            console.print(f"  d={a_entry['distance']:.3f}  {a_entry['name']}")
    if result.axiom_report:
        console.print(f"[cyan]Axiom report:[/cyan]")
        for k, v in result.axiom_report.items():
            console.print(f"  {k}: {v}")
    for note in result.notes:
        console.print(f"[dim]{note}[/dim]")
    if result.error:
        console.print(f"[red]Error:[/red] {result.error}")


# =============================================================================
# Subcommand: design  — autonomous LLM design agent loop
# =============================================================================

@main.command("design")
@click.argument("goal")
@click.option("--target",          "-t",  default=None,  help="Catalog entry to path toward (optional).")
@click.option("--phi-c-min",              default=0.65,  type=float, show_default=True,
              help="Minimum ⊙ score for convergence.")
@click.option("--xi-cp-max",              default=14.0,  type=float, show_default=True,
              help="Maximum ξ_CP (nats) for convergence.")
@click.option("--max-iterations", "-i",  default=8,     type=int,   show_default=True,
              help="Maximum design iterations.")
@click.option("--provider",        "-p",  default=None, required=True, envvar="IG_PROVIDER",
              help="LLM provider — required (env: IG_PROVIDER). E.g. deepseek, qwen, anthropic, mistral, google/gemini. Requires {PROVIDER}_API_KEY in env.")
@click.option("--model",          "-m",  default=None, envvar="IG_MODEL",
              help="Model ID (env: IG_MODEL). Uses provider default if unset.")
@click.option("--quiet",          "-q",  is_flag=True,
              help="Suppress per-iteration output; print final result only.")
@click.option("--output",         "-o",  default=None,
              help="Save full iteration history to JSON file.")
def design_cmd(goal, target, phi_c_min, xi_cp_max, max_iterations, provider, model, quiet, output):
    """
    Autonomous relational design agent — LLM-in-the-loop structural optimization.

    Proposes 12-primitive encodings for any system type, validates them against
    the axiom set, probes ⊙ candidacy and ξ_CP efficiency, finds cross-domain
    analogs, and self-corrects until the convergence criteria are met.

    \\b
    Convergence: ⊙ score ≥ --phi-c-min AND ξ_CP ≤ --xi-cp-max.
    With --target, a HotSwap path to that catalog entry is also required.

    \\b
    Examples:
        imscribe design "self-modeling recursive system at criticality"
        imscribe design "topologically protected language grammar" --phi-c-min 0.70
        imscribe design "adversarial archetype maximizing irreversibility" --target סַמָּאֵל
        imscribe design "near-critical condensate at phase boundary" --target ising_3d
        imscribe design "..." --quiet --output result.json
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from imscribe_agent import run_design, _OPENAI_BASE_URLS

    # Provider-aware model defaults
    _PROVIDER_DEFAULT_MODELS = {
        "anthropic": "claude-sonnet-4-6",
        "deepseek":  "deepseek-chat",
        "openai":    "gpt-4o",
        "qwen":      "qwen-max",
        "mistral":   "mistral-large-latest",
        "google":    "gemini-2.0-flash",
        "gemini":    "gemini-2.0-flash",
    }
    resolved_model = model or _PROVIDER_DEFAULT_MODELS.get(provider, "deepseek-chat")

    console.print(Panel(
        f"[bold cyan]Imscription Design Agent[/bold cyan]\n"
        f"Goal: {goal}\n"
        f"Criteria: ⊙ ≥ {phi_c_min}  ·  ξ_CP ≤ {xi_cp_max} nats"
        + (f"  ·  path→{target}" if target else ""),
        border_style="cyan",
    ))

    history = run_design(
        goal=goal,
        target=target,
        phi_c_min=phi_c_min,
        xi_cp_max=xi_cp_max,
        max_iterations=max_iterations,
        model=resolved_model,
        provider=provider,
        verbose=not quiet,
    )

    # Always print convergence summary
    console.print()
    table = Table(title="Design History", show_header=True, header_style="bold magenta")
    table.add_column("iter", style="dim", width=4)
    table.add_column("axioms", width=6)
    table.add_column("⊙", width=6)
    table.add_column("ξ_CP", width=7)
    table.add_column("status")

    for r in history:
        ax = "✅" if r.axioms_passed else "❌"
        phi = f"{r.phi_c_score:.3f}" if r.phi_c_score is not None else "—"
        xi  = f"{r.xi_cp:.2f}"       if r.xi_cp is not None else "—"
        status = "[green]CONVERGED[/green]" if r.converged else (r.stop_reason or "iterating")
        table.add_row(str(r.iteration), ax, phi, xi, status)

    console.print(table)

    converged = any(r.converged for r in history)
    if converged:
        final = next(r for r in reversed(history) if r.converged)
        console.print(f"\n[green]✅ Converged[/green]  {final.stop_reason}")
        if final.notation:
            console.print(f"[cyan]Final notation:[/cyan] {final.notation}")
    else:
        console.print("\n[yellow]⚠  Max iterations reached without convergence.[/yellow]")

    if output:
        import json as _json
        out = [
            {
                "iteration": r.iteration,
                "axioms_passed": r.axioms_passed,
                "phi_c_score": r.phi_c_score,
                "xi_cp": r.xi_cp,
                "notation": r.notation,
                "converged": r.converged,
                "stop_reason": r.stop_reason,
                "n_tool_calls": len(r.tool_calls),
            }
            for r in history
        ]
        Path(output).write_text(_json.dumps(out, indent=2))
        console.print(f"[dim]History saved → {output}[/dim]")


imscribe_alias.add_command(tool_cmd, name="tool")
imscribe_alias.add_command(design_cmd, name="design")


# ── imscribe remove ──────────────────────────────────────────────────────────────

@main.command("remove")
@click.argument("names", nargs=-1, required=True)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def remove_cmd(names: tuple, yes: bool):
    """Remove one or more imscriptions from the catalog by name.

    \b
    Examples:
        imscribe remove junk_imscription_1 junk_imscription_2
        imscribe remove imscription_foo --yes
    """
    from imscrbgrmr.registry import global_catalog

    missing = [n for n in names if global_catalog.get(n) is None]
    found   = [n for n in names if global_catalog.get(n) is not None]

    if missing:
        for n in missing:
            console.print(f"[yellow]⚠  Not found:[/yellow] {n}")
    if not found:
        console.print("[red]Nothing to remove.[/red]")
        raise SystemExit(1)

    if not yes:
        console.print(f"\n[bold]About to remove {len(found)} imscription(s):[/bold]")
        for n in found:
            console.print(f"  • {n}")
        click.confirm("\nContinue?", abort=True)

    removed, failed = [], []
    for n in found:
        if global_catalog.remove(n):
            removed.append(n)
        else:
            failed.append(n)

    for n in removed:
        console.print(f"[green]✓ Removed:[/green] {n}")
    for n in failed:
        console.print(f"[red]✗ Failed:[/red]  {n}")

    console.print(f"\n[bold]Catalog now has {len(global_catalog)} imscription(s).[/bold]")


imscribe_alias.add_command(remove_cmd, name="remove")


# ─────────────────────────────────────────────────────────────────────────────
# imscribe transition  — phase transition morphism (Kleisli arrow)
# ─────────────────────────────────────────────────────────────────────────────

@main.command("transition")
@click.argument("src_name")
@click.argument("dst_name")
@click.option("--max-hops", default=6, show_default=True,
              help="Maximum BFS hops for path search.")
@click.option("--xi-tolerance", default=1.0, show_default=True,
              help="Per-hop |Δξ_CP| budget (nats).")
def transition_cmd(src_name: str, dst_name: str, max_hops: int, xi_tolerance: float):
    """Classify the phase transition between two catalog imscriptions.

    \b
    Encodes the transition as a Kleisli arrow in the HotSwap monad:
      • 2nd order — direct HotSwap path through ⊙ intermediates
      • 1st order — no path (D/T or F structural conflict)

    Reports forward/reverse costs and irreversibility asymmetry.

    \b
    Examples:
        imscribe transition condensate_liquid condensate_gel
        imscribe transition alpha_helix beta_hairpin
    """
    from imscrbgrmr.registry import global_catalog
    from imscrbgrmr.morphism import find_transition, TransitionOrder

    src = global_catalog.get(src_name)
    dst = global_catalog.get(dst_name)

    if src is None:
        console.print(f"[red]Not found:[/red] {src_name}")
        raise SystemExit(1)
    if dst is None:
        console.print(f"[red]Not found:[/red] {dst_name}")
        raise SystemExit(1)

    catalog = list(global_catalog._imscriptions.values())
    morph = find_transition(src, dst, catalog,
                            max_hops=max_hops, xi_tolerance=xi_tolerance)

    # Header
    order_colour = {
        TransitionOrder.SECOND:  "green",
        TransitionOrder.FIRST:   "red",
        TransitionOrder.UNKNOWN: "yellow",
    }[morph.order]
    order_label = {
        TransitionOrder.SECOND:  "2nd-order (continuous)",
        TransitionOrder.FIRST:   "1st-order (discontinuous)",
        TransitionOrder.UNKNOWN: "order unknown",
    }[morph.order]

    console.print(f"\n[bold]Transition morphism:[/bold]  "
                  f"[cyan]{src_name}[/cyan] → [cyan]{dst_name}[/cyan]")
    console.print(f"  Order: [{order_colour}]{order_label}[/{order_colour}]")

    import math
    fwd_str = f"{morph.forward_cost:.3f} nat" if math.isfinite(morph.forward_cost) else "∞"
    rev_str = f"{morph.reverse_cost:.3f} nat" if math.isfinite(morph.reverse_cost) else "∞"
    console.print(f"  Forward cost : {fwd_str}")
    console.print(f"  Reverse cost : {rev_str}")
    console.print(f"  Asymmetry    : {morph.asymmetry:.3f}  "
                  f"({'reversible' if morph.is_reversible else 'irreversible'})")

    if morph.phi_c_intermediates:
        console.print(f"  ⊙ intermediates: "
                      f"[magenta]{', '.join(morph.phi_c_intermediates)}[/magenta]")

    if morph.is_quantum_critical:
        qcp = morph.quantum_critical_point
        console.print(f"  [bold yellow]⚛  Quantum critical point detected[/bold yellow]")
        console.print(f"     QCP imscription(s): {', '.join(qcp.qcp_imscription_names)}")
        for h in qcp.universality_hints:
            console.print(f"     {h}")

    # Morphism-level ⊙ score
    from imscrbgrmr.varma_probe import score_transition_phi_c
    phi_report = score_transition_phi_c(morph)
    phi_label = phi_report._candidacy_label()
    phi_colour = (
        "green" if phi_report.score >= 0.70
        else "yellow" if phi_report.score >= 0.40
        else "red"
    )
    console.print(
        f"\n  [bold]Morphism ⊙ score:[/bold]  "
        f"[{phi_colour}]{phi_report.score:.3f}/1.000  —  {phi_label}[/{phi_colour}]"
    )
    if phi_report.universality_class:
        console.print(f"  Universality class: {phi_report.universality_class}")
    if phi_report.gd_degeneracy_type == "morphism_qcp":
        console.print(
            "  [dim](Exact morphism-level predicate — "
            "path-through-⊙ is more reliable than Factor 8 endpoint heuristic)[/dim]"
        )
    if phi_report.flags:
        for f in phi_report.flags:
            console.print(f"  [yellow]⚠  {f}[/yellow]")

    # Forward path
    if morph.forward_path.found:
        hops = " → ".join(morph.forward_path.path)
        console.print(f"\n  [bold]Forward path ({len(morph.forward_path.path)-1} hops):[/bold]")
        console.print(f"    {hops}")
    else:
        console.print(f"\n  [bold]Forward path:[/bold] [red]no path[/red]")
        for n in morph.forward_path.notes:
            console.print(f"    {n}")

    # Reverse path
    if morph.reverse_path.found:
        hops = " → ".join(morph.reverse_path.path)
        console.print(f"  [bold]Reverse path ({len(morph.reverse_path.path)-1} hops):[/bold]")
        console.print(f"    {hops}")
    else:
        console.print(f"  [bold]Reverse path:[/bold] [red]no path[/red]")

    # Notes
    if morph.notes:
        console.print("\n  [bold]Notes:[/bold]")
        for n in morph.notes:
            console.print(f"    • {n}")


imscribe_alias.add_command(transition_cmd, name="transition")


# ── Decomposition algebra commands ─────────────────────────────────────────────

@main.command()
@click.argument("imscription")
@click.argument("primitives", nargs=-1, required=True)
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def project(imscription: str, primitives: tuple, format: str):
    """Project a imscription onto a subset of named primitives (zero all others).

    PRIMITIVES is one or more field names: F K G D T R P Phi Omega Gamma

    \b
    Example:
      imscribe project allosteric_domain F K G Phi
    """
    from .decompose import project as _project
    s = _load_imscription_by_name(imscription)
    r = _project(s, list(primitives))
    if format == "json":
        import json
        click.echo(json.dumps({
            "imscription": imscription,
            "projected_primitives": list(primitives),
            "zeroed": r.zeroed,
            "result": r.result.to_notation() if r.result else None,
            "notes": r.notes,
        }, indent=2))
        return
    click.echo()
    click.echo(f"  project({imscription}, [{', '.join(primitives)}])")
    click.echo()
    if r.zeroed:
        click.echo(f"  Zeroed  : {', '.join(r.zeroed)}")
    click.echo(f"  Result  : {r.result.to_notation() if r.result else 'None'}")
    for n in r.notes:
        click.echo(f"  Note    : {n}")
    click.echo()


@main.command()
@click.argument("imscription")
@click.argument("primitive")
@click.option("--strict", is_flag=True, default=False,
              help="Block peel if it would destroy ⊙ (phase protection).")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def peel(imscription: str, primitive: str, strict: bool, format: str):
    """Descend one tier on a single primitive (peel one layer off).

    Returns the resulting imscription and any peel cost (in nats).
    Use --strict to block the peel if it would destroy a critical phase (⊙).

    \b
    Example:
      imscribe peel condensate_liquid Phi --strict
      imscribe peel allosteric_domain F
    """
    from .decompose import primitive_peel as _peel
    s = _load_imscription_by_name(imscription)
    r = _peel(s, primitive, strict=strict)
    if format == "json":
        import json
        click.echo(json.dumps({
            "imscription": imscription,
            "primitive": primitive,
            "strict": strict,
            "blocked": r.blocked,
            "block_reason": r.block_reason,
            "peel_cost": r.peel_cost,
            "result": r.result.to_notation() if r.result else None,
            "notes": r.notes,
        }, indent=2))
        return
    click.echo()
    click.echo(f"  peel({imscription}, {primitive}{'  [strict]' if strict else ''})")
    click.echo()
    if r.blocked:
        click.echo(f"  BLOCKED : {r.block_reason}")
    else:
        click.echo(f"  Cost    : {r.peel_cost:.3f} nats")
        click.echo(f"  Result  : {r.result.to_notation() if r.result else 'None (already at floor)'}")
        for n in r.notes:
            click.echo(f"  Note    : {n}")
    click.echo()


@main.command()
@click.argument("imscription")
@click.option("--prefer", "-p", default=None,
              help="Preferred primitive to factor on first (e.g. F, K, G).")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def factor(imscription: str, prefer: str, format: str):
    """Find the strongest meet-irreducible factor of a imscription.

    Returns the sub-imscription that best characterises the dominant structure.
    Use --prefer to bias the factoring toward a specific primitive.

    \b
    Example:
      imscribe factor quantum_gravity --prefer K
      imscribe factor allosteric_domain
    """
    from .decompose import factor as _factor
    s = _load_imscription_by_name(imscription)
    r = _factor(s, prefer=prefer)
    if format == "json":
        import json
        click.echo(json.dumps({
            "imscription": imscription,
            "prefer": prefer,
            "stepped_primitive": r.stepped_primitive,
            "result": r.result.to_notation() if r.result else None,
            "notes": r.notes,
        }, indent=2))
        return
    click.echo()
    click.echo(f"  factor({imscription}{'  prefer=' + prefer if prefer else ''})")
    click.echo()
    if r.stepped_primitive == "none":
        click.echo("  Irreducible — imscription is already a join-irreducible atom.")
    else:
        click.echo(f"  Stepped on : {r.stepped_primitive}")
        click.echo(f"  Result     : {r.result.to_notation() if r.result else 'None'}")
    for n in r.notes:
        click.echo(f"  Note       : {n}")
    click.echo()


@main.command("principal-decomp")
@click.argument("imscription")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def principal_decomp_cmd(imscription: str, format: str):
    """Recursively factor a imscription down to its join-irreducible atoms.

    The principal decomposition reveals the minimal building-block atoms
    that, when joined, reproduce the full imscription structure.

    \b
    Example:
      imscribe principal-decomp standard_model
      imscribe principal-decomp quantum_gravity
    """
    from .decompose import principal_decomp as _pd
    s = _load_imscription_by_name(imscription)
    r = _pd(s)
    if format == "json":
        import json
        click.echo(json.dumps({
            "imscription": imscription,
            "n_factors": r.n_factors,
            "factors": [a.to_notation() if hasattr(a, "to_notation") else str(a) for a in r.factors],
            "notes": r.notes,
        }, indent=2))
        return
    click.echo()
    click.echo(f"  principal_decomp({imscription})")
    click.echo(f"  Factors ({r.n_factors}):")
    for i, a in enumerate(r.factors, 1):
        click.echo(f"    [{i}] {a.to_notation() if hasattr(a, 'to_notation') else a}")
    for n in r.notes:
        click.echo(f"  Note : {n}")
    click.echo()


@main.command()
@click.argument("composite")
@click.argument("factor_a")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def cofactor(composite: str, factor_a: str, format: str):
    """Compute the cofactor residual B such that FACTOR_A ⊗ B ≈ COMPOSITE.

    Per-primitive roles: CONTRIBUTOR (B must supply), BOTTLENECK (B is
    the limiting factor), CONFLICT (irreconcilable mismatch), EXPLAINED
    (fully covered by FACTOR_A), PASSTHROUGH (categorical mismatch, passed).

    \b
    Example:
      imscribe cofactor quantum_gravity general_relativity
      imscribe cofactor ads_cft_boundary general_relativity
      imscribe cofactor allosteric_domain gnf_2
    """
    from .decompose import cofactor as _cofactor
    c = _load_imscription_by_name(composite)
    a = _load_imscription_by_name(factor_a)
    r = _cofactor(c, a)
    if format == "json":
        import json
        click.echo(json.dumps({
            "composite": composite,
            "factor_a": factor_a,
            "blocked": r.blocked,
            "conflict_primitives": r.conflict_primitives,
            "contributor_primitives": [d.primitive for d in r.dimensions if d.role == "CONTRIBUTOR"],
            "result": r.result.to_notation() if r.result else None,
            "dimensions": [
                {"primitive": d.primitive, "role": d.role,
                 "factor_val": str(d.factor_val), "composite_val": str(d.composite_val)}
                for d in r.dimensions
            ],
            "notes": r.notes,
        }, indent=2))
        return
    click.echo()
    click.echo(f"  cofactor({composite}, {factor_a})")
    click.echo()
    if r.conflict_primitives:
        click.echo(f"  CONFLICTS : {', '.join(r.conflict_primitives)}")
    contributors = [d.primitive for d in r.dimensions if d.role == "CONTRIBUTOR"]
    bottlenecks  = [d.primitive for d in r.dimensions if d.role == "BOTTLENECK"]
    if contributors:
        click.echo(f"  B supplies: {', '.join(contributors)}")
    if bottlenecks:
        click.echo(f"  Bottleneck: {', '.join(bottlenecks)}")
    click.echo()
    click.echo(f"  {'Primitive':<8}  {'Role':<15}  {'factor_a':25}  composite")
    click.echo(f"  {'─'*8}  {'─'*15}  {'─'*25}  {'─'*25}")
    for d in r.dimensions:
        click.echo(f"  {d.primitive:<8}  {d.role:<15}  {str(d.factor_val):25}  {str(d.composite_val)}")
    click.echo()
    if r.result:
        click.echo(f"  Residual B : {r.result.to_notation()}")
    else:
        click.echo("  Residual B : None (blocked — irreconcilable conflicts)")
    for n in r.notes:
        click.echo(f"  Note       : {n}")
    click.echo()


# Register decomposition commands with imscribe alias
imscribe_alias.add_command(project)          # DECOMPOSE_PROJECT
imscribe_alias.add_command(peel)             # DECOMPOSE_PEEL
imscribe_alias.add_command(factor)           # DECOMPOSE_FACTOR
imscribe_alias.add_command(principal_decomp_cmd, name="principal-decomp")  # DECOMPOSE_PD
imscribe_alias.add_command(cofactor)         # DECOMPOSE_COFACTOR


# =============================================================================
# Subcommand: frobenius-tier  — Frobenius ouroboricity classification
# =============================================================================

def _frobenius_classify(s) -> str:
    """Apply R1–R5 to classify a Imscription into its Frobenius tier."""
    phi   = s.criticality_phase.value
    p     = s.polarity.value
    omega = s.protection.value
    d     = s.dimensionality.value
    # Phi_closerevepsilon has identical tier distribution to ⊙ (real vs complex is inner-crystal only)
    at_c  = phi in ("⊙_ctyogh", "⊙_closerevepsilon")
    # R1: exact proved Z₂ symmetry at criticality → special Frobenius
    if at_c and p == "<_doublebarpipe":
        return "O_∞"
    # R2: no self-referential loop possible (Phi_revepsilon absorbs O_∞ under tensor → O₀ own tier)
    if phi in ("⊙_softsign", "⊙_upstep", "⊙_revepsilon"):
        return "O₀"
    # R3: critical but no topological protection
    if at_c and omega == "𐑷":
        return "O₁"
    # R4: critical + topological + bounded domain (D_turnthree → D_cube in enum)
    if at_c and omega != "𐑷" and d in ("𐑛", "𐑦", "𐑨"):
        return "O₂"
    # R5: critical + topological + unbounded domain
    if at_c and omega != "𐑷" and d == "𐑼":
        return "O₂†"
    return "O₀"


_FROBENIUS_TIER_DESC = {
    "O_∞":   "Special Frobenius — exact proved Z₂ symmetry at criticality (μ∘δ=id).",
    "O₀":     "No ouroboricity — cannot form a self-referential critical loop.",
    "O₁":     "Ouroboricity tier 1 — critical, no topological protection.",
    "O₂":     "Ouroboricity tier 2 — critical + topologically protected, bounded domain.",
    "O₂†": "Ouroboricity tier 2† — critical + topologically protected, unbounded (D_invomega) domain.",
}


@main.command("ouroborics")
@click.argument("imscription", default="__all__", required=False)
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def frobenius_tier_cmd(imscription: str, format: str):
    """Classify a imscription (or the whole catalog) into its Frobenius ouroboricity tier.

    Tiers: O_∞ / O₀ / O₁ / O₂ / O₂†

    \b
    Rules (applied in priority order):
      R1: ⊙ + P_doublebarpipe            → O_∞  (special Frobenius, exact Z₂ symmetry)
      R2: Phi_softsign or Phi_upstep          → O₀   (no self-referential loop)
      R3: ⊙ + Omega_closeepsilon             → O₁   (critical, unprotected)
      R4: ⊙ + Omega≠0 + D_bounded → O₂   (critical, protected, bounded)
      R5: ⊙ + Omega≠0 + D_invomega   → O₂†  (critical, protected, unbounded)

    \b
    Examples:
      imscribe ouroborics ising_3d
      imscribe ouroborics allosteric_domain
      imscribe ouroborics                      (census of whole catalog)
      imscribe ouroborics __all__ --format json
    """
    import json as _json
    from .registry import global_catalog

    if imscription == "__all__":
        all_imscriptions = global_catalog.search()
        counts = {"O_∞": 0, "O₀": 0, "O₁": 0, "O₂": 0, "O₂†": 0}
        by_tier: Dict[str, list] = {k: [] for k in counts}
        for s in all_imscriptions:
            tier = _frobenius_classify(s)
            counts[tier] += 1
            by_tier[tier].append(s.name)
        total = sum(counts.values())

        if format == "json":
            click.echo(_json.dumps({
                "census": "full catalog",
                "total": total,
                "summary": {t: {"count": c, "pct": round(100 * c / total, 1) if total else 0}
                            for t, c in counts.items()},
                "O_inf_entries": sorted(by_tier["O_∞"]),
            }, indent=2))
            return

        click.echo()
        click.echo("  Frobenius tier census — full catalog")
        click.echo(f"  Total: {total}")
        click.echo()
        tier_order = ["O_∞", "O₂†", "O₂", "O₁", "O₀"]
        for t in tier_order:
            c = counts[t]
            pct = round(100 * c / total, 1) if total else 0
            label = t.replace("O₂†", "O₂†")
            click.echo(f"  {label:<8}  {c:>4}  ({pct:.1f}%)")
        if by_tier["O_∞"]:
            click.echo()
            click.echo(f"  O_∞ entries ({counts['O_∞']}):")
            for name in sorted(by_tier["O_∞"]):
                click.echo(f"    • {name}")
        click.echo()
        return

    s = global_catalog.get(imscription)
    if s is None:
        click.echo(f"Imscription '{imscription}' not found in catalog.", err=True)
        raise SystemExit(1)

    tier = _frobenius_classify(s)

    if format == "json":
        click.echo(_json.dumps({
            "name": imscription,
            "frobenius_tier": tier,
            "Phi": s.criticality_phase.value,
            "P": s.polarity.value,
            "Omega": s.protection.value,
            "D": s.dimensionality.value,
            "interpretation": _FROBENIUS_TIER_DESC[tier],
        }, indent=2))
        return

    click.echo()
    click.echo(f"  ouroborics({imscription})")
    click.echo()
    tier_label = tier.replace("O₂†", "O₂†")
    click.echo(f"  Tier    : {tier_label}")
    click.echo(f"  Phi     : {s.criticality_phase.value}")
    click.echo(f"  P       : {s.polarity.value}")
    click.echo(f"  Omega   : {s.protection.value}")
    click.echo(f"  D       : {s.dimensionality.value}")
    click.echo(f"  Meaning : {_FROBENIUS_TIER_DESC[tier]}")
    click.echo()


imscribe_alias.add_command(frobenius_tier_cmd, name="ouroborics")  # OUROBORICS
imscribe_alias.add_command(lambda_group, name="lambda")  # λ-engine
imscribe_alias.add_command(nav_group, name="nav")  # navigators


# ── vocal imscription ──────────────────────────────────────────────────────────

@main.command("vocal")
@click.argument("name", required=False, default=None)
@click.option("--output", "-o", default=None,
              help="Output WAV path (default: <name>_imscription.wav in cwd).")
@click.option("--gap", default=120, show_default=True,
              help="Silence gap between primitives in ms.")
@click.option("--play", is_flag=True, default=False,
              help="Play the imscription immediately via ffplay after saving.")
@click.option("--sounds-dir", default=None,
              help="Override path to vocal_sounds/ directory.")
@click.option("--explain", is_flag=True, default=False,
              help="Print pronunciation guide for the entry's 12 primitives.")
@click.option("--guide", is_flag=True, default=False,
              help="Print the full 49-symbol pronunciation reference and exit.")
def vocal_cmd(name: Optional[str], output: Optional[str], gap: int, play: bool,
              sounds_dir: Optional[str], explain: bool, guide: bool):
    """Render the 12-primitive tuple of a catalog entry as a vocal imscription WAV.

    \b
    Examples:
        imscribe vocal psychedelic_baseline
        imscribe vocal magnetar --play --explain
        imscribe vocal carboxylic_acid_dimer --output /tmp/cad.wav --gap 80
        imscribe vocal --guide          # full pronunciation reference
    """
    from imscrbgrmr.vocal import (
        make_imscription, save_wav, _SOUNDS_DIR,
        PRONUNCIATION_GUIDES, PRIMITIVE_ORDER,
    )
    import subprocess

    # ── full guide mode ───────────────────────────────────────────────────────
    if guide:
        _print_full_guide(PRONUNCIATION_GUIDES, PRIMITIVE_ORDER)
        return

    if not name:
        console.print("[red]Provide a catalog entry name, or use --guide for the reference.[/red]")
        raise SystemExit(1)

    # ── load entry from IG_catalog.json ───────────────────────────────────────
    catalog_path = _PROJECT_ROOT / "IG_catalog.json"
    if not catalog_path.exists():
        console.print("[red]IG_catalog.json not found.[/red]")
        raise SystemExit(1)

    with open(catalog_path) as f:
        catalog: list[dict] = json.load(f)

    entry = next((e for e in catalog if e.get("name") == name), None)
    if entry is None:
        lower = name.lower()
        matches = [e for e in catalog if e.get("name", "").lower().startswith(lower)]
        if len(matches) == 1:
            entry = matches[0]
            console.print(f"[dim]Matched: {entry['name']}[/dim]")
        elif len(matches) > 1:
            console.print(f"[yellow]Ambiguous prefix '{name}'. Matches:[/yellow]")
            for m in matches[:8]:
                console.print(f"  {m['name']}")
            raise SystemExit(1)
        else:
            console.print(f"[red]No catalog entry named '{name}'.[/red]")
            raise SystemExit(1)

    # ── explain mode (print before generating) ───────────────────────────────
    if explain:
        console.print(f"\n[bold]{entry['name']}[/bold] — vocal imscription\n")
        t = Table(show_header=True, header_style="bold dim", box=None, padding=(0, 1))
        t.add_column("#",     style="dim",    min_width=2)
        t.add_column("Prim",  style="cyan",   min_width=6, no_wrap=True)
        t.add_column("Value", style="yellow", min_width=24, no_wrap=True)
        t.add_column("IPA",   style="green",  min_width=6, no_wrap=True)
        t.add_column("Sounds like", style="white")
        for i, prim in enumerate(PRIMITIVE_ORDER, 1):
            value = entry.get(prim, "—")
            if value == "—":
                continue
            g = PRONUNCIATION_GUIDES.get(value)
            if g:
                ipa, hint, _detail = g
                t.add_row(str(i), prim, value, ipa, hint)
            else:
                t.add_row(str(i), prim, value, "?", "—")
        console.print(t)
        console.print()

    # ── generate ──────────────────────────────────────────────────────────────
    sdir = Path(sounds_dir) if sounds_dir else _SOUNDS_DIR
    try:
        samples, sr = make_imscription(entry, sounds_dir=sdir, gap_ms=gap)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1)

    out_path = Path(output) if output else Path(f"{entry['name']}_imscription.wav")
    save_wav(samples, sr, out_path)

    duration_s = len(samples) / sr
    console.print(
        f"[green]✓[/green] {entry['name']} → [bold]{out_path}[/bold]  "
        f"({duration_s:.1f}s, {sr} Hz)"
    )

    if play:
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(out_path)],
            check=False,
        )


def _print_full_guide(guides: dict, primitive_order: list[str]) -> None:
    """Print the complete 49-symbol pronunciation reference."""
    from imscrbgrmr.vocal import PRONUNCIATION_GUIDES as _G  # local import to avoid circular

    primitive_of: dict[str, str] = {}
    for prim in primitive_order:
        for key in guides:
            if key.startswith(prim + "_") or key == prim:
                primitive_of[key] = prim

    current_prim = None
    for key, (ipa, hint, detail) in guides.items():
        prim = primitive_of.get(key, "?")
        if prim != current_prim:
            console.print(f"\n[bold cyan]{prim}[/bold cyan]")
            current_prim = prim
        console.print(
            f"  [yellow]{key:30s}[/yellow]  [green]{ipa:8s}[/green]  "
            f"[white]{hint}[/white]\n"
            f"    [dim]{detail}[/dim]"
        )
    console.print()


imscribe_alias.add_command(vocal_cmd, name="vocal")


# =============================================================================
# PROOF-PATH — find and translate a proof path between two imscriptions
# =============================================================================

@main.command("proof-path")
@click.argument("source")
@click.argument("target")
@click.option("--translate/--no-translate", default=True,
              help="Generate LLM proof sketch (default: on).")
@click.option("--full-proof/--no-full-proof", default=False,
              help="Expand sketch to a full LaTeX proof + Lean4 skeleton (default: off).")
@click.option("--compile/--no-compile", "compile_pdf", default=False,
              help="Run lualatex twice on the generated .tex to produce a PDF (default: off).")
@click.option("--model", default="google/gemini-2.5-flash-preview", show_default=True,
              help="OpenRouter model for proof sketch and full proof.")
@click.option("--max-steps", default=12, show_default=True,
              help="Maximum number of operation steps in the path.")
@click.pass_context
def proof_path_cmd(
    ctx, source: str, target: str,
    translate: bool, full_proof: bool, compile_pdf: bool,
    model: str, max_steps: int,
):
    """Find the operation path from SOURCE imscription to TARGET and translate it.

    SOURCE and TARGET must be names of catalog entries.

    \b
    Examples:
      imscribe proof-path hodge_conjecture lefschetz_1_1_theorem
      imscribe proof-path hodge_conjecture lefschetz_1_1_theorem --full-proof
      imscribe proof-path hodge_conjecture lefschetz_1_1_theorem --full-proof --compile
      imscribe proof-path hodge_conjecture lefschetz_1_1_theorem --no-translate
    """
    from imscrbgrmr.proof_path import find_path, generate_lean_skeleton, generate_full_proof, compile_latex
    from imscrbgrmr.proof_path.translator import (
        format_path_display, translate_path, _get_client, _TRANSCRIPT_DIR,
    )

    # Resolve catalog entries for descriptions
    catalog_path = _PROJECT_ROOT / "IG_catalog.json"
    with open(catalog_path) as f:
        raw = json.load(f)
    entries = raw if isinstance(raw, list) else raw.get("entries", [])
    by_name = {e["name"]: e for e in entries}

    if source not in by_name:
        console.print(f"[red]Source '{source}' not found in catalog.[/red]")
        raise SystemExit(1)
    if target not in by_name:
        console.print(f"[red]Target '{target}' not found in catalog.[/red]")
        raise SystemExit(1)

    src_desc = by_name[source].get("description", "")
    tgt_desc = by_name[target].get("description", "")

    console.print(f"\n[bold]Searching for proof path…[/bold]")
    console.print(f"  Source: [cyan]{source}[/cyan] — {src_desc[:70]}")
    console.print(f"  Target: [cyan]{target}[/cyan] — {tgt_desc[:70]}\n")

    steps = find_path(source, target, max_steps=max_steps)

    if steps is None:
        console.print(f"[red]No proof path found within {max_steps} steps.[/red]")
        raise SystemExit(1)

    if not steps:
        console.print("[green]Source and target are identical — no path needed.[/green]")
        return

    console.print(format_path_display(steps, source, target))

    sketch: str | None = None

    if translate:
        console.print("[bold]Generating proof sketch…[/bold]\n")
        try:
            sketch = translate_path(
                steps,
                source_name=source,
                source_desc=src_desc,
                target_name=target,
                target_desc=tgt_desc,
                model=model,
            )
        except Exception as exc:
            console.print(f"[red]Sketch failed: {exc}[/red]")

    if full_proof:
        # Always generate the Lean4 skeleton (deterministic — no LLM needed)
        console.print("\n[bold]Generating Lean4 skeleton…[/bold]")
        lean = generate_lean_skeleton(steps, source, target)

        # Full LaTeX proof requires the sketch as context
        latex: str | None = None
        if sketch:
            console.print("[bold]Generating full proof (LaTeX)…[/bold]\n")
            try:
                client = _get_client()
                latex = generate_full_proof(
                    steps=steps,
                    source_name=source,
                    source_desc=src_desc,
                    target_name=target,
                    target_desc=tgt_desc,
                    sketch=sketch,
                    client=client,
                    model=model,
                )
            except Exception as exc:
                console.print(f"[red]Full proof generation failed: {exc}[/red]")
        else:
            console.print(
                "[yellow]Skipping LaTeX proof — sketch required (run without --no-translate).[/yellow]"
            )

        # Write artifacts to proof_transcripts/
        import datetime
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        slug = f"{source}___{target}".replace(" ", "_")
        base = _TRANSCRIPT_DIR / f"{ts}_{slug}"
        _TRANSCRIPT_DIR.mkdir(exist_ok=True)

        lean_path = Path(f"{base}.lean")
        lean_path.write_text(lean, encoding="utf-8")
        console.print(f"[green]Lean4 skeleton:[/green] {lean_path}")

        if latex:
            tex_path = Path(f"{base}.tex")
            tex_path.write_text(latex, encoding="utf-8")
            console.print(f"[green]LaTeX proof:  [/green] {tex_path}")

            if compile_pdf:
                console.print("[bold]Compiling PDF (2 passes)…[/bold]")
                try:
                    from imscrbgrmr.proof_path.writer import compile_latex
                    pdf_path = compile_latex(tex_path)
                    console.print(f"[green]PDF:          [/green] {pdf_path}")
                except Exception as exc:
                    console.print(f"[red]Compile failed: {exc}[/red]")
        elif compile_pdf:
            console.print("[yellow]--compile requires --full-proof and a successful sketch.[/yellow]")


imscribe_alias.add_command(proof_path_cmd, name="proof-path")


if __name__ == "__main__":
    main()
