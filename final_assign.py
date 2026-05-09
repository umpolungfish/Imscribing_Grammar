#!/usr/bin/env python3
"""
FINAL PHONETIC SYMBOL ASSIGNMENTS for Imscribing Grammar primitives.

Each entry: (primitive, subtype, phonetic_symbol_name, display_char, reasoning)
"""
import re, json

with open("psymbols.txt", "r", encoding="utf-8") as f:
    raw = f.read()

# Build comprehensive map of all phonetic symbols
symbol_map = {}
# \text... entries
for m in re.finditer(r'(\S)\s+\\(text[a-zA-Z]+)', raw):
    char = m.group(1)
    name = m.group(2)
    short = name[4:]
    if short not in symbol_map:
        symbol_map[short] = ('\\' + name, char)

# Non-\text entries from later tables
nontext = {
    'dh': 'ð', 'DH': 'Ð', 'thorn': 'þ', 'Thorn': 'Þ',
    'openo': 'l', 'schwa': 'e', 'esh': 's', 'yogh': '`',
    'eth': 'd', 'glottal': '?', 'pwedge': 'U', 'flap': 'f',
    'rotOmega': None, 'rotm': 'm', 'rotr': 'r', 'rotw': 'w',
    'rotvara': 'A', 'roty': 'y', 'varomega': '',
    'varopeno': 'C', 'hbar': None, 'pwedge': 'U',
    'vod': 'v', 'voicedh': 'h'
}
# Only add entries with known characters
nontext_valid = {k: v for k, v in nontext.items() if v and v.strip()}

# My final assignments
# Format: (primitive, subtype, symbol_name, display_char, nature_reason, sound_reason)

