"""
migration.py — Catalog migration from legacy primitive values to canonical form.

Handles all value renames introduced by the models.py unification with Core.lean:

  1. Dimensionality: D_triangle -> D_cube, D_infinity -> D_infty
  2. Topology: T_chains -> T_linear, T_square -> T_network, T_in -> T_network,
               T_box -> T_cage
  3. Recognition: R_dagger / R_cat -> R_catalytic
  4. Polarity: P_asym -> P_pm, P_sym -> P_pm_sym
  5. Grammar: Gamma_and -> G_and, Gamma_seq -> G_seq, etc.
  6. Criticality: Phi_super -> Phi_sup
  7. Chirality: Hinf -> H_inf
  8. Stoichiometry: "n:n" -> "n:m"
  9. Granularity PERMUTATION (ordering was inverted):
       old G_aleph (GLOBAL/coarse) -> new G_gimel
       old G_gimel (MESOSCALE)     -> new G_beth
       old G_beth  (LOCAL/fine)    -> new G_aleph
     This is a 3-cycle. The migration uses a temporary sentinel to avoid
     double-substitution within a single entry.

Run as a script to migrate IG_catalog.json in-place:
    python -m imscrbgrmr.migration [--catalog PATH] [--dry-run]

Or call migrate_entry(d) / migrate_catalog(entries) programmatically.
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Per-field value maps (old value -> new canonical value)
# ─────────────────────────────────────────────────────────────────────────────

_D_MAP = {
    "D_triangle":  "D_cube",
    "D_infinity":  "D_infty",
    # unchanged: D_point, D_line, D_wedge, D_cube, D_infty, D_holo
}

_T_MAP = {
    "T_chains":  "T_linear",
    "T_square":  "T_network",   # hub-node -> generic network
    "T_in":      "T_network",   # old shorthand
    "T_box":     "T_cage",
    # unchanged: T_linear, T_branched, T_network, T_bowtie, T_torus, T_holo,
    #            T_network_hex, T_network_mixed, T_network_interp, T_network_sym,
    #            T_cage, T_bowl, T_braid
}

_R_MAP = {
    "R_dagger": "R_catalytic",
    "R_cat":    "R_catalytic",
    # unchanged: R_exact, R_subset, R_superset, R_catalytic, R_allosteric,
    #            R_mechanical, R_covalent_dynamic
}

_P_MAP = {
    "P_asym": "P_pm",
    "P_sym":  "P_pm_sym",
    # unchanged: P_neutral, P_plus, P_minus, P_pm, P_pm_sym, P_pm_pseudo, P_directional
}

_GAMMA_MAP = {
    "Gamma_and":         "G_and",
    "Gamma_or":          "G_or",
    "Gamma_seq":         "G_seq",
    "Gamma_dissipative": "G_dissipative",
    # already canonical: G_and, G_or, G_seq, G_xor, G_impl, G_dissipative
    # compound forms like "Gamma_and(SPECIFIC)" -> extract operator part
}

_PHI_MAP = {
    "Phi_super": "Phi_sup",
    # unchanged: Phi_sub, Phi_c, Phi_sup
}

_H_MAP = {
    "Hinf": "H_inf",
    # unchanged: H0, H1, H2, H_inf
}

_S_MAP = {
    "n:n": "n:m",   # alias
    # unchanged: 1:1, 1:n, n:m, cat
}

# Granularity 3-cycle correction (old meaning -> new canonical value):
#   old G_aleph was GLOBAL (coarsest) -> must become G_gimel (coarsest)
#   old G_gimel was MESOSCALE         -> must become G_beth  (mesoscale)
#   old G_beth  was LOCAL (finest)    -> must become G_aleph (finest)
# We use a sentinel to avoid double-substitution.
_G_SENTINEL_MAP = {
    "G_aleph": "__G_GIMEL__",
    "G_gimel": "__G_BETH__",
    "G_beth":  "__G_ALEPH__",
}
_G_SENTINEL_RESOLVE = {
    "__G_GIMEL__": "G_gimel",
    "__G_BETH__":  "G_beth",
    "__G_ALEPH__": "G_aleph",
}


def _migrate_gamma(value: str) -> str:
    """
    Migrate a Gamma field value.
    Handles compound forms like "Gamma_and(SPECIFIC)" by extracting the operator.
    """
    if "(" in value:
        # compound form: extract operator before "("
        operator_part = value.split("(")[0].strip()
        return _GAMMA_MAP.get(operator_part, operator_part)
    return _GAMMA_MAP.get(value, value)


# ─────────────────────────────────────────────────────────────────────────────
# Entry-level migration
# ─────────────────────────────────────────────────────────────────────────────

MigrationLog = List[Tuple[str, str, str]]   # [(field, old_value, new_value)]


def migrate_entry(entry: Dict[str, Any]) -> Tuple[Dict[str, Any], MigrationLog]:
    """
    Migrate a single catalog entry dict to canonical form.

    Returns (migrated_entry, log) where log lists every change made as
    (field, old_value, new_value) tuples. Empty log means no changes needed.
    """
    e = deepcopy(entry)
    log: MigrationLog = []

    def _apply(field: str, mapping: Dict[str, str]) -> None:
        old = e.get(field)
        if old is None:
            return
        new = mapping.get(str(old))
        if new and new != old:
            e[field] = new
            log.append((field, str(old), new))

    _apply("D",     _D_MAP)
    _apply("T",     _T_MAP)
    _apply("R",     _R_MAP)
    _apply("P",     _P_MAP)
    _apply("Phi",   _PHI_MAP)
    _apply("H",     _H_MAP)
    _apply("S",     _S_MAP)

    # Grammar: special handler for compound forms
    old_gamma = e.get("Gamma")
    if old_gamma is not None:
        new_gamma = _migrate_gamma(str(old_gamma))
        if new_gamma != old_gamma:
            e["Gamma"] = new_gamma
            log.append(("Gamma", str(old_gamma), new_gamma))

    # Granularity: 3-cycle via sentinel
    old_g = e.get("G")
    if old_g is not None:
        sentinel = _G_SENTINEL_MAP.get(str(old_g))
        if sentinel:
            new_g = _G_SENTINEL_RESOLVE[sentinel]
            e["G"] = new_g
            log.append(("G", str(old_g), new_g))

    return e, log


def migrate_catalog(
    entries: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, MigrationLog]]:
    """
    Migrate a list of catalog entries.

    Returns (migrated_entries, changes) where changes maps entry name to its
    migration log. Entries with empty logs were already canonical.
    """
    migrated = []
    changes: Dict[str, MigrationLog] = {}
    for entry in entries:
        new_entry, log = migrate_entry(entry)
        migrated.append(new_entry)
        if log:
            changes[entry.get("name", "<unnamed>")] = log
    return migrated, changes


def report(changes: Dict[str, MigrationLog]) -> str:
    """Human-readable migration report."""
    if not changes:
        return "Catalog already canonical — no changes required.\n"
    lines = [f"Migrated {len(changes)} entries:\n"]
    for name, log in sorted(changes.items()):
        lines.append(f"  {name}:")
        for field, old, new in log:
            lines.append(f"    {field}: {old!r} -> {new!r}")
    lines.append(f"\nTotal field changes: {sum(len(v) for v in changes.values())}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _default_catalog_path() -> Path:
    return Path(__file__).parent.parent / "IG_catalog.json"


def main(argv: Optional[List[str]] = None) -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Migrate IG_catalog.json to canonical form")
    parser.add_argument("--catalog", default=str(_default_catalog_path()),
                        help="Path to catalog JSON (default: IG_catalog.json)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print changes without writing")
    parser.add_argument("--output", default=None,
                        help="Write migrated catalog to this path (default: overwrite input)")
    args = parser.parse_args(argv)

    catalog_path = Path(args.catalog)
    if not catalog_path.exists():
        print(f"Error: catalog not found at {catalog_path}", file=sys.stderr)
        sys.exit(1)

    with open(catalog_path) as f:
        data = json.load(f)

    # Support both list and dict-of-dicts catalog formats
    if isinstance(data, list):
        entries = data
        def _pack(e): return e
        def _unpack(m): return m
    elif isinstance(data, dict):
        entries = list(data.values())
        names = list(data.keys())
        def _pack(e): return e
        def _unpack(migrated): return dict(zip(names, migrated))
    else:
        print("Unsupported catalog format", file=sys.stderr)
        sys.exit(1)

    migrated, changes = migrate_catalog(entries)
    print(report(changes))

    if args.dry_run:
        print("[dry-run] No files written.")
        return

    out_path = Path(args.output) if args.output else catalog_path
    with open(out_path, "w") as f:
        json.dump(_unpack(migrated) if isinstance(data, dict) else migrated,
                  f, indent=2, ensure_ascii=False)
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
