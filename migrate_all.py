"""
Final sweep: apply key + value migration to every Python file in the project.
Skips historical/utility scripts. Uses ast.parse() to verify syntax.
"""

import ast, sys, pathlib, tokenize, io


PLACEHOLDER = 'XPHIFROBX'


def _fstring_line_set(source: str) -> set[int]:
    """Return set of 1-based line numbers that are inside FSTRING_MIDDLE spans."""
    lines_in_fstring: set[int] = set()
    depth = 0
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.FSTRING_START:
                depth += 1
            elif tok.type == tokenize.FSTRING_END:
                depth -= 1
            elif tok.type == tokenize.FSTRING_MIDDLE and depth > 0:
                for ln in range(tok.start[0], tok.end[0] + 1):
                    lines_in_fstring.add(ln)
    except tokenize.TokenError:
        pass
    return lines_in_fstring


def migrate_phi_frob(text: str) -> str:
    """
    Replace PLACEHOLDER with Φ_}} on f-string lines, Φ_} elsewhere.
    The main migrate() function uses PLACEHOLDER instead of Φ_} directly
    so we can tokenize the pre-} text and find f-string line boundaries.
    """
    fstring_lines = _fstring_line_set(text)
    out_lines = []
    for i, line in enumerate(text.splitlines(keepends=True), 1):
        if PLACEHOLDER in line:
            if i in fstring_lines:
                line = line.replace(PLACEHOLDER, 'Φ_}}')
            else:
                line = line.replace(PLACEHOLDER, 'Φ_}')
        out_lines.append(line)
    return ''.join(out_lines)

SKIP = {
    'migrate_keys.py','migrate_keys2.py','migrate_keys3.py','migrate_all.py',
    'migrate_phonetic.py','migrate_primitive_symbols.py','migrate_to_symbol_ids.py',
    'clean_assign.py','final_assign.py','gen_final.py','produce_table.py',
    'final_table.py','assign_symbols.py','parse_symbols.py','match_symbols.py',
    'scan_symbols.py','check_symbols.py','complete_assignment.py','extract_proof.py',
    'verify_proof_logic.py','fix_tex.py','write_header.py',
    'generate_vocal_expressions.py','IG_primitive_map.py',
}

# Collect all .py files
files = []
for p in pathlib.Path('.').glob('*.py'):
    if p.name not in SKIP:
        files.append(p)
for sub in ['agents', 'space_search']:
    for p in pathlib.Path(sub).glob('*.py'):
        if p.name not in SKIP:
            files.append(p)
files.sort()

KEY_PAIRS = [
    ("Gamma", "ɢ"), ("Omega", "Ω"), ("Phi", "φ̂"),
    ("D", "Ð"), ("T", "Þ"), ("R", "Ř"), ("P", "Φ"),
    ("F", "ƒ"), ("K", "Ç"), ("G", "Γ"), ("H", "Ħ"), ("S", "Σ"),
]

