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
           "chembio": S.CHEMBIO_SPECIALIST_PROMPT}

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
    "math":      ["./ask", "imasm16_3", "m3iosis.paranumber", "la lookup",
                  "verify_sic_moduli.sh", "cl9nk"],
    "chembio":   ["rebis.serpentrod", "rebis.p4ra", "vita-probe", "genetic-engine",
                  "cetacean-speaker", "vessel.run"],
    "editorial": ["ltx", "zdd", "zenodo_upload.py", "ig_figures.py"],
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

sys.exit(0 if ok else 1)
