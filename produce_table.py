import re, json

with open("psymbols.txt", "r", encoding="utf-8") as f:
    raw = f.read()

# Full symbol map including non-\text entries
symbol_map = {}
for m in re.finditer(r'(\S)\s+\\(text[a-zA-Z]+)', raw):
    char = m.group(1)
    name = m.group(2)
    short = name[4:]
    if short not in symbol_map:
        symbol_map[short] = (char, '\\' + name)

# Add non-\text entries
for entry in [
    ('dh', 'ð'), ('DH', 'Ð'), ('thorn', 'þ'), ('openo_bar', None),
    ('schwa_plain', None), ('esh_plain', None), ('yogh_plain', None),
    ('eth_plain', None), ('flap', None), ('glottal', None),
    ('pwedge', None), ('rotm', None), ('rotr', None), ('rotw', None),
    ('rotvara', None), ('roty', None), ('vod', None), ('voicedh', None),
    ('ibar', None), ('rotOmega', None), ('varomega', None), ('varopeno', None)
]:
    pass  # non-text entries, not needed

# Manual override for dh (non-\text command)
symbol_map['dh'] = ('ð', '\\dh')

# All subtype names to assign
all_subtypes = {
    'D': ['wedge', 'triangle', 'infty', 'odot'],
    'T': ['network', 'in', 'bowtie', 'boxtimes', 'odot'],
    'R': ['super', 'cat', 'dagger', 'lr'],
    'P': ['asym', 'psi', 'pm', 'sym', 'pm_sym'],
    'F': ['ell', 'eth', 'hbar'],
    'K': ['fast', 'mod', 'slow', 'trap', 'MBL'],
    'G': ['beth', 'gimel', 'aleph'],
    'Gamma': ['and', 'or', 'seq', 'broad'],
    'Phi': ['sub', 'c', 'c_complex', 'EP', 'super'],
    'H': ['0', '1', '2', 'inf'],
    'S': ['Σ_doublebaresh', 'Σ_ctn', 'Σ_ltailm'],
    'Omega': ['0', 'Z2', 'Z', 'NA']
}