# Comprehensive old → new value pairs (longest first to avoid partial matches)
VALUE_PAIRS = [
    ("Phi_c_complex",       "φ̂_Æ"),
    ("Phi_closerevepsilon", "φ̂_Æ"),
    ("φ̂_closerevepsilon",  "φ̂_Æ"),
    ("Phi_revepsilon",      "φ̂_3"),
    ("Phi_upstep",          "φ̂_Ţ"),
    ("Phi_softsign",        "φ̂_ž"),
    ("Phi_ctyogh",          "φ̂_ÿ"),
    ("φ̂_ctyogh",           "φ̂_ÿ"),
    ("Phi_super",           "φ̂_Ţ"),
    ("Phi_EP",              "φ̂_3"),
    ("Phi_sub",             "φ̂_ž"),
    ("Phi_c",               "φ̂_ÿ"),
    ("Gamma_doublevertline","ɢ_Ş"),
    ("Gamma_secstress",     "ɢ_ˌ"),
    ("Gamma_spleftarrow",   "ɢ_˝"),
    ("Gamma_corner",        "ɢ_^"),
    ("Gamma_broad",         "ɢ_Ş"),
    ("Gamma_seq",           "ɢ_ˌ"),
    ("Gamma_or",            "ɢ_˝"),
    ("Gamma_and",           "ɢ_^"),
    ("ɢ_doublevertline",    "ɢ_Ş"),
    ("ɢ_secstress",         "ɢ_ˌ"),
    ("Omega_closeepsilon",  "Ω_Å"),
    ("Omega_dzlig",         "Ω_z"),
    ("Ω_dzlig",             "Ω_z"),
    ("Omega_crtwo",         "Ω_2"),
    ("Ω_crtwo",             "Ω_2"),
    ("Omega_turna",         "Ω_5"),
    ("Ω_turna",             "Ω_5"),
    ("Omega_NA",            "Ω_5"),
    ("Omega_Z2",            "Ω_2"),
    ("Omega_Z",             "Ω_z"),
    ("Omega_0",             "Ω_Å"),
    ("D_invomega",          "Ð_;"),
    ("D_turnthree",         "Ð_C"),
    ("D_triangle",          "Ð_C"),
    ("D_wedge",             "Ð_ß"),
    ("D_infty",             "Ð_;"),
    ("D_odot",              "Ð_ω"),
    ("D_omega",             "Ð_ω"),
    ("Ð_omega",             "Ð_ω"),
    ("Ð_turnthree",         "Ð_C"),
    ("Ð_invomega",          "Ð_;"),
    ("Ð_wynn",              "Ð_ß"),
    ("T_commatailz",        "Þ_¨"),
    ("Þ_commatailz",        "Þ_¨"),
    ("T_bullseye",          "Þ_ò"),
    ("Þ_bullseye",          "Þ_ò"),
    ("T_boxtimes",          "Þ_¨"),
    ("T_network",           "Þ_6"),
    ("T_bowtie",            "Þ_ò"),
    ("T_nrleg",             "Þ_6"),
    ("Þ_nrleg",             "Þ_6"),
    ("T_invscr",            "Þ_K"),
    ("Þ_invscr",            "Þ_K"),
    ("T_openo",             "Þ_O"),
    ("Þ_openo",             "Þ_O"),
    ("T_odot",              "Þ_O"),
    ("T_in",                "Þ_K"),
    ("R_subrightarrow",     "Ř_¯"),
    ("Ř_subrightarrow",     "Ř_¯"),
    ("R_lyoghlig",          "Ř_="),
    ("Ř_lyoghlig",          "Ř_="),
    ("R_downstep",          "Ř_Ť"),
    ("Ř_downstep",          "Ř_Ť"),
    ("R_dagger",            "Ř_Ť"),
    ("R_super",             "Ř_¯"),
    ("R_cat",               "Ř_ý"),
    ("R_ctz",               "Ř_ý"),
    ("Ř_ctz",               "Ř_ý"),
    ("R_lr",                "Ř_="),
    ("P_doublebarpipe",     PLACEHOLDER),
    ("Φ_doublebarpipe",     PLACEHOLDER),
    ("P_subdoublearrow",    "Φ_˙"),
    ("Φ_subdoublearrow",    "Φ_˙"),
    ("P_pipevar",           "Φ_F"),
    ("Φ_pipevar",           "Φ_F"),
    ("P_upsilon",           "Φ_υ"),
    ("Φ_upsilon",           "Φ_υ"),
    ("P_aolig",             "Φ_ɐ"),
    ("Φ_aolig",             "Φ_ɐ"),
    ("P_pm_sym",            PLACEHOLDER),
    ("P_asym",              "Φ_ɐ"),
    ("P_psi",               "Φ_υ"),
    ("P_pm",                "Φ_F"),
    ("P_sym",               "Φ_˙"),
    ("F_hardsign",          "ƒ_ż"),
    ("ƒ_hardsign",          "ƒ_ż"),
    ("F_beltl",             "ƒ_ì"),
    ("ƒ_beltl",             "ƒ_ì"),
    ("F_hbar",              "ƒ_ż"),
    ("F_eth",               "ƒ_ð"),
    ("F_ell",               "ƒ_ì"),
    ("F_dh",                "ƒ_ð"),
    ("K_frtailgamma",       "Ç_-"),
    ("Ç_frtailgamma",       "Ç_-"),
    ("K_teshlig",           "Ç_Ù"),
    ("Ç_teshlig",           "Ç_Ù"),
    ("K_turnm",             "Ç_W"),
    ("Ç_turnm",             "Ç_W"),
    ("K_lambda",            "Ç_λ"),
    ("K_schwa",             "Ç_@"),
    ("Ç_schwa",             "Ç_@"),
    ("K_MBL",               "Ç_λ"),
    ("K_fast",              "Ç_-"),
    ("K_mod",               "Ç_W"),
    ("K_slow",              "Ç_@"),
    ("K_trap",              "Ç_Ù"),
    ("G_revapostrophe",     "Γ_ʔ"),
    ("Γ_revapostrophe",     "Γ_ʔ"),
    ("G_gimel",             "Γ_γ"),
    ("G_aleph",             "Γ_ʔ"),
    ("G_gamma",             "Γ_γ"),
    ("G_beth",              "Γ_β"),
    ("G_beta",              "Γ_β"),
    ("H_invscripta",        "Ħ_!"),
    ("Ħ_invscripta",        "Ħ_!"),
    ("H_toneletterstem",    "Ħ_£"),
    ("Ħ_toneletterstem",    "Ħ_£"),
    ("H_turntwo",           "Ħ_A"),
    ("Ħ_turntwo",           "Ħ_A"),
    ("H_closeomega",        "Ħ_Ñ"),
    ("Ħ_closeomega",        "Ħ_Ñ"),
    ("H_inf",               "Ħ_!"),
    ("S_doublebaresh",      "Σ_S"),
    ("Σ_doublebaresh",      "Σ_S"),
    ("S_ltailm",            "Σ_ï"),
    ("Σ_ltailm",            "Σ_ï"),
    ("S_n_m",               "Σ_ï"),
    ("S_n_n",               "Σ_ő"),
    ("S_1_1",               "Σ_S"),
    ("S_ctn",               "Σ_ő"),
    ("Σ_ctn",               "Σ_ő"),
]

