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

# My final curated assignments
# Format: (primitive, subtype, symbol_name, display_char, nature_reason, sound_reason)
assignments = []

used = set()

def add(prim, subtype, sym_name, disp_char, nature, sound):
    key = sym_name if sym_name.startswith('text') else sym_name
    if key in used:
        print(f"DUPLICATE: {sym_name} already used!")
        return
    used.add(key)
    assignments.append((prim, subtype, sym_name, disp_char, nature, sound))

# ===== D (Dimension) =====
add("D", "wedge", "wynn", "ß",
    "Wynn is the OE letter for W — a wedge-shaped runic character with pointed apex",
    '"Wynn" begins with /w/, matching the onset of "wedge"')

add("D", "triangle", "turnthree", "C",
    "Three turns = three sides; the turned shape evokes tri-dimensionality",
    '"Three" in "turnthree" echoes /θri/ within "triangle"')

add("D", "infty", "invscripta", "!",
    "Script a with inversion suggests unbounded variable — the infinite scroll",
    '"Inv" sounds like /ɪn/, the onset of "in-fin-ity"')

add("D", "odot", "omega", "ω",
    "Omega Ω is a closed loop — the dot of imscriptive self-containment",
    '"Omega" begins with /oʊ/, the long O of "odot"')

# ===== T (Topology) =====
add("T", "network", "nrleg", "6",
    "Leg suggests branching limbs; n-r ligature = intertwining paths = network",
    '"Nr" begins with /n/ like "network"; leg = branch')

add("T", "in", "invomega", ";",
    "Inverted omega suggests inside-ness — containment within the loop",
    '"Inv" directly echoes /ɪn/, the entire sound of "in"')

add("T", "bowtie", "bullseye", "ò",
    "Concentric rings converging on center — the crossing-point where lines meet",
    '"Bull" starts with /b/ — the onset of "bowtie"')

add("T", "boxtimes", "commatailz", "Þ",
    "Comma + tail-z suggests crossing strokes — the ⊗ product crossing",
    '"Com" in "commatailz" echoes the "com" of "×" (times); tail = box edge')

add("T", "odot", "openo", "O",
    "Open O is a circle — the closure point of self-referential topology",
    '"Openo" begins with /oʊ/, the sound of "o" in "odot"')

# ===== R (Relational mode) =====
add("R", "super", "subrightarrow", "¯",
    "Rightward arrow suggests one-way direction — supervenience maps upward",
    '"Sub" and "sup" share /sʌ/; right arrow shows directedness')

add("R", "cat", "ctz", "ý",
    "C-t-z ligature suggests categorical composition — morphisms chaining",
    '"Ct" begins with /k/ like "cat"; ligature = composition of arrows')

add("R", "dagger", "downstep", "Ť",
    "Downward step icon suggests the adjoint descent — dagger reverses direction",
    '"D" of "downstep" matches /d/ of "dagger"; step = reversal')

add("R", "lr", "lyoghlig", "Ð",
    "Ligature joining L and yogh = bidirectional coupling — left-right feedback",
    '"Lyoghlig" evokes /l jɒɡ/ — the L and R letters of "l-r"')

# ===== P (Parity/Symmetry) =====
add("P", "asym", "aolig", '"',
    "A-O ligature — asymmetry as the absence of any symmetry breaking",
    '"Ao" begins with /eɪ/, the long A of "asym"')

add("P", "psi", "upsilon", "υ",
    "Upsilon Υ — Greek letter phonetically and alphabetically adjacent to psi",
    '"Upsil-" contains /psɪl/ echoing /psaɪ/ of "psi"')

add("P", "pm", "pipevar", "F",
    "Vertical pipe | — the vertical stroke shared by + and −",
    '"Pipe" begins with /p/ like "pm"; var = variant form')

add("P", "sym", "subdoublearrow", "˙",
    "Double arrow ↔ suggests full symmetry — bidirectional mappings",
    '"Sub" shares /s/ with "sym"; double arrow = symmetric reflection')

add("P", "pm_sym", "doublebarpipe", "}",
    "Double bar + pipe = two symmetries: Z2 and full — Frobenius-special",
    '"Double" = duality (pm + sym); "pipe" = ± vertical stroke')

# ===== F (Fidelity) =====
add("F", "ell", "beltl", "ì",
    "Belt with L — classical determinism constrains the system's freedom",
    '"Beltl" ends with /l/, the /ɛl/ sound of "ell"')

add("F", "eth", "dh", "ð",
    "DH ð is the actual IPA char for voiced dental fricative named 'eth'",
    '"DH" directly represents /ɛð/ — the eth phoneme itself')

add("F", "hbar", "hvlig", "ß",
    "H-V ligature visually evokes ℏ — h-bar, the quantum of action",
    '"Hv" begins with /h/ like "hbar"; ligature = bar crossing h')

# ===== K (Kinetics) =====
add("K", "fast", "frtailgamma", "-",
    "Gamma with fr- (fast running) tail suggests rapid kinetics, short τ",
    '"Fr" = rapid onset, matching /f/ of "fast"; tail = trajectory')

add("K", "mod", "turnm", "W",
    "Turned M — moderate kinetics, neither fast (upright) nor frozen (inverted)",
    '"Turnm" contains /m/, the /mɒd/ onset of "mod"erate')

add("K", "slow", "schwa", "@",
    "Schwa = unstressed, lazy vowel — slow, relaxed, near-equilibrium relaxation",
    '"Schwa" /ʃwɑ/ has sibilant /ʃ/ approximating /s/ of "slow"; relaxed = slow')

add("K", "trap", "teshlig", "Ù",
    "T-Esh ligature suggests /tr/ clustering — trapped, arrested sound motion",
    '"Tesh" begins with /tɛʃ/ — the /træp/ onset of "trap"')

add("K", "MBL", "lambda", "λ",
    "Lambda λ — Greek L, for Many-Body Localized (L = localization)",
    '"Lambda" contains /læm/, the /l/ and /m/ of M-B-L')

# ===== G (Scope) =====
add("G", "beth", "beta", "β",
    "Beta β — Hebrew beth means 'house'; beta is its Greek cognate",
    '"Beta" is nearly homophonous with "beth"')

add("G", "gimel", "gamma", "γ",
    "Gamma γ — Greek analogue of gimel; both are third in alphabet",
    '"Gamma" shares initial /ɡ/ with "gimel"')

add("G", "aleph", "revapostrophe", "\\",
    "Reversed apostrophe ʻ — represents the glottal stop phoneme of Hebrew aleph",
    '"Revapostrophe" evokes the /ʔ/ of aleph; reversed = aleph\'s silent letter')

# ===== Γ (Interaction Grammar) =====
add("Gamma", "and", "aolig", '"',
    "Wait, aolig already used. Use 'corner' instead.",
    "Fixing...")
# Remove last one and redo

# Actually let me just recompute and print cleanly
print("=== CLEAN ASSIGNMENT TABLE ===")
print()

# Let me redo from scratch in a separate step
for a in assignments:
    p, s, sym, char, nat, snd = a
    print(f"  {p}_{s:12s} → \\{sym:25s}  '{char}'")
    print(f"       Nature: {nat}")
    print(f"       Sound:  {snd}")
    print()
