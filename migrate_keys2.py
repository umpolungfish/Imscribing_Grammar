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
    ("Gamma", "ɢ"), ("Omega", "Ω"), ("Phi", "φ̂"),   # multi-char first
    ("D", "Ð"), ("T", "Þ"), ("R", "Ř"), ("P", "Φ"),
    ("F", "ƒ"), ("K", "Ç"), ("G", "Γ"), ("H", "Ħ"), ("S", "Σ"),
]

# ── Value renaming — old TIPA-name forms → canonical glyph pairs ──────────────
# Longer patterns first to avoid partial matches.
VALUE_PAIRS = [
    # Ð — Dimension
    ("Ð_omega",          "Ð_ω"),
    ("Ð_turnthree",      "Ð_C"),
    ("Ð_invomega",       "Ð_;"),
    ("Ð_wynn",           "Ð_ß"),
    # Þ — Topology
    ("Þ_openo",          "Þ_O"),
    ("Þ_commatailz",     "Þ_¨"),
    ("Þ_bullseye",       "Þ_ò"),
    ("Þ_invscr",         "Þ_K"),
    ("Þ_nrleg",          "Þ_6"),
    # Ř — Relational
    ("Ř_downstep",       "Ř_Ť"),
    ("Ř_lyoghlig",       "Ř_="),
    ("Ř_ctz",            "Ř_ý"),
    ("Ř_subrightarrow",  "Ř_¯"),
    # Φ — Parity
    ("Φ_doublebarpipe",  "Φ_}"),
    ("Φ_subdoublearrow", "Φ_˙"),
    ("Φ_pipevar",        "Φ_F"),
    ("Φ_upsilon",        "Φ_υ"),
    ("Φ_aolig",          "Φ_ɐ"),
    # ƒ — Fidelity
    ("ƒ_hardsign",       "ƒ_ż"),
    ("ƒ_dh",             "ƒ_ð"),
    ("ƒ_beltl",          "ƒ_ì"),
    # Ç — Kinetics
    ("Ç_lambda",         "Ç_λ"),
    ("Ç_teshlig",        "Ç_Ù"),
    ("Ç_schwa",          "Ç_@"),
    ("Ç_turnm",          "Ç_W"),
    ("Ç_frtailgamma",    "Ç_-"),
    # Γ — Scope
    ("Γ_revapostrophe",  "Γ_ʔ"),
    ("Γ_gamma",          "Γ_γ"),
    ("Γ_beta",           "Γ_β"),
    # ɢ — Coupling
    ("ɢ_doublevertline", "ɢ_Ş"),
    ("ɢ_secstress",      "ɢ_ˌ"),
    ("ɢ_spleftarrow",    "ɢ_˝"),
    ("ɢ_corner",         "ɢ_^"),
    # φ̂ — Criticality
    ("φ̂_closerevepsilon","φ̂_Æ"),
    ("φ̂_revepsilon",     "φ̂_3"),
    ("φ̂_upstep",         "φ̂_Ţ"),
    ("φ̂_ctyogh",         "φ̂_ÿ"),
    ("φ̂_softsign",       "φ̂_ž"),
    # Ħ — Temporal Depth
    ("Ħ_invscripta",     "Ħ_!"),
    ("Ħ_turntwo",        "Ħ_A"),
    ("Ħ_toneletterstem", "Ħ_£"),
    ("Ħ_closeomega",     "Ħ_Ñ"),
    # Σ — Stoichiometry
    ("Σ_ltailm",         "Σ_ï"),
    ("Σ_ctn",            "Σ_ő"),
    ("Σ_doublebaresh",   "Σ_S"),
    # Ω — Topological Invariant
    ("Ω_dzlig",          "Ω_z"),
    ("Ω_turna",          "Ω_5"),
    ("Ω_crtwo",          "Ω_2"),
    ("Ω_closeepsilon",   "Ω_Å"),
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
