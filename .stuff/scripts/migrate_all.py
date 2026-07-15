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
    Replace PLACEHOLDER with 𐑹} on f-string lines, 𐑹 elsewhere.
    The main migrate() function uses PLACEHOLDER instead of 𐑹 directly
    so we can tokenize the pre-} text and find f-string line boundaries.
    """
    fstring_lines = _fstring_line_set(text)
    out_lines = []
    for i, line in enumerate(text.splitlines(keepends=True), 1):
        if PLACEHOLDER in line:
            if i in fstring_lines:
                line = line.replace(PLACEHOLDER, '𐑹}')
            else:
                line = line.replace(PLACEHOLDER, '𐑹')
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
    ("Gamma", "ɢ"), ("Omega", "Ω"), ("Phi", "⊙"),
    ("D", "Ð"), ("T", "Þ"), ("R", "Ř"), ("P", "Φ"),
    ("F", "ƒ"), ("K", "Ç"), ("G", "Γ"), ("H", "Ħ"), ("S", "Σ"),
]

# Comprehensive old → new value pairs (longest first to avoid partial matches)
VALUE_PAIRS = [
    ("Phi_c_complex",       "𐑮"),
    ("Phi_closerevepsilon", "𐑮"),
    ("⊙_closerevepsilon",  "𐑮"),
    ("Phi_revepsilon",      "𐑻"),
    ("Phi_upstep",          "𐑣"),
    ("Phi_softsign",        "𐑢"),
    ("Phi_ctyogh",          "⊙"),
    ("⊙_ctyogh",           "⊙"),
    ("Phi_super",           "𐑣"),
    ("Phi_EP",              "𐑻"),
    ("Phi_sub",             "𐑢"),
    ("Phi_c",               "⊙"),
    ("Gamma_doublevertline","ɢ^Ş"),
    ("Gamma_secstress",     "ɢ^ˌ"),
    ("Gamma_spleftarrow",   "ɢ^˝"),
    ("Gamma_corner",        "ɢ^∧"),
    ("Gamma_broad",         "ɢ^Ş"),
    ("Gamma_seq",           "ɢ^ˌ"),
    ("Gamma_or",            "ɢ^˝"),
    ("Gamma_and",           "ɢ^∧"),
    ("ɢ_doublevertline",    "ɢ^Ş"),
    ("ɢ_secstress",         "ɢ^ˌ"),
    ("Omega_closeepsilon",  "𐑷"),
    ("Omega_dzlig",         "𐑭"),
    ("Ω_dzlig",             "𐑭"),
    ("Omega_crtwo",         "𐑴"),
    ("Ω_crtwo",             "𐑴"),
    ("Omega_turna",         "𐑟"),
    ("Ω_turna",             "𐑟"),
    ("Omega_NA",            "𐑟"),
    ("Omega_Z2",            "𐑴"),
    ("Omega_Z",             "𐑭"),
    ("Omega_0",             "𐑷"),
    ("D_invomega",          "𐑼"),
    ("D_turnthree",         "𐑨"),
    ("D_triangle",          "𐑨"),
    ("D_wedge",             "𐑛"),
    ("D_infty",             "𐑼"),
    ("D_odot",              "𐑦"),
    ("D_omega",             "𐑦"),
    ("Ð_omega",             "𐑦"),
    ("Ð_turnthree",         "𐑨"),
    ("Ð_invomega",          "𐑼"),
    ("Ð_wynn",              "𐑛"),
    ("T_commatailz",        "𐑶"),
    ("Þ_commatailz",        "𐑶"),
    ("T_bullseye",          "𐑥"),
    ("Þ_bullseye",          "𐑥"),
    ("T_boxtimes",          "𐑶"),
    ("T_network",           "𐑡"),
    ("T_bowtie",            "𐑥"),
    ("T_nrleg",             "𐑡"),
    ("Þ_nrleg",             "𐑡"),
    ("T_invscr",            "𐑰"),
    ("Þ_invscr",            "𐑰"),
    ("T_openo",             "𐑸"),
    ("Þ_openo",             "𐑸"),
    ("T_odot",              "𐑸"),
    ("T_in",                "𐑰"),
    ("R_subrightarrow",     "𐑩"),
    ("Ř_subrightarrow",     "𐑩"),
    ("R_lyoghlig",          "𐑾"),
    ("Ř_lyoghlig",          "𐑾"),
    ("R_downstep",          "𐑽"),
    ("Ř_downstep",          "𐑽"),
    ("R_dagger",            "𐑽"),
    ("R_super",             "𐑩"),
    ("R_cat",               "𐑑"),
    ("R_ctz",               "𐑑"),
    ("Ř_ctz",               "𐑑"),
    ("R_lr",                "𐑾"),
    ("P_doublebarpipe",     PLACEHOLDER),
    ("Φ_doublebarpipe",     PLACEHOLDER),
    ("P_subdoublearrow",    "𐑯"),
    ("Φ_subdoublearrow",    "𐑯"),
    ("P_pipevar",           "𐑬"),
    ("Φ_pipevar",           "𐑬"),
    ("P_upsilon",           "𐑿"),
    ("Φ_upsilon",           "𐑿"),
    ("P_aolig",             "𐑗"),
    ("Φ_aolig",             "𐑗"),
    ("P_pm_sym",            PLACEHOLDER),
    ("P_asym",              "𐑗"),
    ("P_psi",               "𐑿"),
    ("P_pm",                "𐑬"),
    ("P_sym",               "𐑯"),
    ("F_hardsign",          "ƒ^ż"),
    ("ƒ_hardsign",          "ƒ^ż"),
    ("F_beltl",             "ƒ^ì"),
    ("ƒ_beltl",             "ƒ^ì"),
    ("F_hbar",              "ƒ^ż"),
    ("F_eth",               "ƒ^ð"),
    ("F_ell",               "ƒ^ì"),
    ("F_dh",                "ƒ^ð"),
    ("K_frtailgamma",       "Ç^-"),
    ("Ç_frtailgamma",       "Ç^-"),
    ("K_teshlig",           "Ç^Ù"),
    ("Ç_teshlig",           "Ç^Ù"),
    ("K_turnm",             "Ç^W"),
    ("Ç_turnm",             "Ç^W"),
    ("K_lambda",            "Ç^λ"),
    ("K_schwa",             "Ç^@"),
    ("Ç_schwa",             "Ç^@"),
    ("K_MBL",               "Ç^λ"),
    ("K_fast",              "Ç^-"),
    ("K_mod",               "Ç^W"),
    ("K_slow",              "Ç^@"),
    ("K_trap",              "Ç^Ù"),
    ("G_revapostrophe",     "𐑲"),
    ("Γ_revapostrophe",     "𐑲"),
    ("G_gimel",             "𐑔"),
    ("G_aleph",             "𐑲"),
    ("G_gamma",             "𐑔"),
    ("G_beth",              "𐑚"),
    ("G_beta",              "𐑚"),
    ("H_invscripta",        "𐑫"),
    ("Ħ_invscripta",        "𐑫"),
    ("H_toneletterstem",    "𐑒"),
    ("Ħ_toneletterstem",    "𐑒"),
    ("H_turntwo",           "𐑖"),
    ("Ħ_turntwo",           "𐑖"),
    ("H_closeomega",        "𐑓"),
    ("Ħ_closeomega",        "𐑓"),
    ("H_inf",               "𐑫"),
    ("S_doublebaresh",      "𐑙"),
    ("Σ_doublebaresh",      "𐑙"),
    ("S_ltailm",            "𐑳"),
    ("Σ_ltailm",            "𐑳"),
    ("S_n_m",               "𐑳"),
    ("S_n_n",               "𐑕"),
    ("S_1_1",               "𐑙"),
    ("S_ctn",               "𐑕"),
    ("Σ_ctn",               "𐑕"),
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
    # Resolve PLACEHOLDER → 𐑹 or 𐑹} depending on f-string context
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