def migrate(text: str) -> str:
    for old, new in KEY_PAIRS:
        text = text.replace(f'"{old}"', f'"{new}"')
        text = text.replace(f"{old}='", f"{new}='")
        text = text.replace(f'{old}="', f'{new}="')
        text = text.replace(f'"{old}: ', f'"{new}: ')
        text = text.replace(f"{old}={{self.", f"{new}={{self.")
        text = text.replace(f", {old}=self.", f", {new}=self.")
        text = text.replace(f"({old}=self.", f"({new}=self.")
    for old_v, new_v in VALUE_PAIRS:
        text = text.replace(old_v, new_v)
    # Resolve PLACEHOLDER → Φ_} or Φ_}} depending on f-string context
    if PLACEHOLDER in text:
        text = migrate_phi_frob(text)
    return text

total = 0
for p in files:
    original = p.read_text(encoding="utf-8")
    migrated = migrate(original)
    if migrated == original:
        continue
    try:
        ast.parse(migrated)
    except SyntaxError as e2:
        print(f"SYNTAX ERROR {p}: {e2}")
        sys.exit(1)
    n = sum(1 for a, b in zip(original.splitlines(), migrated.splitlines()) if a != b)
    p.write_text(migrated, encoding="utf-8")
    total += 1
    print(f"OK ({n:3d} lines): {p}")

print(f"\n{total}/{len(files)} files modified.")
