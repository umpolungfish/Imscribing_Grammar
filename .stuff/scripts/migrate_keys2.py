"""
Phase 2 migration: remaining files not covered by migrate_keys.py.
Applies both key migration AND value migration (old TIPA names → glyph chars).
"""

import ast, sys, pathlib

FILES = [
    "quiver_crystal.py",
    "navigators.py",
    "riemann_xi_navigator.py",
    "category_theory_navigator.py",
]

# ── Key renaming ───────────────────────────────────────────────────────────────
KEY_PAIRS = [
    ("Gamma", "ɢ"), ("Omega", "Ω"), ("Phi", "⊙"),   # multi-char first
    ("D", "Ð"), ("T", "Þ"), ("R", "Ř"), ("P", "Φ"),
    ("F", "ƒ"), ("K", "Ç"), ("G", "Γ"), ("H", "Ħ"), ("S", "Σ"),
]

# ── Value renaming — old TIPA-name forms → canonical glyph pairs ──────────────
# Longer patterns first to avoid partial matches.
VALUE_PAIRS = [
    # Ð — Dimension
    ("Ð_omega",          "𐑦"),
    ("Ð_turnthree",      "𐑨"),
    ("Ð_invomega",       "𐑼"),
    ("Ð_wynn",           "𐑛"),
    # Þ — Topology
    ("Þ_openo",          "𐑸"),
    ("Þ_commatailz",     "𐑶"),
    ("Þ_bullseye",       "𐑥"),
    ("Þ_invscr",         "𐑰"),
    ("Þ_nrleg",          "𐑡"),
    # Ř — Relational
    ("Ř_downstep",       "𐑽"),
    ("Ř_lyoghlig",       "𐑾"),
    ("Ř_ctz",            "𐑑"),
    ("Ř_subrightarrow",  "𐑩"),
    # Φ — Parity
    ("Φ_doublebarpipe",  "𐑹"),
    ("Φ_subdoublearrow", "𐑯"),
    ("Φ_pipevar",        "𐑬"),
    ("Φ_upsilon",        "𐑿"),
    ("Φ_aolig",          "𐑗"),
    # ƒ — Fidelity
    ("ƒ_hardsign",       "ƒ^ż"),
    ("ƒ_dh",             "ƒ^ð"),
    ("ƒ_beltl",          "ƒ^ì"),
    # Ç — Kinetics
    ("Ç_lambda",         "Ç^λ"),
    ("Ç_teshlig",        "Ç^Ù"),
    ("Ç_schwa",          "Ç^@"),
    ("Ç_turnm",          "Ç^W"),
    ("Ç_frtailgamma",    "Ç^-"),
    # Γ — Scope
    ("Γ_revapostrophe",  "𐑲"),
    ("Γ_gamma",          "𐑔"),
    ("Γ_beta",           "𐑚"),
    # ɢ — Coupling
    ("ɢ_doublevertline", "ɢ^Ş"),
    ("ɢ_secstress",      "ɢ^ˌ"),
    ("ɢ_spleftarrow",    "ɢ^˝"),
    ("ɢ_corner",         "ɢ^∧"),
    # ⊙ — Criticality
    ("⊙_closerevepsilon","𐑮"),
    ("⊙_revepsilon",     "𐑻"),
    ("⊙_upstep",         "𐑣"),
    ("⊙_ctyogh",         "⊙"),
    ("⊙_softsign",       "𐑢"),
    # Ħ — Chirality
    ("Ħ_invscripta",     "𐑫"),
    ("Ħ_turntwo",        "𐑖"),
    ("Ħ_toneletterstem", "𐑒"),
    ("Ħ_closeomega",     "𐑓"),
    # Σ — Stoichiometry
    ("Σ_ltailm",         "𐑳"),
    ("Σ_ctn",            "𐑕"),
    ("Σ_doublebaresh",   "𐑙"),
    # Ω — Topological Invariant
    ("Ω_dzlig",          "𐑭"),
    ("Ω_turna",          "𐑟"),
    ("Ω_crtwo",          "𐑴"),
    ("Ω_closeepsilon",   "𐑷"),
]

def migrate(text: str) -> str:
    # Key migration
    for old, new in KEY_PAIRS:
        q_old, q_new = f'"{old}"', f'"{new}"'
        text = text.replace(q_old, q_new)
        text = text.replace(f"{old}='", f"{new}='")
        text = text.replace(f'{old}="', f'{new}="')
        text = text.replace(f'"{old}: ', f'"{new}: ')
        text = text.replace(f"{old}={{self.", f"{new}={{self.")
        text = text.replace(f", {old}=self.", f", {new}=self.")
        text = text.replace(f"({old}=self.", f"({new}=self.")
    # Value migration (longer patterns first — already ordered above)
    for old_v, new_v in VALUE_PAIRS:
        text = text.replace(old_v, new_v)
    return text

total_changed = 0
for fname in FILES:
    p = pathlib.Path(fname)
    if not p.exists():
        print(f"SKIP (not found): {fname}")
        continue
    original = p.read_text(encoding="utf-8")
    migrated = migrate(original)
    if migrated == original:
        print(f"NO CHANGE: {fname}")
        continue
    try:
        ast.parse(migrated)
    except SyntaxError as e:
        print(f"SYNTAX ERROR in {fname}: {e}")
        sys.exit(1)
    n = sum(1 for a, b in zip(original.splitlines(), migrated.splitlines()) if a != b)
    p.write_text(migrated, encoding="utf-8")
    total_changed += 1
    print(f"OK ({n} lines changed): {fname}")

print(f"\nDone. {total_changed}/{len(FILES)} files modified.")