assignments = [
    # ===== D (Dimension) =====
    ("D", "wedge", "wynn", "ß",
     "Wynn is the old English letter for W — a wedge-shaped letter with pointed apex",
     "\"Wynn\" begins with /w/ sound, matching the initial of \"wedge\""),
    
    ("D", "triangle", "turnthree", "C",
     "\"Three\" evokes the three sides of a triangle; the turned shape suggests rotation of perspective",
     "\"Turnthree\" contains the /θri/ sound of \"three\", echoing the /traɪ/ of \"triangle\""),
    
    ("D", "infty", "invscripta", "!",
     "Script a suggests variable/continuous dimension; inverted form suggests unboundedness",
     "\"Inv\" sounds like the /ɪn/ in \"infty\" (infinity); the /skrɪp/ echoes the long /aɪ/"),
    
    ("D", "odot", "openo", "O",
     "Open O is a circle — the dot/point of imscriptive self-containment",
     "\"Openo\" begins with /oʊ/, the long O sound of \"odot\""),

    # ===== T (Topology) =====
    ("T", "network", "nrleg", "6",
     "The leg suggests branching, the n-r ligature intertwining paths — a network",
     "\"Nr\" begins with /n/ like \"network\"; \"leg\" suggests branching limbs"),
    
    ("T", "in", "invomega", ";",
     "Omega is a looping curve suggesting containment; inverted omega suggests being inside",
     "\"Inv\" directly echoes the /ɪn/ of \"in\""),
    
    ("T", "bowtie", "bullseye", "ò",
     "A bullseye is a crossing point — the target center where lines meet, like a bowtie knot",
     "\"Bullseye\" begins with /bʊl/, the /b/ matching \"bow\"; the target suggests the meeting point"),
    
    ("T", "boxtimes", "doublevertline", "Ş",
     "Double vertical lines suggest the parallel sides of a box; the structure evokes containment",
     "\"Double\" suggests multiplicity; \"vertline\" evokes the shape of a box's sides"),
    
    ("T", "odot", "omega", "ω",
     "Omega is a closed loop — self-referential closure for imscriptive topology",
     "\"Omega\" begins with /oʊ/, the long O of \"odot\""),

    # ===== R (Relational mode) =====
    ("R", "super", "subrightarrow", "¯",
     "Rightward arrow suggests directionality of supervenience — one-way upward mapping",
     "\"Sub\" and \"sup\" share the /sʌ/ initial; the arrow shows directedness"),
    
    ("R", "cat", "ctz", "ý",
     "The c-t-z ligature suggests categorical composition — morphisms chaining together",
     "\"Ct\" begins with /k/ like \"cat\"; the ligature suggests composition"),
    
    ("R", "dagger", "downstep", "Ť",
     "Downward step evokes the adjoint's descent — the dagger functor goes opposite direction",
     "\"D\" in \"downstep\" matches /d/ of \"dagger\"; the step suggests the adjoint's reversal"),
    
    ("R", "lr", "lyoghlig", "Ð",
     "Ligature joining two letters suggests bidirectional coupling — left-right feedback",
     "\"L\" and \"yogh\" together echo the /ɛl ɑr/ of \"l-r\"; ligature = joining"),

    # ===== P (Parity/Symmetry) =====
    ("P", "asym", "aolig", '"',
     "A ligature joins letters — asymmetry means no symmetry, yet the ligature is one shape",
     "\"Ao\" begins with /eɪ/ like \"a\" in \"asym\"; the ligature suggests unity of absence"),
    
    ("P", "psi", "upsilon", "υ",
     "Upsilon is the Greek υ — psi (ψ) and upsilon share the /ps ~ ʊ/ family of sounds",
     "\"Upsilon\" contains /psɪl/ — echoing the /psaɪ/ of \"psi\""),
    
    ("P", "pm", "primstress", '"',
     "Primary stress mark — a single mark like the plus-minus's vertical bar",
     "\"Prim\" begins with /pr/ — /pr/ echoes the /p/ of \"pm\""),
    # Wait, "primstress" (" was already used for asym. Need unique symbols!
    ("P", "pm", "pipevar", "F",
     "The pipe is a vertical bar — the plus-minus's vertical stroke",
     "\"Pipe\" begins with /p/ matching \"pm\""),
    
    ("P", "sym", "subdoublearrow", "˙",
     "Double arrow suggests the two-way nature of full symmetry — mappings in both directions",
     "\"Sym\" shares /s/ with \"sub\"; the double arrow is symmetric reflection"),
    
    ("P", "pm_sym", "doublebarpipe", "}",
     "Double bar + pipe = two symmetries superimposed — the Frobenius-special symmetry",
     "\"Double\" suggests duality; \"pipe\" = vertical line of ±; double = full symmetry"),

    # ===== F (Fidelity) =====
    ("F", "ell", "beltl", "ì",
     "Belt with L suggests binding — classical determinism constrains the system",
     "\"Beltl\" ends with /l/ — the /ɛl/ sound of \"ell\""),
    
    ("F", "eth", "dh", "ð",
     "DH is the ACTUAL IPA character for the voiced dental fricative — named \"eth\"",
     "\"DH\" IS the eth sound — /ɛð/ — directly matching \"eth\" in sound and letter"),
    
    ("F", "hbar", "hvlig", "ß",
     "H-V ligature suggests the h-bar (ℏ) — a ligature of h and the bar through it",
     "\"Hv\" begins with /h/ like \"hbar\"; the ligature evokes the crossed-h of ℏ"),

    # ===== K (Kinetics) =====
    ("K", "fast", "frtailgamma", "-",
     "Gamma with a tail suggesting a fast trajectory — the tail marks rapid motion",
     "\"Fr\" begins with /f/ like \"fast\"; tail suggests trajectory"),
    
    ("K", "mod", "ramshorns", "7",
     "Ram's horns curl in a moderate arc — not too tight (trap) nor too loose (fast)",
     "\"Mod\" has no direct phonetic match, but \"ram\" shares /m/; horns suggest resonance"),
    
    ("K", "slow", "schwa", "e",
     "Schwa is the relaxed, unstressed vowel — like slow, near-equilibrium kinetics",
     "\"Schwa\" shares /sl/... actually not. Let me reconsider.",
     ),

    # Actually I need to reconsider K_schwa. Let me use \textsubrightarrow? No that's taken by R_subrightarrow.
    # \texttslig (ţ)? "tslig" — "ts" has no relation to "slow"
    # What about something with "ow" or "lo"?
]

# Let me just show all assignments and fix K_schwa
# Let me look for symbols starting with 'sl' or containing 'low'
print("=== Search for 'slow' matches ===")
for short, (full, char) in sorted(symbol_map.items()):
    if 'sl' in short.lower() or 'low' in short.lower() or 'lo' in short.lower()[:4]:
        print(f"  {full:25s} '{char}'")

print("\n=== All 's' starting symbols ===")
for short, (full, char) in sorted(symbol_map.items()):
    if short.startswith('s') and len(short) < 12:
        print(f"  {full:25s} '{char}' ({short})")

