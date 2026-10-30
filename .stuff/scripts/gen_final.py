#!/usr/bin/env python3
import re

with open("psymbols.txt", "r", encoding="utf-8") as f:
    raw = f.read()

symbol_map = {}
for m in re.finditer(r'(\S)\s+\\(text[a-zA-Z]+)', raw):
    char = m.group(1)
    name = m.group(2)
    short = name[4:]
    if short not in symbol_map:
        symbol_map[short] = (char, name)

# ── Overrides ────────────────────────────────────────────────────────────────
# dh: actual IPA eth glyph (not in psymbols.txt TeX block)
symbol_map['dh'] = ('ð', 'dh')
# aolig: psymbols.txt proxy is " (U+0022) — use ɐ (U+0250 turned-A) to avoid quote escaping
symbol_map['aolig'] = ('ɐ', 'textaolig')
# revapostrophe: psymbols.txt proxy is \ (U+005C) — use ʔ (U+0294 glottal stop = IPA aleph)
symbol_map['revapostrophe'] = ('ʔ', 'textrevapostrophe')
# secstress: psymbols.txt proxy is U+00AD soft hyphen (invisible) — use ˌ (U+02CC IPA secondary stress)
symbol_map['secstress'] = ('ˌ', 'textsecstress')

# ── Primitive Unicode keys (used in IG_catalog.json) ─────────────────────────
PRIM_CHARS = {
    'D':     'Ð',
    'T':     'Þ',
    'R':     'Ř',
    'P':     'Φ',
    'F':     'ƒ',
    'K':     'Ç',
    'G':     'Γ',
    'Gamma': 'ɢ',
    'Phi':   '⊙',
    'H':     'Ħ',
    'S':     'Σ',
    'Omega': 'Ω',
}

# ── Assignments: (primitive, subtype, symbol_name, reasoning_nature, reasoning_sound)
FINAL = []

def add(prim, sub, sym, nature, sound):
    FINAL.append((prim, sub, sym, nature, sound))

# D — Dimensionality (F4)
add("D","wedge",   "wynn",     "Wynn = OE W letter, wedge-shaped runic apex",          '"Wynn" /wɪn/ matches /w/ onset of "wedge"')
add("D","triangle","turnthree","Three turns = three sides of triangle",                 '"Turnthree" /θri/ echoes "tri-" of "triangle"')
add("D","infty",   "invomega", "Inverted omega = unbounded infinite loop",              '"Inv" = /ɪn/, onset of "in-fin-ity"')
add("D","odot",    "omega",    "Omega = closed loop imscriptive self-containment",      '"Omega" /oʊ/ matches O of "odot"')

# T — Topology (F5)
add("T","network", "nrleg",     "N-R leg = branching network limbs",                   '"Nr" /n/ = onset of "network"; leg=branch')
add("T","in",      "invscr",    "Inverted script = containment topology",              '"Inv" = /ɪn/, sound of "in"')
add("T","bowtie",  "bullseye",  "Concentric target = crossing center of bowtie knot",  '"Bull" /b/ = onset of "bowtie"')
add("T","boxtimes","rectangle", "Rectangle = bounding box of × product",               '"Rect" /r/ onset + box shape = boxtimes geometry')
add("T","odot",    "openo",     "Open O = unclosed circle of self-referential topology",'"Openo" /oʊ/ = O sound of "odot"')

# R — Relational Mode (F4)
add("R","super",  "subrightarrow","Rightward arrow = one-way supervenience mapping",   '"Sub" /sʌ/ shared with "super"; arrow=dir')
add("R","cat",    "ctz",          "C-t-z ligature = categorical composition",          '"Ct" /k/ = onset of "cat"(egory)')
add("R","dagger", "downstep",     "Downward step = adjoint reversal (dagger functor)", '"Down" /d/ = /d/ of "dagger"; step=reversal')
add("R","lr",     "qplig",        "Q-P ligature = mirror-image letter pair = bilateral L-R",'"QP" mirrors L↔R: q is p reversed, as L and R are lateral inverses')

# P — Parity/Symmetry (F5)
add("P","asym",   "aolig",         "A-O ligature = asymmetry as absence of symmetry",  '"Ao" /eɪ/ = long A of "asym" [char: ɐ turned-A]')
add("P","psi",    "upsilon",       "Upsilon = Greek letter adjacent to psi in alphabet",'"Upsilon" /psɪl/ echoes /psaɪ/ of "psi"')
add("P","pm",     "pipevar",       "Vertical pipe = the stroke shared by + and −",     '"Pipe" /p/ = onset of "pm"')
add("P","sym",    "subdoublearrow","Double arrow = symmetric bidirectional mapping",    '"Sub" /s/ shared with "sym"; double=reflect')
add("P","pm_sym", "doublebarpipe", "Double bar+pipe = Frobenius-special (pm+sym)",     '"Double"=duality; "pipe"=± vertical')