# My curated assignments ensuring ALL symbols are unique
# (primitive, subtype, symbol_name, display_char, nature, sound)
TABLE = [
    # ===== D (Dimension) =====
    ("D", "wedge", "wynn", "ß",
     "Wynn = Old English W — wedge-shaped runic apex",
     "\"Wynn\" /wɪn/ matches /w/ onset of \"wedge\""),
    ("D", "triangle", "turnthree", "C",
     "Three turns = three sides of a triangle",
     "\"Turnthree\" contains /θri/ echoing \"tri-\" of \"triangle\""),
    ("D", "infty", "invomega", ";",
     "Inverted omega suggests unbounded infinite loop",
     "\"Inv\" = /ɪn/, onset of \"in-fin-ity\""),
    ("D", "odot", "omega", "ω",
     "Omega = closed loop; imscriptive self-containment",
     "\"Omega\" /oʊ/ matches the O of \"odot\""),

    # ===== T (Topology) =====
    ("T", "network", "nrleg", "6",
     "N-R leg suggests branching network limbs",
     "\"Nr\" /n/ = onset of \"network\"; leg = branch limb"),
    ("T", "in", "invscr", "K",
     "Inverted script suggests containment topology",
     "\"Inv\" = /ɪn/, sound of \"in\""),
    ("T", "bowtie", "bullseye", "ò",
     "Concentric target = crossing center of bowtie knot",
     "\"Bull\" /bʊl/ = /b/ onset of \"bowtie\""),
    ("T", "boxtimes", "commatailz", "Þ",
     "Comma + tail-z = crossing strokes of ⊗ box product",
     "\"Comma\" evokes \"×\" (times); tail = box boundary"),
    ("T", "odot", "openo", "O",
     "Open O = unclosed circle of self-referential topology",
     "\"Openo\" /oʊ/ matches the O sound of \"odot\""),

    # ===== R (Relational mode) =====
    ("R", "super", "subrightarrow", "¯",
     "Rightward arrow = one-way supervenience mapping",
     "\"Sub\" /sʌ/ shared with \"sup\" (super); arrow = direction"),
    ("R", "cat", "ctz", "ý",
     "C-t-z ligature = categorical composition of morphisms",
     "\"Ct\" /k/ = onset of \"cat\" (category)"),
    ("R", "dagger", "downstep", "Ť",
     "Downward step = adjoint's reversal († dagger functor)",
     "\"Down\" /d/ matches /d/ of \"dagger\"; step = reversal"),
    ("R", "lr", "lyoghlig", "Ð",
     "Ligature of L+yogh = bidirectional L-R coupling",
     "\"Lyogh\" evokes L and R letters of \"l-r\""),

    # ===== P (Parity/Symmetry) =====
    ("P", "asym", "aolig", "\"",
     "A-O ligature = asymmetry as absence of symmetry break",
     "\"Ao\" /eɪ/ = long A of \"asym\""),
    ("P", "psi", "upsilon", "υ",
     "Upsilon Υ = Greek letter adjacent to psi (Ψ) in alphabet",
     "\"Upsilon\" contains /psɪl/ echoing /psaɪ/ of \"psi\""),
    ("P", "pm", "pipevar", "F",
     "Vertical pipe | = the stroke shared by + and −",
     "\"Pipe\" /p/ = onset of \"pm\""),
    ("P", "sym", "subdoublearrow", "˙",
     "Double arrow ↔ = symmetric bidirectional mapping",
     "\"Sub\" /s/ shared with \"sym\"; double arrow = reflection"),
    ("P", "pm_sym", "doublebarpipe", "}",
     "Double bar + pipe = Frobenius-special (pm + sym combined)",
     "\"Double\" = duality; \"pipe\" = ± vertical stroke"),

    # ===== F (Fidelity) =====
    ("F", "ell", "beltl", "ì",
     "Belt with L = classical constraint on determinism",
     "\"Beltl\" ends with /l/, the /ɛl/ of \"ell\""),
    ("F", "eth", "dh", "ð",
     "DH ð = actual IPA char for voiced dental fricative (eth)",
     "\"DH\" directly represents /ɛð/, the eth phoneme"),
    ("F", "hbar", "hvlig", "ß",
     "H-V ligature = ℏ (h-bar), quantum coherence symbol",
     "\"Hv\" /h/ = onset of \"hbar\"; ligature = bar through h"),

    # ===== K (Kinetics) =====
    ("K", "fast", "frtailgamma", "-",
     "Gamma with fr- tail = fast trajectory, short τ",
     "\"Fr\" /f/ = onset of \"fast\"; tail = motion"),
    ("K", "mod", "turnm", "W",
     "Turned M = moderate kinetics, neither fast nor frozen",
     "\"Turnm\" /m/ = onset of \"mod\"erate"),
    ("K", "slow", "schwa", "@",
     "Schwa = unstressed lazy vowel = slow equilibrium",
     "\"Schwa\" /ʃwɑ/ sibilant approximates /s/ of \"slow\""),
    ("K", "trap", "teshlig", "Ù",
     "T-Esh ligature = trapped consonant cluster /tr/",
     "\"Tesh\" /tɛʃ/ captures /tr/ onset of \"trap\""),
    ("K", "MBL", "lambda", "λ",
     "Lambda λ = Greek L for Localization in Many-Body Localization",
     "\"Lambda\" /læm/ = L and M sounds of \"MBL\""),

    # ===== G (Scope) =====
    ("G", "beth", "beta", "β",
     "Beta β = Greek cognate of Hebrew beth (ב)",
     "\"Beta\" is near-homophone of \"beth\""),
    ("G", "gimel", "gamma", "γ",
     "Gamma γ = Greek analogue of gimel, 3rd letter",
     "\"Gamma\" /ɡ/ = onset of \"gimel\""),
    ("G", "aleph", "revapostrophe", "\\",
     "Reversed apostrophe = IPA glottal stop /ʔ/ = aleph",
     "\"Revapostrophe\" /ɛv/ and /ʔ/ evoke aleph's silent onset"),

    # ===== Gamma (Coupling) =====
    ("Gamma", "and", "corner", "^",
     "Corner ⌜ = two lines meeting = logical AND",
     "\"Corner\" ends with schwa; the join = simultaneity of AND"),
    ("Gamma", "or", "spleftarrow", "˝",
     "Leftward arrow = alternate direction/path in disjunction",
     "\"Spleftarrow\" /sp/ evokes /ɔr/ through the leftward branch"),
    ("Gamma", "seq", "secstress", "­",
     "Secondary stress mark = ordered sequence of syllables",
     "\"Secstress\" /sɛk/ = /sɛk/ of \"seq\" (sequential)"),
    ("Gamma", "broad", "doublevertline", "Ş",
     "Double vertical lines = broadcast to all recipients",
     "\"Doublevertline\" /dʌb/ evokes \"br\" of \"broad\" through the spread of parallel lines"),

    # ===== Phi (Criticality) =====
    ("Phi", "sub", "softsign", "ž",
     "Soft sign = below threshold, not yet critical",
     "\"Soft\" /sɒf/ shares /s/ with \"sub\" (below)"),
    ("Phi", "c", "ctc", "C",
     "C-t-c ligature = critical self-modeling point",
     "\"Ctc\" /k/ = /k/ of critical \"c\""),
    ("Phi", "c_complex", "closerevepsilon", "Æ",
     "Closed reversed epsilon = complex-plane criticality",
     "\"Closerevepsilon\" /riːvɛps/ echoes \"complex\""),
    ("Phi", "EP", "revepsilon", "3",
     "Reversed epsilon = exceptional point (non-Hermitian degeneracy)",
     "\"Revepsilon\" /rɛvɛps/ begins with /ɛp/ = \"EP\""),
    ("Phi", "super", "sup", None,
     "Supercritical = above threshold, runaway",
     "Need a substitute..."),

    # Actually 'sup' is not in map. Let me use \textupstep 'Ţ'
    ("Phi", "super", "upstep", "Ţ",
     "Upward step = supercritical, crossing threshold upward",
     "\"Upstep\" /ʌp/ = \"sup\"'s /sʌp/ without the /s/; up = above"),

    # ===== H (Temporal depth) =====
    ("H", "0", "crtwo", "2",
     "Wait, crtwo = '2', not '0'. Let me use something circular.",
     "Fixing..."),

    # H_0: zero → circle. \textcloseomega 'Ñ'? \textcloseepsilon 'Å'?
    ("H", "0", "closeomega", "Ñ",
     "Closed omega = zero memory, no temporal depth, closed loop",
     "\"Closeomega\" /kloʊz/ evokes zero as a closed circle"),
    ("H", "1", "toneletterstem", "£",
     "Tone letter stem = one mark, one step of memory",
     "\"Toneletter\" /toʊn/ contains /wʌn/ echo of \"one\""),
    ("H", "2", "turntwo", "A",
     "Turned two = two-step memory, the turned form of 2",
     "\"Turntwo\" contains /tuː/, the sound of \"two\""),
    ("H", "inf", "invscripta", "!",
     "Inverted script a = unbounded infinite memory depth",
     "\"Inv\" /ɪn/ = /ɪn/ of \"inf\" (infinite)"),

    # ===== S (Stoichiometry) =====
    ("S", "Σ_doublebaresh", "doublebarpipe", "}",
     "Wait, doublebarpipe taken by P_doublebarpipe!",
     "Fixing..."),

    ("S", "Σ_doublebaresh", "doublebaresh", "S",
     "Double-bar esh = one-to-one pairing of two identical strokes",
     "\"Doublebaresh\" /dʌb/ = 'double' suggesting the 1:1 pairing"),
    ("S", "Σ_ctn", "Σ_ctn", None,
     "Need symbol with 'n' sound for n:n stoichiometry"),
    # Let me use \textnrleg '6' — already used for T_nrleg.
    # \textinvscr 'K' — used for T_invscr
    # \textomega... let me find an unused 'n' sound symbol
]

# Print available 'n' sounds
print("=== Available symbols starting with or containing 'n' ===")
used_symbols = set()
for entry in TABLE:
    if entry[3]:  # has char
        used_symbols.add(entry[2])

for short, (char, full) in sorted(symbol_map.items()):
    if (short.startswith('n') or 'n' in short[:3]) and short not in used_symbols:
        print(f"  {full:25s} '{char}' ({short})")

print(f"\n=== Used so far ({len(used_symbols)} symbols) ===")
for u in sorted(used_symbols):
    c, f = symbol_map.get(u, ('?', '?'))
    print(f"  {f:25s} '{c}' ({u})")

