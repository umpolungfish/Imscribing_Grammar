#!/usr/bin/env python3
"""
manuscript_eval.py — Universal Manuscript REPL  [v1.0.0]

Interactive navigator for the Voynich, Rohonc, and Linear A manuscript engines.
Backed by manuscript_zfct.json (313 elements × 3 corpora).

Commands:
  <corpus> <id>              show element imscription + ZFCₜ expression
  :dist <a> <b>              distance between any two elements
  :near <element> [N]        N nearest neighbors across all corpora
  :corpus <name>             corpus-level crystal imscription + stats
  :ig_bridge                 4×4 cross-corpus distance matrix
  :section <corpus>          section topology breakdown
  :find <prim>=<val>         find elements with a specific primitive value
  :list <corpus>             list all elements in a corpus
  :run <file>                run a .ms program file
  :programs                  list available .ms programs
  :help                      show this text
  :quit / :q                 exit

Element addressing:
  voynich:f1r  or just  f1r    (if unambiguous)
  rohonc:p1    or just  p1
  linear_a:t40 or just  t40
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import readline
except ImportError:
    pass

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None  # type: ignore[assignment]

# ── paths ──────────────────────────────────────────────────────────────────────

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "manuscript_zfct.json"
PROGRAMS_DIR = HERE / "manuscript_programs"

# ── corpus metadata ────────────────────────────────────────────────────────────

CORPUS_BASE = {
    'voynich': {
        '⊢':'𐑦','⊣':'𐑸','>':'𐑾','<':'𐑹',
        '⋈':'⋈^ì','⊤':'⊤^Ù','∈':'𐑲','∋':'∋^Ş',
        '⊙':'⊙','⊥':'𐑫','⊞':'𐑙','◻':'𐑭',
    },
    'rohonc': {
        '⊢':'𐑨','⊣':'𐑶','>':'𐑽','<':'𐑹',
        '⋈':'⋈^ì','⊤':'⊤^@','∈':'𐑲','∋':'∋^ˌ',
        '⊙':'⊙','⊥':'𐑖','⊞':'𐑳','◻':'𐑭',
    },
    'linear_a': {
        '⊢':'𐑨','⊣':'𐑶','>':'𐑽','<':'𐑹',
        '⋈':'⋈^ż','⊤':'⊤^W','∈':'𐑲','∋':'∋^ˌ',
        '⊙':'⊙','⊥':'𐑖','⊞':'𐑳','◻':'𐑭',
    },
}

CORPUS_LABELS = {
    'voynich':  'Voynich Manuscript   (Beinecke MS 408)',
    'rohonc':   'Rohonc Codex         (Oct. Hung. 73)',
    'linear_a': 'Linear A             (GORILA corpus)',
}

CORPUS_TIER = {
    'voynich':  'O_∞  (C=0.0 — kinetically frozen)',
    'rohonc':   'O_∞  (C=0.0 — equilibrium)',
    'linear_a': 'O_∞  (d=0.00 with OS imscription)',
}

CORPUS_PREFIXES = {'voynich': 'f', 'rohonc': 'p', 'linear_a': 't'}

SECTIONS = {
    'voynich': [
        ('cosmological', ['f68r1','f68r2','f68r3','f69r','f69v','f70r','f70v']),
        ('botanical',    ['f1r','f1v','f2r','f2v','f3r','f3v','f4r','f4v']),
        ('biological',   ['f75r','f75v','f76r','f76v','f77r','f77v','f78r','f78v']),
        ('balneological',['f103r','f103v','f104r','f104v']),
    ],
    'rohonc': [
        ('liturgical',    ['p1','p2','p3','p4','p5']),
        ('pictographic',  ['p51','p52','p53','p54','p55']),
        ('astronomical',  ['p151','p152','p153']),
        ('mixed',         ['p301','p302','p303']),
    ],
    'linear_a': [
        ('haghia_triada',  ['t1','t2','t3','t4','t5']),
        ('knossos',        ['t40','t41','t42','t43','t44']),
        ('zakros',         ['t80','t81','t82','t83','t84']),
        ('other_palatial', ['t120','t121','t122','t123','t124']),
    ],
}

IG_KEYS   = ['⊢','⊣','>','<','⋈','⊤','∈','∋','⊙','⊥','⊞','◻']
IG_WEIGHTS = [10000, 10000, 10000, 12000, 9000, 8000, 10000, 10000, 11000, 8000, 10000, 7000]

CORPUS_COLORS = {'voynich': 'cyan', 'rohonc': 'green', 'linear_a': 'gold1'}

# ── load data ──────────────────────────────────────────────────────────────────

def _load_data() -> dict:
    if not DATA_FILE.exists():
        _err(f"manuscript_zfct.json not found at {DATA_FILE}\n"
             f"Run:  uv run manuscript_zfct.py --all --out manuscript_zfct")
        sys.exit(1)
    with open(DATA_FILE) as f:
        return json.load(f)


DB: dict = {}


def _ensure_db():
    global DB
    if not DB:
        DB = _load_data()

# ── distance ───────────────────────────────────────────────────────────────────

def _ig_dist(ta: dict, tb: dict) -> tuple[float, list[str]]:
    conflicts, d2 = [], 0.0
    for i, k in enumerate(IG_KEYS):
        if ta.get(k) != tb.get(k):
            conflicts.append(k)
            d2 += IG_WEIGHTS[i]
    return math.sqrt(d2) / 1000, conflicts

# ── element resolution ─────────────────────────────────────────────────────────

def _resolve(ref: str) -> Optional[tuple[str, str, dict]]:
    """Return (corpus, element_id, entry) or None."""
    _ensure_db()
    if ':' in ref:
        corpus, eid = ref.split(':', 1)
        corpus = corpus.lower()
    else:
        eid = ref
        corpus = None
        for c, els in DB.items():
            if eid in els:
                if corpus is not None:
                    _warn(f"'{eid}' exists in multiple corpora — prefix with corpus:id")
                    return None
                corpus = c
        if corpus is None:
            _warn(f"Element '{eid}' not found in any corpus.")
            return None

    if corpus not in DB:
        _warn(f"Unknown corpus '{corpus}'. Choose: voynich, rohonc, linear_a")
        return None
    if eid not in DB[corpus]:
        _warn(f"Element '{eid}' not found in corpus '{corpus}'.")
        return None
    return corpus, eid, DB[corpus][eid]

# ── output helpers ─────────────────────────────────────────────────────────────

def _out(msg: str = ''):
    if HAS_RICH:
        console.print(msg)
    else:
        print(msg)


def _warn(msg: str):
    if HAS_RICH:
        console.print(f"[yellow]  ⚠  {msg}[/yellow]")
    else:
        print(f"  ⚠  {msg}")


def _err(msg: str):
    if HAS_RICH:
        console.print(f"[red]  ✗  {msg}[/red]")
    else:
        print(f"  ✗  {msg}")


def _fmt_tuple(t: dict, corpus: str = '') -> str:
    vals = '  '.join(f"{k}={v}" for k, v in t.items())
    return f"⟨ {vals} ⟩"


def _print_element(corpus: str, eid: str, entry: dict):
    t = entry['tuple']
    n = entry['n_instructions']
    tok = entry['token_count']
    expr = entry['expression']
    color = CORPUS_COLORS.get(corpus, 'white')

    if HAS_RICH:
        label = f"[bold {color}]{CORPUS_LABELS[corpus]}[/bold {color}]  →  [bold]{eid}[/bold]"
        console.print()
        console.print(Panel(label, box=box.SIMPLE, padding=(0, 1)))

        # tuple
        trow = Text()
        trow.append('  ⟨ ', style='dim')
        for i, (k, v) in enumerate(t.items()):
            trow.append(k, style=f'bold {color}')
            trow.append('=')
            trow.append(v, style='bright_white')
            if i < len(t) - 1:
                trow.append('  ')
        trow.append(' ⟩', style='dim')
        console.print(trow)
        console.print(f"  [dim]{n} instructions  ·  {tok} ZFCₜ tokens[/dim]")
        console.print()

        # instruction distribution
        mc = entry['mnemonic_counts']
        total = sum(mc.values())
        table = Table(box=box.SIMPLE, show_header=True, header_style='dim')
        table.add_column('Opcode', style='bold', width=10)
        table.add_column('Count', justify='right', width=7)
        table.add_column('Share', width=14)
        for op, cnt in sorted(mc.items(), key=lambda x: -x[1]):
            pct = cnt / total * 100
            bar = '█' * int(pct / 5)
            table.add_row(op, str(cnt), f"[{color}]{bar}[/{color}] {pct:.1f}%")
        console.print(table)

        # ZFCₜ expression
        console.print(f"  [bold]ZFCₜ expression[/bold] [dim]({tok} tokens):[/dim]")
        for line in expr.strip().splitlines():
            console.print(f"    [italic dim]{line.strip()}[/italic dim]")
        console.print()
    else:
        print(f"\n  {CORPUS_LABELS[corpus]}  →  {eid}")
        print(f"  {_fmt_tuple(t)}")
        print(f"  {n} instructions  ·  {tok} ZFCₜ tokens")
        mc = entry['mnemonic_counts']
        total = sum(mc.values())
        for op, cnt in sorted(mc.items(), key=lambda x: -x[1]):
            print(f"    {op:12s}  {cnt:5d}  {cnt/total*100:5.1f}%")
        print(f"\n  ZFCₜ:\n{expr}")


def _print_corpus(corpus: str):
    _ensure_db()
    if corpus not in DB:
        _warn(f"Unknown corpus '{corpus}'.")
        return
    els = DB[corpus]
    base = CORPUS_BASE[corpus]
    color = CORPUS_COLORS.get(corpus, 'white')

    if HAS_RICH:
        console.print()
        console.print(Panel(
            f"[bold {color}]{CORPUS_LABELS[corpus]}[/bold {color}]  ·  {CORPUS_TIER[corpus]}",
            box=box.DOUBLE, padding=(0, 2)
        ))
        trow = Text('  ⟨ ', style='dim')
        for i, (k, v) in enumerate(base.items()):
            trow.append(k, style=f'bold {color}')
            trow.append('=')
            trow.append(v, style='bright_white')
            if i < len(base) - 1:
                trow.append('  ')
        trow.append(' ⟩', style='dim')
        console.print(trow)
        console.print(f"  [dim]{len(els)} elements indexed[/dim]")
        console.print()

        # unique primitive values
        table = Table(title='Primitive variation', box=box.SIMPLE, show_header=True, header_style='dim')
        table.add_column('Primitive', style='bold', width=12)
        table.add_column('Values observed', width=50)
        for k in IG_KEYS:
            vals = sorted(set(e['tuple'].get(k, '—') for e in els.values()))
            table.add_row(k, '  '.join(vals))
        console.print(table)
    else:
        print(f"\n  {CORPUS_LABELS[corpus]}  —  {CORPUS_TIER[corpus]}")
        print(f"  {_fmt_tuple(base)}")
        print(f"  {len(els)} elements")


def _print_ig_bridge():
    _ensure_db()
    corpora = list(CORPUS_BASE.keys())

    if HAS_RICH:
        console.print()
        console.print(Panel("[bold]IG Distance Matrix[/bold]  ·  exOS aleph.rs weighted metric",
                            box=box.DOUBLE, padding=(0, 2)))
        table = Table(box=box.SIMPLE, show_header=True, header_style='dim')
        table.add_column('', width=12)
        for c in corpora:
            table.add_column(c, justify='center', width=14)
        for a in corpora:
            row = [f"[bold]{a}[/bold]"]
            for b in corpora:
                if a == b:
                    row.append('[dim]0.0000[/dim]')
                else:
                    d, conf = _ig_dist(CORPUS_BASE[a], CORPUS_BASE[b])
                    row.append(f"{d:.4f}")
            table.add_row(*row)
        console.print(table)

        # Pairwise detail
        console.print("  [dim]Pairwise detail:[/dim]")
        for i, a in enumerate(corpora):
            for b in corpora[i+1:]:
                d, conf = _ig_dist(CORPUS_BASE[a], CORPUS_BASE[b])
                console.print(f"    [bold]{a}[/bold] ↔ [bold]{b}[/bold]  d={d:.4f}  conflicts: {{{', '.join(conf)}}}")
        console.print()
    else:
        print("\n  IG Distance Matrix")
        for a in corpora:
            for b in corpora:
                if a < b:
                    d, conf = _ig_dist(CORPUS_BASE[a], CORPUS_BASE[b])
                    print(f"  {a} ↔ {b}: d={d:.4f}  conflicts={conf}")


def _print_dist(ref_a: str, ref_b: str):
    ra = _resolve(ref_a)
    rb = _resolve(ref_b)
    if ra is None or rb is None:
        return
    ca, ea, da = ra
    cb, eb, db = rb
    d, conf = _ig_dist(da['tuple'], db['tuple'])

    if HAS_RICH:
        console.print()
        console.print(f"  [bold]{ca}:{ea}[/bold]  ↔  [bold]{cb}:{eb}[/bold]")
        console.print(f"  d = [bold bright_white]{d:.4f}[/bold bright_white]")
        if conf:
            console.print(f"  conflicts: [yellow]{{{', '.join(conf)}}}[/yellow]")

            table = Table(box=box.SIMPLE, show_header=True, header_style='dim')
            table.add_column('Primitive', width=12)
            table.add_column(f'{ca}:{ea}', width=18)
            table.add_column(f'{cb}:{eb}', width=18)
            for k in conf:
                va = da['tuple'].get(k, '—')
                vb = db['tuple'].get(k, '—')
                table.add_row(f"[bold]{k}[/bold]", f"[cyan]{va}[/cyan]", f"[green]{vb}[/green]")
            console.print(table)
        else:
            console.print("  [green]conflicts: ∅  (identical imscriptions)[/green]")
        console.print()
    else:
        print(f"\n  {ca}:{ea} ↔ {cb}:{eb}  d={d:.4f}  conflicts={conf}")


def _print_near(ref: str, n: int = 5):
    r = _resolve(ref)
    if r is None:
        return
    ca, ea, da = r
    ta = da['tuple']

    _ensure_db()
    candidates = []
    for corpus, els in DB.items():
        for eid, entry in els.items():
            if corpus == ca and eid == ea:
                continue
            d, conf = _ig_dist(ta, entry['tuple'])
            candidates.append((d, corpus, eid, conf))
    candidates.sort(key=lambda x: x[0])

    if HAS_RICH:
        console.print()
        console.print(f"  [bold]Nearest neighbors[/bold] to {ca}:{ea} (top {n}):")
        table = Table(box=box.SIMPLE, show_header=True, header_style='dim')
        table.add_column('Rank', width=5)
        table.add_column('Element', width=20)
        table.add_column('d', justify='right', width=8)
        table.add_column('Conflicts', width=30)
        for i, (d, corpus, eid, conf) in enumerate(candidates[:n], 1):
            color = CORPUS_COLORS.get(corpus, 'white')
            table.add_row(
                str(i),
                f"[{color}]{corpus}:{eid}[/{color}]",
                f"{d:.4f}",
                ', '.join(conf) if conf else '[green]∅[/green]',
            )
        console.print(table)
        console.print()
    else:
        print(f"\n  Nearest to {ca}:{ea}:")
        for i, (d, corpus, eid, conf) in enumerate(candidates[:n], 1):
            print(f"  {i:2d}. {corpus}:{eid}  d={d:.4f}  {conf}")


def _print_find(spec: str):
    """Find elements where primitive=value, e.g. ⊣=𐑶"""
    _ensure_db()
    if '=' not in spec:
        _warn("Usage: :find <primitive>=<value>   e.g.  :find ⊣=𐑶")
        return
    prim, val = spec.split('=', 1)
    prim, val = prim.strip(), val.strip()

    results = []
    for corpus, els in DB.items():
        for eid, entry in els.items():
            tv = entry['tuple'].get(prim)
            if tv == val:
                results.append((corpus, eid))

    if HAS_RICH:
        console.print()
        console.print(f"  Elements where [bold]{prim}={val}[/bold]:  {len(results)} found")
        by_corpus: dict[str, list[str]] = {}
        for corpus, eid in results:
            by_corpus.setdefault(corpus, []).append(eid)
        for corpus, eids in by_corpus.items():
            color = CORPUS_COLORS.get(corpus, 'white')
            console.print(f"  [{color}]{corpus}[/{color}] ({len(eids)}): {' '.join(eids[:20])}"
                          + ('  …' if len(eids) > 20 else ''))
        console.print()
    else:
        print(f"\n  {prim}={val}: {len(results)} elements")
        for corpus, eid in results[:30]:
            print(f"    {corpus}:{eid}")


def _print_section(corpus: str):
    if corpus not in SECTIONS:
        _warn(f"No section data for '{corpus}'.")
        return
    _ensure_db()
    color = CORPUS_COLORS.get(corpus, 'white')

    if HAS_RICH:
        console.print()
        console.print(Panel(f"[bold {color}]{corpus}[/bold {color}]  — section topology",
                            box=box.SIMPLE, padding=(0, 1)))
        for sec_name, sample_ids in SECTIONS[corpus]:
            # collect what we have
            present = [eid for eid in sample_ids if eid in DB.get(corpus, {})]
            if not present:
                continue
            entries = [DB[corpus][eid] for eid in present]
            # mode of ⊣
            t_vals = [e['tuple']['⊣'] for e in entries]
            dom_t = max(set(t_vals), key=t_vals.count)
            phi_vals = [e['tuple']['<'] for e in entries]
            dom_phi = max(set(phi_vals), key=phi_vals.count)
            console.print(f"  [bold]{sec_name:20s}[/bold]  ⊣={dom_t}  <={dom_phi}  (sample {len(present)} elements)")
        console.print()
    else:
        for sec_name, sample_ids in SECTIONS[corpus]:
            present = [eid for eid in sample_ids if eid in DB.get(corpus, {})]
            print(f"  {sec_name}: {len(present)} sample elements")


def _print_list(corpus: str):
    _ensure_db()
    if corpus not in DB:
        _warn(f"Unknown corpus '{corpus}'.")
        return
    eids = list(DB[corpus].keys())
    if HAS_RICH:
        color = CORPUS_COLORS.get(corpus, 'white')
        console.print(f"\n  [{color}]{corpus}[/{color}]  ({len(eids)} elements):")
        console.print('  ' + '  '.join(eids))
        console.print()
    else:
        print(f"\n  {corpus} ({len(eids)}): {' '.join(eids)}")


def _print_programs():
    PROGRAMS_DIR.mkdir(exist_ok=True)
    programs = sorted(PROGRAMS_DIR.glob('*.ms'))
    if HAS_RICH:
        console.print()
        if not programs:
            console.print(f"  [dim]No .ms programs found in {PROGRAMS_DIR}[/dim]")
        else:
            for p in programs:
                first = ''
                try:
                    with open(p) as f:
                        for line in f:
                            if line.strip() and not line.strip().startswith('#'):
                                first = line.strip()[:60]
                                break
                except Exception:
                    pass
                console.print(f"  [bold]{p.name}[/bold]  [dim]{first}[/dim]")
        console.print()
    else:
        for p in programs:
            print(f"  {p.name}")


def _run_file(path_str: str):
    p = Path(path_str)
    if not p.is_absolute():
        p = PROGRAMS_DIR / p
    if not p.exists():
        p2 = PROGRAMS_DIR / (path_str + '.ms')
        if p2.exists():
            p = p2
        else:
            _err(f"File not found: {path_str}")
            return
    try:
        src = p.read_text()
    except Exception as e:
        _err(str(e))
        return

    _out(f"\n  [dim]Running {p.name}…[/dim]\n" if HAS_RICH else f"\n  Running {p.name}…")
    for line in src.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        _out(f"  [cyan]→[/cyan] {line}" if HAS_RICH else f"  → {line}")
        _dispatch(line)


# ── help ───────────────────────────────────────────────────────────────────────

HELP_TEXT = """
[bold]ELEMENT NAVIGATION[/bold]
  [cyan]voynich f1r[/cyan]            show folio f1r
  [cyan]rohonc p1[/cyan]              show page p1
  [cyan]linear_a t40[/cyan]           show tablet t40
  [cyan]voynich:f1r[/cyan]  or  [cyan]f1r[/cyan]  shorthand (if unambiguous)