# F — Fidelity (F3)
add("F","ell",  "beltl",    "Belt+L = classical determinism constrains",               '"Beltl" /l/ = /ɛl/ of "ell"; belt=bind')
add("F","eth",  "dh",       "DH = actual IPA char for voiced eth /ð/",                '"DH" directly = /ɛð/, the eth phoneme')
add("F","hbar", "hardsign", "Hard sign = rigid coherence barrier blocks decoherence",  '"Hard" /h/ = onset of "hbar"; sign=mark')

# K — Kinetics (F5)
add("K","fast","frtailgamma","Gamma with fr-tail = fast trajectory short τ",           '"Fr" /f/ = onset of "fast"; tail=motion')
add("K","mod", "turnm",     "Turned M = moderate kinetics τ∼T",                        '"Turnm" /m/ = onset of "mod"erate')
add("K","slow","schwa",     "Schwa = unstressed lazy vowel = slow equilibrium",         '"Schwa" /ʃwɑ/ sibilant ≈ /s/ of "slow"')
add("K","trap","teshlig",   "T-Esh ligature = trapped /tr/ consonant cluster",         '"Tesh" /tɛʃ/ captures /tr/ of "trap"')
add("K","MBL", "lambda",    "Lambda = Greek L for Many-Body Localized",                '"Lambda" /læm/ = L and M of "MBL"')

# G — Scope/Granularity (F3)
add("G","beth", "beta",         "Beta = Greek cognate of Hebrew beth",                 '"Beta" near-homophone of "beth"')
add("G","gimel","gamma",        "Gamma = Greek analogue of gimel, 3rd letter",         '"Gamma" /ɡ/ = onset of "gimel"')
add("G","aleph","revapostrophe","Rev apostrophe = glottal stop = aleph",               '"Revapostrophe" /ʔ/ = glottal stop = aleph [char: ʔ]')

# Gamma — Coupling (F4)
add("Gamma","and",  "corner",        "Corner = two lines meeting = logical AND",       '"Corner" join = simultaneity of AND')
add("Gamma","or",   "spleftarrow",   "Left arrow = alternate path in disjunction",     '"Spleftarrow" /sp/ = disjunction branch')
add("Gamma","seq",  "secstress",     "Secondary stress = ordered sequence",            '"Secstress" /sɛk/ = /sɛk/ of "seq" [char: ˌ U+02CC]')
add("Gamma","broad","doublevertline","Double vertical lines = broadcast to all",        '"Doublevertline" /dʌb/ evokes "br" of "broad"')

# Phi — Criticality (F5)
add("Phi","sub",       "softsign",       "Soft sign = below critical threshold",       '"Soft" /sɒf/ = /s/ of "sub"(below)')
add("Phi","c",         "ctyogh",         "C-t-yogh = self-modeling loop closed",       '"Ctyogh" /k/ = /k/ of critical "c"; yogh=loop')
add("Phi","c_complex", "closerevepsilon","Closed reversed epsilon = complex-plane crit",'"Closerevepsilon" /riːvɛps/ echoes "complex"')
add("Phi","EP",        "revepsilon",     "Reversed epsilon = exceptional point",        '"Revepsilon" /rɛvɛps/ = /ɛp/ of "EP"')
add("Phi","super",     "upstep",         "Upward step = supercritical crossing",        '"Upstep" /ʌp/ = "sup" without /s/; up=above')

# H — Chirality (F4)
add("H","0",  "closeomega",    "Closed omega = zero memory closed temporal loop",      '"Closeomega" /kloʊz/ evokes zero as closed')
add("H","1",  "toneletterstem","Tone letter stem = one stroke one step",               '"Tone" /toʊn/ contains /wʌn/ echo of "one"')
add("H","2",  "turntwo",       "Turned 2 = two-step Markov memory depth",              '"Turntwo" /tuː/ = /tuː/ of "two"')
add("H","inf","invscripta",    "Inverted script a = unbounded infinite memory",         '"Inv" /ɪn/ = /ɪn/ of "inf"(inite)')

# S — Stoichiometry (F3)
add("S","one_one","doublebaresh","Double-bar esh = one-to-one paired strokes",          '"Doublebaresh" /dʌb/ evokes paired 1:1')
add("S","n_n",    "ctn",        "C-t-n ligature = many identical n:n",                 '"Ctn" /n/ = repeated N sound of "n:n"')
add("S","n_m",    "rtailn",     "Retroflex N = n with tail = n:m asymmetric excess",   '"Rtailn" /n/ sound preserved; tail=extra m')

