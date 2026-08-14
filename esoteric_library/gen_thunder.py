#!/usr/bin/env python3
"""Generate thunder.json — imscribed catalog entry for
The Thunder, Perfect Mind, from the Nag Hammadi library (Codex VI, tractate 2).

Combines all 18 chapters from the existing gnostic.json into one complete entry
with the canonical tuple: 𐑦, 𐑸, 𐑽, 𐑬, ⋈^ż, ⊤^@, 𐑲, ∋^Ş, ⊙, 𐑫, 𐑳, 𐑭
Tier: O_∞, C_score: 0.95
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PHI = '⊙'

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {
        "name": f"thunder_{num:02d}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "⊢": D, "⊣": T, "≻": R, "≺": P, "⋈": F,
        "⊤": K, "∈": G, "∋": Gm, PHI: C,
        "⊥": H, "⊞": S, "◻": Om,
        "tier": tier, "C_score": cscore, "notes": notes,
    }

# Load existing chapters from gnostic.json to combine the text
gnostic_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gnostic.json")
with open(gnostic_path, encoding="utf-8") as f:
    gnostic = json.load(f)

thunder_chapters = [e for e in gnostic if 'thunder' in e.get('name','')]
thunder_chapters.sort(key=lambda e: e['number'])

# Build the complete text with chapter headers
parts = []
for ch in thunder_chapters:
    num = ch['number']
    # Strip leading/trailing whitespace and normalize spacing
    text = ch['text'].strip()
    parts.append(f"§{num}\n\n{text}")

full_text = "\n\n".join(parts)

chapters = [
    entry(1,
        "The Thunder, Perfect Mind",
        "The complete Gnostic revelation discourse from the Nag Hammadi Library (Codex VI). A divine feminine voice — the aeonic Wisdom — announces herself as the coincidence of all opposites: the first and the last, the honored and the scorned, the whore and the holy one. The text is a thunderous proclamation of ontological antinomy, revealing the nature of the Self as containing all contradictions.",
        full_text,
        "𐑦", "𐑸", "𐑽", "𐑬", "⋈^ż", "⊤^@", "𐑲", "∋^Ş",
        "⊙", "𐑫", "𐑳", "𐑭",
        "O_∞", 0.95,
        "Complete text of all 18 sections as one unified imscription. The thunderous broadcast (∋^Ş) of a divine voice proclaiming the identity of opposites: the adjoint structure (𐑽) links subject and object, knower and known. The Frobenius polarization (𐑬) manifests as the antinomic pairs that constitute the whole. ⊙: the speaker's self-disclosure IS the listener's self-discovery. 𐑭: the circular return of every assertion to its opposite completes a topological winding."),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thunder.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(chapters)} entries -> {out}")