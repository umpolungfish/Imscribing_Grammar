#!/usr/bin/env python3
"""
migrate_phonetic.py — Complete and total rename of the 49 canonical
primitive subtype identifiers to their phonetic-subscript names as
defined in SOUNDSOFTHENAMEOFTHESYMBOLS.md.

Run with:
    uv run migrate_phonetic.py [--dry-run] [--catalog-only]

Without flags: migrates IG_catalog.json + all .py and .lean files in the repo.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# The canonical 49-pair rename mapping.
# IMPORTANT: pairs where one old name is a prefix of another are sorted so
# the longer name comes first (P_pm_sym before P_pm; 𐑮 before ⊙).
# ---------------------------------------------------------------------------

RENAME: list[tuple[str, str]] = [
    # D — Dimensionality  (F4)
    ("Ð_wedge",         "Ð_wynn"),
    ("Ð_triangle",      "Ð_turnthree"),
    ("Ð_infty",         "Ð_invomega"),
    ("Ð_odot",          "Ð_omega"),

    # T — Topology  (F5)
    ("Þ_network",       "Þ_nrleg"),
    ("Þ_in",            "Þ_invscr"),
    ("Þ_bowtie",        "Þ_bullseye"),
    ("Þ_boxtimes",      "Þ_commatailz"),
    ("Þ_odot",          "Þ_openo"),

    # R — Relational Mode  (F4)
    ("Ř_super",         "Ř_subrightarrow"),
    ("Ř_cat",           "Ř_ctz"),
    ("Ř_dagger",        "Ř_downstep"),
    ("Ř_lr",            "Ř_lyoghlig"),

    # P — Parity/Symmetry  (F5) — P_pm_sym before P_pm
    ("Φ_pm_sym",        "Φ_doublebarpipe"),
    ("Φ_asym",          "Φ_aolig"),
    ("Φ_psi",           "Φ_upsilon"),
    ("Φ_pm",            "Φ_pipevar"),
    ("Φ_sym",           "Φ_subdoublearrow"),

    # F — Fidelity  (F3)
    ("ƒ_ell",           "ƒ_beltl"),
    ("ƒ_eth",           "ƒ_dh"),
    ("ƒ_hbar",          "ƒ_hardsign"),

    # K — Kinetics  (F5)
    ("Ç_fast",          "Ç_frtailgamma"),
    ("Ç_mod",           "Ç_turnm"),
    ("Ç_slow",          "Ç_schwa"),
    ("Ç_trap",          "Ç_teshlig"),
    ("Ç_MBL",           "Ç_lambda"),

    # G — Scope/Granularity  (F3)
    ("Γ_beth",          "Γ_beta"),
    ("Γ_gimel",         "Γ_gamma"),
    ("Γ_aleph",         "Γ_revapostrophe"),

    # Gamma — Coupling  (F4)
    # Old Python/JSON used G_ prefix; Lean already uses Gamma_.
    # After migration, Python/JSON also use Gamma_.
    ("Γ_and",           "ɢ_corner"),
    ("Γ_or",            "ɢ_spleftarrow"),
    ("Γ_seq",           "ɢ_secstress"),
    ("Γ_broad",         "ɢ_doublevertline"),

    # Phi — Criticality  (F5) — 𐑮 before ⊙
    ("⊙_c_complex",   "⊙_closerevepsilon"),
    ("⊙",           "⊙_ctyogh"),
    ("⊙_sub",         "⊙_softsign"),
    ("⊙_EP",          "⊙_revepsilon"),
    ("⊙_super",       "⊙_upstep"),
    # Backward-compat alias from models.py
    ("⊙_sup",         "⊙_upstep"),

    # H — Chirality  (F4)
    ("Ħ_inf",           "Ħ_invscripta"),
    ("H0",              "Ħ_closeomega"),
    ("H1",              "Ħ_toneletterstem"),
    ("H2",              "Ħ_turntwo"),

    # S — Stoichiometry  (F3)
    ("one_one",         "Σ_doublebaresh"),
    ("n_n",             "Σ_ctn"),
    ("n_m",             "Σ_ltailm"),

    # Omega — Topological Invariant  (F4)
    ("Ω_Z2",        "Ω_crtwo"),
    ("Ω_Z",         "Ω_dzlig"),
    ("Omega_0",         "Ω_closeepsilon"),
    ("Ω_NA",        "Ω_turna"),
]

# Quick-lookup dict
RENAME_DICT: dict[str, str] = dict(RENAME)


# ---------------------------------------------------------------------------
# Catalog migration (JSON-aware: only renames field VALUES, not keys)
# ---------------------------------------------------------------------------

CATALOG_PRIM_KEYS = {"D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"}


def migrate_entry(entry: dict) -> dict:
    """Return a copy of the catalog entry with all primitive values renamed."""
    out = dict(entry)
    for key in CATALOG_PRIM_KEYS:
        if key in out and isinstance(out[key], str):
            out[key] = RENAME_DICT.get(out[key], out[key])
    return out


def migrate_catalog(path: Path, dry_run: bool = False) -> int:
    """Migrate IG_catalog.json in-place. Returns number of value substitutions."""
    with open(path) as f:
        data = json.load(f)

    prim_changes = 0
    desc_changes = 0
    migrated = []
    for entry in data:
        new_entry = migrate_entry(entry)
        for key in CATALOG_PRIM_KEYS:
            if entry.get(key) != new_entry.get(key):
                prim_changes += 1
        # Also migrate old names in description strings (prose references)
        if "description" in new_entry and isinstance(new_entry["description"], str):
            new_desc, n = migrate_text(new_entry["description"])
            if n:
                new_entry["description"] = new_desc
                desc_changes += n
        migrated.append(new_entry)

    total_changes = prim_changes + desc_changes
    if not dry_run:
        with open(path, "w") as f:
            json.dump(migrated, f, indent=2, ensure_ascii=False)
        print(f"  [catalog] {path.name}: {prim_changes} primitive + {desc_changes} description substitutions ({len(migrated)} entries)")
    else:
        print(f"  [dry-run catalog] would make {prim_changes} primitive + {desc_changes} description substitutions in {path.name}")

    return total_changes


# ---------------------------------------------------------------------------
# Text-file migration (Python, Lean, Markdown, TeX)
# ---------------------------------------------------------------------------

def migrate_text(text: str) -> tuple[str, int]:
    """
    Apply RENAME to a text file. Replaces occurrences of each old name that
    appear as a whole token (preceded and followed by a non-word character or
    string boundary). Returns (new_text, n_substitutions).
    """
    n = 0
    for old, new in RENAME:
        # Use word-boundary anchors: match old only when not preceded or followed
        # by alphanumeric or underscore.
        pattern = r'(?<![A-Za-z0-9_])' + re.escape(old) + r'(?![A-Za-z0-9_])'
        new_text, count = re.subn(pattern, new, text)
        n += count
        text = new_text
    return text, n


def migrate_file(path: Path, dry_run: bool = False) -> int:
    """Migrate a single text file. Returns number of substitutions."""
    original = path.read_text(encoding="utf-8", errors="replace")
    text = original
    latex_count = 0
    if path.suffix in {".md", ".tex", ".html"}:
        text, latex_count = migrate_latex(text)
    text, token_count = migrate_text(text)
    count = latex_count + token_count
    if count == 0:
        return 0
    if not dry_run:
        path.write_text(text, encoding="utf-8")
        tag = f"latex:{latex_count}+token:{token_count}" if latex_count else f"token:{token_count}"
        print(f"  [{path.suffix}] {path.relative_to(ROOT)}: {count} substitution(s) ({tag})")
    else:
        print(f"  [dry-run] {path.relative_to(ROOT)}: would make {count} substitution(s)")
    return count


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

SKIP_DIRS = {".git", ".lake", ".venv", "__pycache__", "unsloth_compiled_cache"}
SKIP_FILES = {"migrate_phonetic.py", "SOUNDSOFTHENAMEOFTHESYMBOLS.md"}

TEXT_SUFFIXES = {".py", ".lean", ".md", ".tex", ".html", ".txt", ".yaml", ".toml", ".json"}

# ---------------------------------------------------------------------------
# LaTeX math-notation replacements
# These fire BEFORE the word-boundary pass, on .md and .tex files only.
# Order: longer/more-specific patterns before shorter/ambiguous ones.
# ---------------------------------------------------------------------------

LATEX_PATTERNS: list[tuple[str, str]] = [
    # ── P — complex P_pm_sym forms (must come before P_pm) ─────────────────
    (r'P_\{\\pm\}\^\{\\text\{sym\}\}',             r'P_{\\text{doublebarpipe}}'),
    (r'P_\{\\pm\}\^\\text\{sym\}',                  r'P_{\\text{doublebarpipe}}'),
    (r'P_\{\\pm\}\^\{\\mathrm\{sym\}\}',            r'P_{\\text{doublebarpipe}}'),
    (r'P_\\pm\^\\text\{sym\}',                      r'P_{\\text{doublebarpipe}}'),

    # ── Phi — complex 𐑮 forms (must come before ⊙) ──────────
    (r'\\⊙\^\{\\mathbb\{C\}\}',                 r'\\Phi_{\\text{closerevepsilon}}'),
    (r'\\⊙\^\\mathbb\{C\}',                     r'\\Phi_{\\text{closerevepsilon}}'),
    (r'\\Phi_\{c\^\{\\mathbb\{C\}\}\}',             r'\\Phi_{\\text{closerevepsilon}}'),
    (r'\\Phi_\{\\text\{c_complex\}\}',              r'\\Phi_{\\text{closerevepsilon}}'),

    # ── Omega — complex forms (must come before Omega_Z alone) ──────────────
    (r'\\Omega_\{\\mathbb\{Z\}_2\}',                r'\\Omega_{\\text{crtwo}}'),
    (r'\\Omega_\{\\mathbb\{Z\}\}',                  r'\\Omega_{\\text{dzlig}}'),
    (r'\\Omega_\\mathbb\{Z\}_2',                    r'\\Omega_{\\text{crtwo}}'),
    (r'\\Omega_\\mathbb\{Z\}',                      r'\\Omega_{\\text{dzlig}}'),
    (r'\\Omega_\{\\text\{NA\}\}',                   r'\\Omega_{\\text{turna}}'),
    (r'\\Omega_\\text\{NA\}',                       r'\\Omega_{\\text{turna}}'),
    (r'\\Omega_\{\\text\{Z2\}\}',                   r'\\Omega_{\\text{crtwo}}'),
    (r'\\Omega_\\text\{Z2\}',                       r'\\Omega_{\\text{crtwo}}'),
    (r'\\Omega_0\b',                                r'\\Omega_{\\text{closeepsilon}}'),

    # ── Phi — simple subscript forms ─────────────────────────────────────────
    (r'\\⊙\b(?!_)',                             r'\\Phi_{\\text{ctyogh}}'),
    (r'\\Phi_\{c\}',                                r'\\Phi_{\\text{ctyogh}}'),
    (r'\\Phi_\{\\text\{sub\}\}',                    r'\\Phi_{\\text{softsign}}'),
    (r'\\Phi_\\text\{sub\}',                        r'\\Phi_{\\text{softsign}}'),
    (r'\\Phi_\{\\text\{EP\}\}',                     r'\\Phi_{\\text{revepsilon}}'),
    (r'\\Phi_\\text\{EP\}',                         r'\\Phi_{\\text{revepsilon}}'),
    (r'\\Phi_\{\\text\{super\}\}',                  r'\\Phi_{\\text{upstep}}'),
    (r'\\Phi_\\text\{super\}',                      r'\\Phi_{\\text{upstep}}'),
    (r'\\Phi_\{\\text\{sup\}\}',                    r'\\Phi_{\\text{upstep}}'),
    (r'\\Phi_\\text\{sup\}',                        r'\\Phi_{\\text{upstep}}'),

    # ── D primitive ──────────────────────────────────────────────────────────
    (r'D_\\wedge\b',                                r'D_{\\text{wynn}}'),
    (r'D_\{\\wedge\}',                              r'D_{\\text{wynn}}'),
    (r'D_\\triangle\b',                             r'D_{\\text{turnthree}}'),
    (r'D_\{\\triangle\}',                           r'D_{\\text{turnthree}}'),
    (r'D_\\infty\b',                                r'D_{\\text{invomega}}'),
    (r'D_\{\\infty\}',                              r'D_{\\text{invomega}}'),
    (r'D_\\odot\b',                                 r'D_{\\text{omega}}'),
    (r'D_\{\\odot\}',                               r'D_{\\text{omega}}'),

    # ── T primitive ──────────────────────────────────────────────────────────
    (r'T_\\bowtie\b',                               r'T_{\\text{bullseye}}'),
    (r'T_\{\\bowtie\}',                             r'T_{\\text{bullseye}}'),
    (r'T_\\boxtimes\b',                             r'T_{\\text{commatailz}}'),
    (r'T_\{\\boxtimes\}',                           r'T_{\\text{commatailz}}'),
    (r'T_\\odot\b',                                 r'T_{\\text{openo}}'),
    (r'T_\{\\odot\}',                               r'T_{\\text{openo}}'),
    (r'T_\{\\in\}',                                 r'T_{\\text{invscr}}'),
    (r'T_\\in\b',                                   r'T_{\\text{invscr}}'),
    (r'T_\{\\text\{net\}\}',                        r'T_{\\text{nrleg}}'),
    (r'T_\\text\{net\}',                            r'T_{\\text{nrleg}}'),
    (r'T_\{\\text\{network\}\}',                    r'T_{\\text{nrleg}}'),
    (r'T_\\text\{network\}',                        r'T_{\\text{nrleg}}'),
    (r'T_\{\\text\{in\}\}',                         r'T_{\\text{invscr}}'),
    (r'T_\\text\{in\}',                             r'T_{\\text{invscr}}'),

    # ── R primitive ──────────────────────────────────────────────────────────
    (r'R_\\dagger\b',                               r'R_{\\text{downstep}}'),
    (r'R_\{\\dagger\}',                             r'R_{\\text{downstep}}'),
    (r'R_\\leftrightarrow\b',                       r'R_{\\text{lyoghlig}}'),
    (r'R_\{\\leftrightarrow\}',                     r'R_{\\text{lyoghlig}}'),
    (r'R_\{\\text\{sup\}\}',                        r'R_{\\text{subrightarrow}}'),
    (r'R_\\text\{sup\}',                            r'R_{\\text{subrightarrow}}'),
    (r'R_\{\\text\{super\}\}',                      r'R_{\\text{subrightarrow}}'),
    (r'R_\\text\{super\}',                          r'R_{\\text{subrightarrow}}'),
    (r'R_\{\\text\{cat\}\}',                        r'R_{\\text{ctz}}'),
    (r'R_\\text\{cat\}',                            r'R_{\\text{ctz}}'),
    (r'R_\{\\text\{lr\}\}',                         r'R_{\\text{lyoghlig}}'),
    (r'R_\\text\{lr\}',                             r'R_{\\text{lyoghlig}}'),
    (r'R_\{\\text\{dagger\}\}',                     r'R_{\\text{downstep}}'),
    (r'R_\\text\{dagger\}',                         r'R_{\\text{downstep}}'),

    # ── P primitive ──────────────────────────────────────────────────────────
    (r'P_\\psi\b',                                  r'P_{\\text{upsilon}}'),
    (r'P_\{\\psi\}',                                r'P_{\\text{upsilon}}'),
    (r'P_\\pm\b',                                   r'P_{\\text{pipevar}}'),
    (r'P_\{\\pm\}(?!\^)',                           r'P_{\\text{pipevar}}'),
    (r'P_\{\\text\{asym\}\}',                       r'P_{\\text{aolig}}'),
    (r'P_\\text\{asym\}',                           r'P_{\\text{aolig}}'),
    (r'P_\{\\text\{sym\}\}',                        r'P_{\\text{subdoublearrow}}'),
    (r'P_\\text\{sym\}',                            r'P_{\\text{subdoublearrow}}'),

    # ── F primitive ──────────────────────────────────────────────────────────
    (r'F_\\ell\b',                                  r'F_{\\text{beltl}}'),
    (r'F_\{\\ell\}',                                r'F_{\\text{beltl}}'),
    (r'F_\\eth\b',                                  r'F_{\\text{dh}}'),
    (r'F_\{\\eth\}',                                r'F_{\\text{dh}}'),
    (r'F_\\hbar\b',                                 r'F_{\\text{hardsign}}'),
    (r'F_\{\\hbar\}',                               r'F_{\\text{hardsign}}'),

    # ── K primitive ──────────────────────────────────────────────────────────
    (r'K_\{\\text\{fast\}\}',                       r'K_{\\text{frtailgamma}}'),
    (r'K_\\text\{fast\}',                           r'K_{\\text{frtailgamma}}'),
    (r'K_\{\\text\{mod\}\}',                        r'K_{\\text{turnm}}'),
    (r'K_\\text\{mod\}',                            r'K_{\\text{turnm}}'),
    (r'K_\{\\text\{slow\}\}',                       r'K_{\\text{schwa}}'),
    (r'K_\\text\{slow\}',                           r'K_{\\text{schwa}}'),
    (r'K_\{\\text\{trap\}\}',                       r'K_{\\text{teshlig}}'),
    (r'K_\\text\{trap\}',                           r'K_{\\text{teshlig}}'),
    (r'K_\{\\text\{MBL\}\}',                        r'K_{\\text{lambda}}'),
    (r'K_\\text\{MBL\}',                            r'K_{\\text{lambda}}'),

    # ── G (scope/granularity) ─────────────────────────────────────────────────
    (r'G_\\beth\b',                                 r'G_{\\text{beta}}'),
    (r'G_\{\\beth\}',                               r'G_{\\text{beta}}'),
    (r'G_\\gimel\b',                                r'G_{\\text{gamma}}'),
    (r'G_\{\\gimel\}',                              r'G_{\\text{gamma}}'),
    (r'G_\\aleph\b',                                r'G_{\\text{revapostrophe}}'),
    (r'G_\{\\aleph\}',                              r'G_{\\text{revapostrophe}}'),

    # ── Gamma (interaction grammar) ───────────────────────────────────────────
    (r'\\Gamma_\\wedge\b',                          r'\\Gamma_{\\text{corner}}'),
    (r'\\Gamma_\{\\wedge\}',                        r'\\Gamma_{\\text{corner}}'),
    (r'\\Gamma_\\vee\b',                            r'\\Gamma_{\\text{spleftarrow}}'),
    (r'\\Gamma_\{\\vee\}',                          r'\\Gamma_{\\text{spleftarrow}}'),
    (r'\\Gamma_\{\\text\{seq\}\}',                  r'\\Gamma_{\\text{secstress}}'),
    (r'\\Gamma_\\text\{seq\}',                      r'\\Gamma_{\\text{secstress}}'),
    (r'\\Gamma_\{\\text\{brd\}\}',                  r'\\Gamma_{\\text{doublevertline}}'),
    (r'\\Gamma_\\text\{brd\}',                      r'\\Gamma_{\\text{doublevertline}}'),
    (r'\\Gamma_\{\\text\{broad\}\}',                r'\\Gamma_{\\text{doublevertline}}'),
    (r'\\Gamma_\\text\{broad\}',                    r'\\Gamma_{\\text{doublevertline}}'),
    (r'\\Gamma_\{\\text\{and\}\}',                  r'\\Gamma_{\\text{corner}}'),
    (r'\\Gamma_\\text\{and\}',                      r'\\Gamma_{\\text{corner}}'),
    (r'\\Gamma_\{\\text\{or\}\}',                   r'\\Gamma_{\\text{spleftarrow}}'),
    (r'\\Gamma_\\text\{or\}',                       r'\\Gamma_{\\text{spleftarrow}}'),

    # ── H primitive ──────────────────────────────────────────────────────────
    # H_\infty is safe; H_0/H_1/H_2 are too ambiguous (homology groups etc.)
    # and are handled by the word-boundary token pass for Python/JSON only.
    (r'H_\\infty\b',                                r'H_{\\text{invscripta}}'),
    (r'H_\{\\infty\}',                              r'H_{\\text{invscripta}}'),
]


def migrate_latex(text: str) -> tuple[str, int]:
    """Apply LaTeX-specific pattern replacements. Run before migrate_text()."""
    n = 0
    for pattern, replacement in LATEX_PATTERNS:
        new_text, count = re.subn(pattern, replacement, text)
        n += count
        text = new_text
    return text, n


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file():
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.name in SKIP_FILES:
                continue
            if path.suffix in TEXT_SUFFIXES and path.name != "IG_catalog.json":
                yield path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv
    catalog_only = "--catalog-only" in sys.argv

    catalog_path = ROOT / "IG_catalog.json"
    total = 0

    print(f"\n{'DRY RUN: ' if dry_run else ''}Phonetic primitive migration")
    print(f"  {len(RENAME)} canonical renames defined")
    print()

    print("=== Catalog ===")
    total += migrate_catalog(catalog_path, dry_run=dry_run)

    if not catalog_only:
        print()
        print("=== Text files ===")
        for path in sorted(iter_files(ROOT)):
            total += migrate_file(path, dry_run=dry_run)

    print()
    print(f"Total substitutions: {total}")
    if dry_run:
        print("(dry run — no files written)")


if __name__ == "__main__":
    main()