# Omega — Topological Invariant (F4)
add("Omega","0", "closeepsilon","Closed epsilon = trivial no topological invariant",    '"Closeepsilon" closes = zero invariant')
add("Omega","Z2","crtwo",       "Curly 2 = Z2 binary parity protection",               '"Crtwo" = /tuː/ = "two" of Z2')
add("Omega","Z", "dzlig",       "DZ ligature = integer Z winding number",              '"Dzlig" /z/ = /zɛd/ of "Z"; ligature=twist')
add("Omega","NA","turna",       "Turned a = non-Abelian braiding twists",              '"Turna" /eɪ/ = /eɪ/ of "NA" (en-ay)')

# ── Generate table ────────────────────────────────────────────────────────────
used_syms  = {}   # tex_name → (prim, sub)
used_chars = {}   # rendered_char → (prim, sub)
dupes_sym  = []
dupes_char = []

print("=" * 110)
print("COMPLETE PHONETIC SYMBOL ASSIGNMENT — IMSCRIBING GRAMMAR PRIMITIVES")
print("=" * 110)
print()
print(f"{'Symbol_symbol ID':16s} {'TeX Symbol':28s} {'Char'} {'Nature & Sound'}")
print("-" * 110)

for prim, sub, sym, nature, sound in FINAL:
    if sym in symbol_map:
        char, full = symbol_map[sym]
        tex = f"\\{full}" if full.startswith('text') else f"\\{full}"
    else:
        char = '?'
        tex = f"\\{sym}"

    prim_char = PRIM_CHARS[prim]
    id_str = f"{prim_char}_{char}"

    if sym in used_syms:
        dupes_sym.append((prim, sub, sym, f"first: {used_syms[sym]}"))
    used_syms[sym] = f"{prim}_{sub}"

    if char in used_chars:
        dupes_char.append((prim, sub, char, f"first: {used_chars[char]}"))
    used_chars[char] = f"{prim}_{sub}"

    print(f"{id_str:16s} {tex:28s} {char:4s}  {nature}")
    print(f"{'':16s} {'':28s} {'':4s}  {sound}")
    print()

if dupes_sym:
    print(f"\n*** DUPLICATE TeX NAMES: {dupes_sym} ***")
if dupes_char:
    print(f"\n*** DUPLICATE RENDERED CHARS: {dupes_char} ***")
if not dupes_sym and not dupes_char:
    print(f"\nAll {len(FINAL)} assignments: unique TeX names AND unique rendered chars.")
    print(f"Total unique Symbol_symbol IDs: {len(used_syms)}")

# ── Emit machine-readable RENAME mapping (old phonetic-name → new Symbol_symbol)
print()
print("─" * 110)
print("OLD → NEW RENAME MAPPING")
print("─" * 110)

# Map from old catalog names (PrimKey_texname) to new (PrimKey_char)
OLD_NAMES = {
    "D":     {"wedge":"wynn","triangle":"turnthree","infty":"invomega","odot":"omega"},
    "T":     {"network":"nrleg","in":"invscr","bowtie":"bullseye","boxtimes":"commatailz","odot":"openo"},
    "R":     {"super":"subrightarrow","cat":"ctz","dagger":"downstep","lr":"lyoghlig"},
    "P":     {"asym":"aolig","psi":"upsilon","pm":"pipevar","sym":"subdoublearrow","pm_sym":"doublebarpipe"},
    "F":     {"ell":"beltl","eth":"dh","hbar":"hvlig"},
    "K":     {"fast":"frtailgamma","mod":"turnm","slow":"schwa","trap":"teshlig","MBL":"lambda"},
    "G":     {"beth":"beta","gimel":"gamma","aleph":"revapostrophe"},
    "Gamma": {"and":"corner","or":"spleftarrow","seq":"secstress","broad":"doublevertline"},
    "Phi":   {"sub":"softsign","c":"ctc","c_complex":"closerevepsilon","EP":"revepsilon","super":"upstep"},
    "H":     {"0":"closeomega","1":"toneletterstem","2":"turntwo","inf":"invscripta"},
    "S":     {"one_one":"doublebaresh","n_n":"ctn","n_m":"scn"},
    "Omega": {"0":"closeepsilon","Z2":"crtwo","Z":"dzlig","NA":"turna"},
}

for entry in FINAL:
    prim, sub, new_sym, _, _ = entry
    prim_char = PRIM_CHARS[prim]
    new_char = symbol_map[new_sym][0]
    new_id = f"{prim_char}_{new_char}"

    old_sym = OLD_NAMES.get(prim, {}).get(sub, new_sym)
    old_id = f"{prim_char}_{old_sym}"

    if old_id != new_id:
        print(f"  {old_id:24s} → {new_id}")
