"""
Phase 3 migration: comprehensive sweep of ALL remaining Python files.
Handles both quoted and unquoted old-style names in code, comments, and docstrings.
Also migrates files not yet touched (navigators/crystal_viz/lambda/etc).
"""

import ast, sys, pathlib

# All remaining files needing migration
FILES = [
    "quiver_crystal.py",
    "navigators.py",
    "riemann_xi_navigator.py",
    "category_theory_navigator.py",
    "thurston_t_specialist.py",
    "langlands_program_navigator.py",
    "hott_bridge.py",
    "quantum_field_theory_navigator.py",
    "perfect_cuboid_navigator.py",
    "homotopy_type_theory_navigator.py",
    "imscribe_agent.py",
    "representation_theory_navigator.py",
    "algebraic_geometry_navigator.py",
    "crystal_viz.py",
    "lambda_engine.py",
    "aleph_tensor.py",
    "zfc_navigator.py",
    "crystal_enumeration.py",
    "domain_navigators.py",
    "crystal_navigator.py",
    "IG_inquiry.py",
    "agents/true_agentic_agent.py",
    "space_search/primitives.py",
]

# ── Key renaming (quoted form) ─────────────────────────────────────────────────
KEY_PAIRS = [
    ("Gamma", "ɢ"), ("Omega", "Ω"), ("Phi", "⊙"),
    ("D", "Ð"), ("T", "Þ"), ("R", "Ř"), ("P", "Φ"),
    ("F", "ƒ"), ("K", "Ç"), ("G", "Γ"), ("H", "Ħ"), ("S", "Σ"),
]

