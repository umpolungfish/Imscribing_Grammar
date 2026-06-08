#!/usr/bin/env python3
"""Write novel_psychedelics_synthesis.md using data from novel_psychedelics module."""
import sys, json
sys.path.insert(0, '/home/mrnob0dy666/imscribing_grammar')
from novel_psychedelics import *

out = []
out.append("# Novel Navigatable Psychedelics\n")
out.append("**Author:** Lando⊗⊙perator\n")
out.append("## 5 Novel Compounds\n")
for k in ["verticullum","chimerium","apertix","retiarius","praxeum"]:
    t = NOVEL_COMPOUNDS[k]
    out.append(f"### {NOVEL_NAMES[k]}\n")
    out.append(f"`{t}`\n")
    out.append(f"Tier: {assign_tier(t)}\n")
out.append("## 6 Control Methods\n")
for m in ['ep','chirality','winding','scope','adjoint','launch']:
    out.append(f"- **{m}**: see novel_psychedelics.py\n")
with open('/home/mrnob0dy666/imscribing_grammar/novel_psychedelics_synthesis.md','w') as f:
    f.write('\n'.join(out))
print("OK", len('\n'.join(out)))
