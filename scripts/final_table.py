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

# Extra: non-\text entries
for short, (char, name) in [('dh', ('ð', 'dh')), ('thorn', ('þ', 'thorn')),
    ('openo_bar', ('l', 'openo')), ('schwa_plain', ('e', 'schwa')),  
    ('esh_plain', ('s', 'esh')), ('yogh_plain', ('`', 'yogh')), 
    ('eth_plain', ('d', 'eth'))]:
    pass  # keeping them in mind

# Final assignments. Each: (Primitive, Subtype, TeX_name, Char, Nature, Sound)
FINAL = [
    # D
    ("D", "wedge", "\\textwynn", "ß",
     "Wynn is the Old English letter for W — a wedge-shaped runic character with a pointed apex that visually evokes the wedge/cone shape of a zero-dimensional boundary.",
     "\"Wynn\" begins with /w/, matching the initial onset of \"wedge\"; both share the labial-velar approximant."),
    
    ("D", "triangle", "\\textturnthree", "C",
     "Three turns = three sides of a triangle; the turned character suggests the reorientation of perspective needed to perceive triangular dimensionality.",
     "\"Turnthree\" contains /θri/, directly echoing the \"tri-\" syllable /traɪ/ of \"triangle\" — three-number essence."),
    
    ("D", "infty", "\\textinvscripta", "!",
     "Script 'a' with inversion suggests unbounded continuous variation — the infinite scroll of a field-theoretic dimension.",
     "\"Invscripta\" begins with /ɪnv/, the /ɪn/ onset of \"in-fin-ity\"; the script suggests flowing continuity."),
    
    ("D", "odot", "\\textomega", "ω",
     "Omega Ω is a closed loop — the dot of imscriptive self-containment, where the state-space writes itself.",
     "\"Omega\" begins with /oʊ/, the long O sound of \"odot\"; omega is the last letter, as odot is the terminal D."),

    # T
    ("T", "network", "\\textnrleg", "6",
     "The n-r leg suggests branching limbs intertwining in a network topology — each node a crossing of paths.",
     "\"Nr\" begins with /n/ like \"network\"; \"leg\" = a branching limb extending from a node."),
    
    ("T", "in", "\\textinvomega", ";",
     "Inverted omega suggests inside-ness — containment within the loop, the topology of inclusion.",
     "\"Inv\" directly echoes /ɪn/, the entire sound of \"in\"; inversion = turning into the interior."),
    
    ("T", "bowtie", "\\textbullseye", "ò",
     "Concentric rings converging on a center — the crossing-point (bowtie knot) where lines of force intersect.",
     "\"Bull\" begins with /b/, matching the /b/ onset of \"bowtie\"; the 'eye' is the crossing singularity."),
    
    ("T", "boxtimes", "\\textcommatailz", "Þ",
     "Comma with tail-z suggests crossing strokes that bound a region — the ⊗ box product with a tailed boundary.",
     "\"Comma\" evokes the \"×\" (times) crossing shape; \"tail-z\" suggests the enclosing box edges."),
    
    ("T", "odot", "\\textopeno", "O",
     "Open O is an unclosed circle — the openness of self-referential imscriptive topology that always writes itself open.",
     "\"Openo\" begins with /oʊ/, the O sound of \"odot\"; the open form mirrors topology's self-containment."),

    # R
    ("R", "super", "\\textsubrightarrow", "¯",
     "Rightward arrow → supervenience's one-way direction — lower levels determine higher, never the reverse.",
     "\"Sub\" and \"sup\" share /sʌ/; the rightward arrow suggests the directed upward mapping of supervenience."),
    
    ("R", "cat", "\\textctz", "ý",
     "C-t-z ligature — categorical composition of morphisms chaining in a functorial category.",
     "\"Ct\" begins with /k/ like \"cat\" (category); the ligature = the composition of arrows in a functor."),
    
    ("R", "dagger", "\\textdownstep", "Ť",
     "Downward step icon — the adjoint functor descends, reversing direction like the † (dagger) in adjunction.",
     "\"Downstep\" begins with /d/, matching /d/ of \"dagger\"; the step down = the adjoint's reversal of direction."),
    
    ("R", "lr", "\\textlyoghlig", "Ð",
     "Ligature joining L and yogh — two letters bound into one bidirectional feedback loop.",
     "\"Lyoghlig\" phonetically combines /l/ and /jɒɡ/, echoing the two letters \"l\" and \"r\" in \"l-r\"."),

    # P
    ("P", "asym", "\\textaolig", "\"",
     "A-O ligature joined into one symbol — asymmetry as the absence of any dividing symmetry.",
     "\"Aolig\" begins with /eɪ/, the long A of \"asym\" (a-symmetric = without symmetry)."),
    
    ("P", "psi", "\\textupsilon", "υ",
     "Upsilon Υ — the Greek letter directly adjacent to psi (Ψ) in the alphabet; both denote quantum states.",
     "\"Upsilon\" contains /psɪl/ — echoing the /psaɪ/ of \"psi\"; both are Greek letters for wavefunctions."),
    
    ("P", "pm", "\\textpipevar", "F",
     "Vertical pipe | — the vertical stroke shared by plus (+) and minus (−); var = variant of the ± symbol.",
     "\"Pipevar\" begins with /p/ like \"pm\"; the pipe is the vertical spine of + and −."),
    
    ("P", "sym", "\\textsubdoublearrow", "˙",
     "Double arrow ↔ — full symmetry means bidirectional mapping; the two heads mirror each other.",
     "\"Sub\" shares /s/ with \"sym\"; the double arrow is the symmetric reflection of a single arrow."),
    
    ("P", "pm_sym", "\\textdoublebarpipe", "}",
     "Double bar + pipe = two symmetries superimposed — the Frobenius Z2 and the full symmetry together.",
     "\"Double\" = duality of pm + sym; \"pipe\" = the vertical bar of ±; together = Frobenius-special symmetry."),

    # F
    ("F", "ell", "\\textbeltl", "ì",
     "Belt with 'l' — classical determinism constrains/belts the system; no quantum superposition escapes.",
     "\"Beltl\" ends with /l/, precisely the /ɛl/ sound of \"ell\"; belt = constraint."),
    
    ("F", "eth", "\\textdh", "ð",
     "DH ð is the actual IPA character for the voiced dental fricative — the eth sound itself.",
     "\"DH\" directly represents /ɛð/ — the phoneme \"eth\" in IPA. Sound and letter are identical."),
    
    ("F", "hbar", "\\texthvlig", "ß",
     "H-V ligature — hv visually evokes ℏ (h-bar), the quantum of action with coherence across the bar.",
     "\"Hv\" begins with /h/ like \"hbar\"; the ligature = the bar crossing through h."),

    # K
    ("K", "fast", "\\textfrtailgamma", "-",
     "Gamma with a tail running fast (fr-) — rapid kinetics, short relaxation time τ ≪ T.",
     "\"Fr\" begins with /f/ like \"fast\"; the tail = the trajectory of rapid motion."),
    
    ("K", "mod", "\\textturnm", "W",
     "Turned M — moderate kinetics (τ ∼ T); neither upright (fast) nor inverted (trap); the turn is the balance.",
     "\"Turnm\" contains /m/, the /mɒd/ onset of \"mod\"erate; turned = neither extreme."),
    
    ("K", "slow", "\\textschwa", "@",
     "Schwa ə — the unstressed, lazy central vowel; slow, near-equilibrium kinetics with τ ≫ T.",
     "\"Schwa\" /ʃwɑ/ has the sibilant /ʃ/ approximating /s/ of \"slow\"; schwa = relaxed = slow."),
    
    ("K", "trap", "\\textteshlig", "Ù",
     "T-Esh ligature — the /tr/ consonant cluster is itself a trap for the tongue, arrested motion.",
     "\"Tesh\" begins with /tɛʃ/ — the /t/ and /ʃ/ capture the onset of \"trap\"; ligature = stuck together."),
    
    ("K", "MBL", "\\textlambda", "λ",
     "Lambda λ — Greek L, for Many-Body Localized (the L = localization in MBL).",
     "\"Lambda\" contains /læm/ — the /l/ and /m/ that sound the letters L and M in \"MBL\"."),

    # G
    ("G", "beth", "\\textbeta", "β",
     "Beta β — Hebrew beth (ב) means 'house'; beta is the second Greek letter, its direct cognate.",
     "\"Beta\" (/biːtə/ or /beɪtə/) is nearly homophonous with \"beth\" (/bɛθ/ or /beɪt/)."),
    
    ("G", "gimel", "\\textgamma", "γ",
     "Gamma γ — third Greek letter, analogue of Hebrew gimel (ג); both mean 'camel'.",
     "\"Gamma\" shares initial /ɡ/ with \"gimel\"; both are third in their alphabets."),
    
    ("G", "aleph", "\\textrevapostrophe", "\\",
     "Reversed apostrophe ʻ — represents the glottal stop /ʔ/, the consonant of Hebrew aleph (א).",
     "\"Revapostrophe\" contains /ɛv/ and /ʔ/ quality; the reversed apostrophe is the standard IPA for aleph's sound."),

    # Gamma
    ("Gamma", "and", "\\textcorner", "^",
     "Corner ⌜ — the conjunction of two lines meeting at 90°, all-simultaneous like logical AND.",
     "\"Corner\" ends with /ər/; the right-angle join = 'and' as simultaneous co-occurrence."),
    
    ("Gamma", "or", "\\textopeno", "O",
     "Open O — the space of alternatives, the disjunctive 'or' as an open choice among paths.",
     "\"Openo\" begins with /oʊ/, the vowel of \"or\"; the open circle = the space of alternate paths."),
    
    ("Gamma", "seq", "\\textsecstress", "­",
     "Secondary stress mark — a sequential ordering marker like linguistic stress in a word's syllables.",
     "\"Secstress\" begins with /sɛk/ — directly echoing /siːk/ or /sɛk/ of \"seq\" (sequential)."),
    
    ("Gamma", "broad", "\\textbullseye", "ò",
     "Wait — bullseye already used for T_bullseye. Need another.",
     "Fixing..."),

    # Let me recalculate what's left
]

print("=== USED SYMBOLS ===")
used = set()
for f in FINAL:
    name = f[2].replace('\\text', '')
    used.add(name)
    print(f"  {f[0]:6s} {f[1]:12s} → {f[2]:25s} '{f[3]}'")

print(f"\nTotal assignments: {len(FINAL)}")