# ── Full old-name → glyph-pair value replacements (longest first) ─────────────
# Covers both ASCII-prefix (D_omega) and glyph-prefix (Ð_omega) forms,
# both quoted in code and bare in comments/docstrings.
VALUE_PAIRS = [
    # multi-word names first (longest)
    ("𐑮",         "𐑮"),
    ("Phi_closerevepsilon",   "𐑮"),
    ("Phi_revepsilon",        "𐑻"),
    ("Phi_upstep",            "𐑣"),
    ("Phi_softsign",          "𐑢"),
    ("⊙",            "⊙"),
    ("Phi_super",             "𐑣"),
    ("𐑻",                "𐑻"),
    ("𐑢",               "𐑢"),
    ("⊙",                 "⊙"),
    ("Gamma_doublevertline",  "ɢ^Ş"),
    ("Gamma_secstress",       "ɢ^ˌ"),
    ("Gamma_spleftarrow",     "ɢ^˝"),
    ("Gamma_corner",          "ɢ^∧"),
    ("Gamma_broad",           "ɢ^Ş"),
    ("Gamma_seq",             "ɢ^ˌ"),
    ("Gamma_or",              "ɢ^˝"),
    ("Gamma_and",             "ɢ^∧"),
    ("Omega_closeepsilon",    "𐑷"),
    ("Omega_dzlig",           "𐑭"),
    ("Omega_crtwo",           "𐑴"),
    ("Omega_turna",           "𐑟"),
    ("Omega_NA",              "𐑟"),
    ("Omega_Z2",              "𐑴"),
    ("Omega_Z",               "𐑭"),
    ("Omega_0",               "𐑷"),
    ("D_invomega",            "𐑼"),
    ("D_turnthree",           "𐑨"),
    ("D_triangle",            "𐑨"),
    ("D_wedge",               "𐑛"),
    ("D_infty",               "𐑼"),
    ("D_odot",                "𐑦"),
    ("D_omega",               "𐑦"),
    ("T_commatailz",          "𐑶"),
    ("T_bullseye",            "𐑥"),
    ("T_boxtimes",            "𐑶"),
    ("T_network",             "𐑡"),
    ("T_bowtie",              "𐑥"),
    ("T_nrleg",               "𐑡"),
    ("T_invscr",              "𐑰"),
    ("T_openo",               "𐑸"),
    ("T_odot",                "𐑸"),
    ("T_in",                  "𐑰"),
    ("R_subrightarrow",       "𐑩"),
    ("R_lyoghlig",            "𐑾"),
    ("R_downstep",            "𐑽"),
    ("R_dagger",              "𐑽"),
    ("R_super",               "𐑩"),
    ("R_cat",                 "𐑑"),
    ("R_ctz",                 "𐑑"),
    ("R_lr",                  "𐑾"),
    ("P_doublebarpipe",       "𐑹"),
    ("P_subdoublearrow",      "𐑯"),
    ("P_pipevar",             "𐑬"),
    ("P_upsilon",             "𐑿"),
    ("P_aolig",               "𐑗"),
    ("P_pm_sym",              "𐑹"),
    ("P_asym",                "𐑗"),
    ("P_psi",                 "𐑿"),
    ("P_pm",                  "𐑬"),
    ("P_sym",                 "𐑯"),
    ("F_hardsign",            "ƒ^ż"),
    ("F_beltl",               "ƒ^ì"),
    ("F_hbar",                "ƒ^ż"),
    ("F_eth",                 "ƒ^ð"),
    ("F_ell",                 "ƒ^ì"),
    ("F_dh",                  "ƒ^ð"),
    ("K_frtailgamma",         "Ç^-"),
    ("K_teshlig",             "Ç^Ù"),
    ("K_turnm",               "Ç^W"),
    ("K_lambda",              "Ç^λ"),
    ("K_schwa",               "Ç^@"),
    ("K_MBL",                 "Ç^λ"),
    ("K_fast",                "Ç^-"),
    ("K_mod",                 "Ç^W"),
    ("K_slow",                "Ç^@"),
    ("K_trap",                "Ç^Ù"),
    ("G_revapostrophe",       "𐑲"),
    ("G_gimel",               "𐑔"),
    ("G_aleph",               "𐑲"),
    ("G_gamma",               "𐑔"),
    ("G_beth",                "𐑚"),
    ("G_beta",                "𐑚"),
    ("H_invscripta",          "𐑫"),
    ("H_toneletterstem",      "𐑒"),
    ("H_turntwo",             "𐑖"),
    ("H_closeomega",          "𐑓"),
    ("H_inf",                 "𐑫"),
    ("H0",                    "𐑓"),
    ("H1",                    "𐑒"),
    ("H2",                    "𐑖"),
    ("S_doublebaresh",        "𐑙"),
    ("S_ltailm",              "𐑳"),
    ("S_n_m",                 "𐑳"),
    ("S_n_n",                 "𐑕"),
    ("S_1_1",                 "𐑙"),
    ("S_ctn",                 "𐑕"),
    # glyph-prefix forms left from phase 2 misses
    ("Ð_omega",               "𐑦"),
    ("Þ_openo",               "𐑸"),
    ("Ř_ctz",                 "𐑑"),
    ("Ř_downstep",            "𐑽"),
    ("Φ_doublebarpipe",       "𐑹"),
    ("ƒ_hardsign",            "ƒ^ż"),
    ("Ç_schwa",               "Ç^@"),
    ("Γ_revapostrophe",       "𐑲"),
    ("ɢ_doublevertline",      "ɢ^Ş"),
    ("⊙_ctyogh",              "⊙"),
    ("⊙_closerevepsilon",     "𐑮"),
    ("Ħ_invscripta",          "𐑫"),
    ("Σ_ltailm",              "𐑳"),
    ("Ω_dzlig",               "𐑭"),
    ("Ω_crtwo",               "𐑴"),
    ("Ω_turna",               "𐑟"),
]

def migrate(text: str) -> str:
    # Key migration (quoted form only — safe)
    for old, new in KEY_PAIRS:
        q_old, q_new = f'"{old}"', f'"{new}"'
        text = text.replace(q_old, q_new)
        text = text.replace(f"{old}='", f"{new}='")
        text = text.replace(f'{old}="', f'{new}="')
        text = text.replace(f'"{old}: ', f'"{new}: ')
        text = text.replace(f"{old}={{self.", f"{new}={{self.")
        text = text.replace(f", {old}=self.", f", {new}=self.")
        text = text.replace(f"({old}=self.", f"({new}=self.")
    # Value migration — covers code, comments, docstrings
    for old_v, new_v in VALUE_PAIRS:
        text = text.replace(old_v, new_v)
    return text

total_changed = 0
for fname in FILES:
    p = pathlib.Path(fname)
    if not p.exists():
        continue
    original = p.read_text(encoding="utf-8")
    migrated = migrate(original)
    if migrated == original:
        continue
    try:
        ast.parse(migrated)
    except SyntaxError as e:
        print(f"SYNTAX ERROR in {fname}: {e}")
        sys.exit(1)
    n = sum(1 for a, b in zip(original.splitlines(), migrated.splitlines()) if a != b)
    p.write_text(migrated, encoding="utf-8")
    total_changed += 1
    print(f"OK ({n} lines): {fname}")

print(f"\nDone. {total_changed} files modified.")
