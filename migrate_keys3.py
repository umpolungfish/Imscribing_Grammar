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
    "synthon_agent.py",
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
    ("Gamma", "ɢ"), ("Omega", "Ω"), ("Phi", "φ̂"),
    ("D", "Ð"), ("T", "Þ"), ("R", "Ř"), ("P", "Φ"),
    ("F", "ƒ"), ("K", "Ç"), ("G", "Γ"), ("H", "Ħ"), ("S", "Σ"),
]

# ── Full old-name → glyph-pair value replacements (longest first) ─────────────
# Covers both ASCII-prefix (D_omega) and glyph-prefix (Ð_omega) forms,
# both quoted in code and bare in comments/docstrings.
VALUE_PAIRS = [
    # multi-word names first (longest)
    ("Phi_c_complex",         "φ̂_Æ"),
    ("Phi_closerevepsilon",   "φ̂_Æ"),
    ("Phi_revepsilon",        "φ̂_3"),
    ("Phi_upstep",            "φ̂_Ţ"),
    ("Phi_softsign",          "φ̂_ž"),
    ("Phi_ctyogh",            "φ̂_ÿ"),
    ("Phi_super",             "φ̂_Ţ"),
    ("Phi_EP",                "φ̂_3"),
    ("Phi_sub",               "φ̂_ž"),
    ("Phi_c",                 "φ̂_ÿ"),
    ("Gamma_doublevertline",  "ɢ_Ş"),
    ("Gamma_secstress",       "ɢ_ˌ"),
    ("Gamma_spleftarrow",     "ɢ_˝"),
    ("Gamma_corner",          "ɢ_^"),
    ("Gamma_broad",           "ɢ_Ş"),
    ("Gamma_seq",             "ɢ_ˌ"),
    ("Gamma_or",              "ɢ_˝"),
    ("Gamma_and",             "ɢ_^"),
    ("Omega_closeepsilon",    "Ω_Å"),
    ("Omega_dzlig",           "Ω_z"),
    ("Omega_crtwo",           "Ω_2"),
    ("Omega_turna",           "Ω_5"),
    ("Omega_NA",              "Ω_5"),
    ("Omega_Z2",              "Ω_2"),
    ("Omega_Z",               "Ω_z"),
    ("Omega_0",               "Ω_Å"),
    ("D_invomega",            "Ð_;"),
    ("D_turnthree",           "Ð_C"),
    ("D_triangle",            "Ð_C"),
    ("D_wedge",               "Ð_ß"),
    ("D_infty",               "Ð_;"),
    ("D_odot",                "Ð_ω"),
    ("D_omega",               "Ð_ω"),
    ("T_commatailz",          "Þ_¨"),
    ("T_bullseye",            "Þ_ò"),
    ("T_boxtimes",            "Þ_¨"),
    ("T_network",             "Þ_6"),
    ("T_bowtie",              "Þ_ò"),
    ("T_nrleg",               "Þ_6"),
    ("T_invscr",              "Þ_K"),
    ("T_openo",               "Þ_O"),
    ("T_odot",                "Þ_O"),
    ("T_in",                  "Þ_K"),
    ("R_subrightarrow",       "Ř_¯"),
    ("R_lyoghlig",            "Ř_="),
    ("R_downstep",            "Ř_Ť"),
    ("R_dagger",              "Ř_Ť"),
    ("R_super",               "Ř_¯"),
    ("R_cat",                 "Ř_ý"),
    ("R_ctz",                 "Ř_ý"),
    ("R_lr",                  "Ř_="),
    ("P_doublebarpipe",       "Φ_}"),
    ("P_subdoublearrow",      "Φ_˙"),
    ("P_pipevar",             "Φ_F"),
    ("P_upsilon",             "Φ_υ"),
    ("P_aolig",               "Φ_ɐ"),
    ("P_pm_sym",              "Φ_}"),
    ("P_asym",                "Φ_ɐ"),
    ("P_psi",                 "Φ_υ"),
    ("P_pm",                  "Φ_F"),
    ("P_sym",                 "Φ_˙"),
    ("F_hardsign",            "ƒ_ż"),
    ("F_beltl",               "ƒ_ì"),
    ("F_hbar",                "ƒ_ż"),
    ("F_eth",                 "ƒ_ð"),
    ("F_ell",                 "ƒ_ì"),
    ("F_dh",                  "ƒ_ð"),
    ("K_frtailgamma",         "Ç_-"),
    ("K_teshlig",             "Ç_Ù"),
    ("K_turnm",               "Ç_W"),
    ("K_lambda",              "Ç_λ"),
    ("K_schwa",               "Ç_@"),
    ("K_MBL",                 "Ç_λ"),
    ("K_fast",                "Ç_-"),
    ("K_mod",                 "Ç_W"),
    ("K_slow",                "Ç_@"),
    ("K_trap",                "Ç_Ù"),
    ("G_revapostrophe",       "Γ_ʔ"),
    ("G_gimel",               "Γ_γ"),
    ("G_aleph",               "Γ_ʔ"),
    ("G_gamma",               "Γ_γ"),
    ("G_beth",                "Γ_β"),
    ("G_beta",                "Γ_β"),
    ("H_invscripta",          "Ħ_!"),
    ("H_toneletterstem",      "Ħ_£"),
    ("H_turntwo",             "Ħ_A"),
    ("H_closeomega",          "Ħ_Ñ"),
    ("H_inf",                 "Ħ_!"),
    ("H0",                    "Ħ_Ñ"),
    ("H1",                    "Ħ_£"),
    ("H2",                    "Ħ_A"),
    ("S_doublebaresh",        "Σ_S"),
    ("S_ltailm",              "Σ_ï"),
    ("S_n_m",                 "Σ_ï"),
    ("S_n_n",                 "Σ_ő"),
    ("S_1_1",                 "Σ_S"),
    ("S_ctn",                 "Σ_ő"),
    # glyph-prefix forms left from phase 2 misses
    ("Ð_omega",               "Ð_ω"),
    ("Þ_openo",               "Þ_O"),
    ("Ř_ctz",                 "Ř_ý"),
    ("Ř_downstep",            "Ř_Ť"),
    ("Φ_doublebarpipe",       "Φ_}"),
    ("ƒ_hardsign",            "ƒ_ż"),
    ("Ç_schwa",               "Ç_@"),
    ("Γ_revapostrophe",       "Γ_ʔ"),
    ("ɢ_doublevertline",      "ɢ_Ş"),
    ("φ̂_ctyogh",              "φ̂_ÿ"),
    ("φ̂_closerevepsilon",     "φ̂_Æ"),
    ("Ħ_invscripta",          "Ħ_!"),
    ("Σ_ltailm",              "Σ_ï"),
    ("Ω_dzlig",               "Ω_z"),
    ("Ω_crtwo",               "Ω_2"),
    ("Ω_turna",               "Ω_5"),
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
