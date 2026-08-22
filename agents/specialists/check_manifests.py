"""Every tool the code defines must appear in every manifest, and each domain's
own entry points must appear in its own."""
import re, sys
sys.path.insert(0, "/home/mrnob0dy666/imsgct/imscribing_grammar/agents")
sys.path.insert(0, "/home/mrnob0dy666/imsgct/imscribing_grammar/agents/specialists")
import true_agentic_agent as taa
import specialists as S
from gen_tool_manifest import base_tools, grammar_tools

prompts = {"math": S.MATH_SPECIALIST_PROMPT,
           "editorial": S.EDITORIAL_SPECIALIST_PROMPT,
           "chembio": S.CHEMBIO_SPECIALIST_PROMPT,
           "recorder": S.RECORDER_SPECIALIST_PROMPT,
           "heterodox": S.HETERODOX_SPECIALIST_PROMPT,
           "momonados": S.MOMONADOS_SPECIALIST_PROMPT,
           "closure": S.CLOSURE_SPECIALIST_PROMPT}

base = [n for n, _ in base_tools()]
gram = grammar_tools()
ok = True

for d, p in prompts.items():
    miss_b = [t for t in base if not re.search(rf'`{t}`', p)]
    miss_g = [t for t in gram if not re.search(rf'`{t}`', p)]
    print(f"{d:10s} base {len(base)-len(miss_b)}/{len(base)}   "
          f"grammar {len(gram)-len(miss_g)}/{len(gram)}")
    if miss_b or miss_g:
        ok = False
        print(f"           MISSING base={miss_b} grammar={miss_g}")

# domain markers that must appear in their own manifest and nowhere it'd be wrong
markers = {
    # m3iosis.paranumber was a marker for a module that no longer exists — the
    # m3iosis entry is now derived from its own argparse tree, which is why the
    # generator reports the module as unresolvable. A marker asserting a dead
    # surface fails forever and teaches nothing, so it is retired here.
    "math":      ["./ask", "imasm16_3", "la lookup",
                  "verify_sic_moduli.sh", "cl9nk"],
    "chembio":   ["rebis.serpentrod", "rebis.p4ra", "vita-probe", "genetic-engine",
                  "cetacean-speaker", "vessel.run"],
    "editorial": ["ltx", "zdd", "zenodo_upload.py", "ig_figures.py"],
    "recorder":  ["recorder_census.py", "build_skeleton.py", "LEDGER.md",
                  "DJED.md", "IG_catalog.json", "command grep"],
    "heterodox": ["./ask", "mOMonadOS", "m3iosis", "p4ramill", "ob3ect",
                  "cl9nk", "para_vm"],
    # The mOMonadOS markers are the places the surface is READ FROM, not a list
    # of commands. A command name here would be exactly the staleness the
    # specialist is built to avoid, and the check would then enforce it.
    "momonados": ["menu.rs", "repl.rs", "run_serial_cmds.sh", "make image",
                  "make ordinals", "check_menu_coverage.py"],
    # The four commands, the four classes, and the word that keeps a report
    # complete. "price" is in the list because a closure without its cost is the
    # failure mode this specialist exists to prevent.
    "closure":   ["ovm", "oneshots", "ctc", "nesting", "sic", "d12", "d2048",
                  "one-shot", "manufactured", "price"],
}
print()
for d, ms in markers.items():
    miss = [m for m in ms if m not in prompts[d]]
    print(f"{d:10s} domain markers {len(ms)-len(miss)}/{len(ms)}"
          + (f"   MISSING {miss}" if miss else ""))
    if miss:
        ok = False

print()
rider = taa._PARTNERSHIP_RIDER.strip().splitlines()[0]
ctx = taa._load_imsgct_context()
marker = ctx.strip().splitlines()[0]
for d, p in prompts.items():
    assembled = p + taa._PARTNERSHIP_RIDER + ctx   # what run() ends up with
    nr = assembled.count(rider)
    nc = assembled.count(marker)
    print(f"{d:10s} rider x{nr}   context-marker x{nc}")
    if nr != 1:
        ok = False

# ── IMASM canon ───────────────────────────────────────────────────────────────
# Every specialist must be able to imscribe, not merely read glyphs. This is
# universal rather than domain-specific, so it lives once in __init__ and is
# appended to all of them; the check is that none has lost it.
print()
_imasm_marks = ["<imasm>", "⊢ VINIT", "∈ FSPLIT", "banked", "δ before δ",
                "parasm", "the decode table is the WORD",
                # the liberation half — without these the canon is a syntax
                # reference and the trained reflex wins
                "hypergematria", "aleph <word>", "CHECKABLE",
                "imagination, not permission"]
for d, p_ in prompts.items():
    miss = [m for m in _imasm_marks if m not in p_]
    if miss:
        ok = False
    print(f"{d:10} imasm {len(_imasm_marks)-len(miss)}/{len(_imasm_marks)}"
          + (f"   MISSING {miss}" if miss else ""))

sys.exit(0 if ok else 1)