[bold]ANALYSIS[/bold]
  [cyan]:dist f1r rohonc:p1[/cyan]    distance between any two elements
  [cyan]:near voynich:f1r 5[/cyan]    5 nearest neighbors across all corpora
  [cyan]:corpus voynich[/cyan]        corpus-level imscription + primitive variation
  [cyan]:ig_bridge[/cyan]             full 3×3 cross-corpus distance matrix
  [cyan]:section rohonc[/cyan]        section topology breakdown
  [cyan]:find ⊣=𐑶[/cyan]           find elements with a specific primitive value

[bold]LISTING[/bold]
  [cyan]:list voynich[/cyan]          list all folio IDs
  [cyan]:list rohonc[/cyan]
  [cyan]:list linear_a[/cyan]

[bold]PROGRAMS[/bold]
  [cyan]:run <file.ms>[/cyan]         run a manuscript program
  [cyan]:programs[/cyan]              list available programs

[bold]SHELL[/bold]
  [cyan]:help[/cyan]                  this text
  [cyan]:quit[/cyan]  /  [cyan]:q[/cyan]           exit
"""


def _print_help():
    if HAS_RICH:
        console.print(Panel(HELP_TEXT, title='manuscript_eval  v1.0.0',
                            box=box.DOUBLE, padding=(0, 2)))
    else:
        print(__doc__)

# ── banner ─────────────────────────────────────────────────────────────────────

BANNER_ASCII = """\
╔═══════════════════════════════════════════════════════════════╗
║  manuscript_eval  v1.0.0                                      ║
║  Universal Imscriptive Grammar × Manuscript Corpora           ║
║  Voynich · Rohonc · Linear A           :help for commands     ║
╚═══════════════════════════════════════════════════════════════╝"""


def _print_banner():
    if HAS_RICH:
        from rich.text import Text as RText
        title = RText()
        title.append('manuscript_eval', style='bold bright_white')
        title.append('  v1.0.0', style='yellow')
        sub = RText()
        sub.append('Universal Imscriptive Grammar × Manuscript Corpora\n', style='dim')
        sub.append('Voynich  ', style='cyan')
        sub.append('·  ', style='dim')
        sub.append('Rohonc  ', style='green')
        sub.append('·  ', style='dim')
        sub.append('Linear A', style='gold1')
        sub.append('          Type ', style='dim')
        sub.append(':help', style='bold cyan')
        sub.append(' for commands', style='dim')
        console.print(Panel(RText.assemble(title, '\n', sub),
                            box=box.DOUBLE, border_style='bright_blue', padding=(1, 2)))
        _ensure_db()
        total = sum(len(v) for v in DB.values())
        console.print(f"  [dim]Loaded {total} elements  ·  {DATA_FILE.name}[/dim]\n")
    else:
        print(BANNER_ASCII)

# ── dispatch ───────────────────────────────────────────────────────────────────

def _dispatch(line: str) -> bool:
    """Process one REPL line. Return False to quit."""
    parts = line.strip().split()
    if not parts:
        return True
    cmd = parts[0].lower()

    # quit
    if cmd in (':quit', ':q'):
        return False

    # help
    if cmd == ':help':
        _print_help()
        return True

    # ig_bridge
    if cmd == ':ig_bridge':
        _print_ig_bridge()
        return True

    # corpus
    if cmd == ':corpus':
        if len(parts) < 2:
            _warn(":corpus <name>   e.g. :corpus voynich")
            return True
        _print_corpus(parts[1].lower())
        return True

    # section
    if cmd == ':section':
        if len(parts) < 2:
            _warn(":section <corpus>   e.g. :section rohonc")
            return True
        _print_section(parts[1].lower())
        return True

    # list
    if cmd == ':list':
        if len(parts) < 2:
            _warn(":list <corpus>   e.g. :list linear_a")
            return True
        _print_list(parts[1].lower())
        return True

    # dist
    if cmd == ':dist':
        if len(parts) < 3:
            _warn(":dist <a> <b>   e.g. :dist voynich:f1r rohonc:p1")
            return True
        _print_dist(parts[1], parts[2])
        return True

    # near
    if cmd == ':near':
        if len(parts) < 2:
            _warn(":near <element> [N]   e.g. :near linear_a:t1 5")
            return True
        n = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 5
        _print_near(parts[1], n)
        return True

    # find
    if cmd == ':find':
        if len(parts) < 2:
            _warn(":find <prim>=<val>   e.g. :find ⊣=𐑶")
            return True
        _print_find(parts[1])
        return True

    # programs
    if cmd == ':programs':
        _print_programs()
        return True

    # run
    if cmd == ':run':
        if len(parts) < 2:
            _warn(":run <file.ms>")
            return True
        _run_file(parts[1])
        return True

    # element navigation: "voynich f1r" or "rohonc p1" or "linear_a t40"
    # also handles: "f1r", "voynich:f1r"
    if cmd in ('voynich', 'rohonc', 'linear_a') and len(parts) >= 2:
        ref = f"{cmd}:{parts[1]}"
        r = _resolve(ref)
        if r:
            _print_element(*r)
        return True

    # bare element id or corpus:id
    r = _resolve(parts[0])
    if r:
        _print_element(*r)
        return True

    _warn(f"Unknown command '{line}'. Type :help for reference.")
    return True

# ── REPL ───────────────────────────────────────────────────────────────────────

def _setup_completion():
    try:
        _ensure_db()
        words = [':help', ':quit', ':q', ':ig_bridge', ':corpus', ':section',
                 ':list', ':dist', ':near', ':find', ':programs', ':run',
                 'voynich', 'rohonc', 'linear_a']
        for corpus, els in DB.items():
            words += [f"{corpus}:{eid}" for eid in els]
            words += list(els.keys())
        words = list(set(words))

        def complete(text, state):
            matches = [w for w in words if w.startswith(text)]
            return matches[state] if state < len(matches) else None

        readline.set_completer(complete)
        readline.parse_and_bind('tab: complete')
    except Exception:
        pass


def run_repl():
    _print_banner()
    _setup_completion()

    while True:
        try:
            if HAS_RICH:
                line = console.input('[bold bright_blue]ms>[/bold bright_blue] ')
            else:
                line = input('ms> ')
        except (EOFError, KeyboardInterrupt):
            _out('\n  Exiting.')
            break

        if not _dispatch(line.strip()):
            break


def run_file(path: str):
    _print_banner()
    _ensure_db()
    _run_file(path)


def print_usage():
    print(__doc__)


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Universal Manuscript REPL')
    ap.add_argument('file', nargs='?', help='Run a .ms program file instead of REPL')
    ap.add_argument('--expr', '-e', help='Evaluate a single command and exit')
    args = ap.parse_args()

    if args.file:
        _print_banner()
        _ensure_db()
        _run_file(args.file)
    elif args.expr:
        _ensure_db()
        _dispatch(args.expr)
    else:
        run_repl()
