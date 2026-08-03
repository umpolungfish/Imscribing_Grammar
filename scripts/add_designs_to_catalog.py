#!/usr/bin/env python3
"""Add all Rebis designs to the IG catalog and write the design document."""

import json, math, sys
from pathlib import Path

BASE = Path(__file__).parent.absolute()
CATALOG_PATH = BASE / "IG_catalog.json"

# Load current catalog
with open(CATALOG_PATH) as f:
    catalog = json.load(f)

# Design entries (old notation format for catalog compatibility)
CAT_KEYS = ['⊢', '⊣', '>', '<', '⋈', '⊤', '∈', '∋', '⊙', '⊥', '⊞', '◻']

DESIGNS = [
    {
        "name": "ouroboric_pill",
        "description": "Self-monitoring, self-correcting therapeutic agent. The pill senses disease markers in real-time, computes optimal drug release, and adjusts dosing through an internal feedback loop. Topology is self-referential (⊣=𐑶) — the pill's efficacy is a function of its own state. Eternal memory (Ħ=𐑫) ensures treatment history is never lost.",
        "⊢": "𐑦", "⊣": "𐑶", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
    {
        "name": "quantum_biologic",
        "description": "Epigenetic reprogramming therapeutic that writes persistent chromatin state changes. Supervenience coupling (>=𐑩) — the epigenetic layer supervenes on the genetic substrate. Eternal chirality (Ħ=𐑫) ensures reprogramming persists through cell division. Frobenius-closed rewrite edits are idempotent.",
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑩", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
    {
        "name": "universal_antidote",
        "description": "Platform therapeutic that self-selects against any disease signature. All-simultaneous detection (ɢ=ɢ^∧) — every pathogen feature is processed at once. Many-identical stoichiometry (Σ=𐑕) — all disease patterns share a universal grammar. Eternal memory (Ħ=𐑫) — once a threat is recognized, never forgotten.",
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑕", "◻": "𐑭"
    },
    {
        "name": "ouroboric_composite",
        "description": "Structural material that senses damage and self-heals via an internal ouroboric loop. Self-referential topology (⊣=𐑶) — response is a function of its own damage state. Trapped-ordered kinetics (⊤=𐑺) — healing agents stored in ordered activatable reservoir. Eternal damage memory (Ħ=𐑫).",
        "⊢": "𐑦", "⊣": "𐑶", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑺", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
    {
        "name": "topological_quantum_material",
        "description": "Room-temperature topological superconductor with non-Abelian braiding for fault-tolerant quantum computing. Non-Abelian winding (Ω=𐑟) supports Majorana zero modes. Self-written dimensionality (⊢=𐑦) — topological order writes its own ground state. Quantum coherent at room temperature via eternal chirality protection.",
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑟"
    },
    {
        "name": "eternal_memory_polymer",
        "description": "Polymer data storage with 10^15 bits/gram density and 10^6 year retention. Trapped-ordered kinetics (⊤=𐑺) — data in kinetically trapped molecular conformations. Eternal chirality (Ħ=𐑫) — info encoded in chirality sequence that cannot thermally equilibrate. Integer winding (Ω=𐑭) per monomer.",
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑺", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
    {
        "name": "self_weaving_fabric",
        "description": "Smart fabric that weaves all functions — sensing, actuation, communication, energy harvesting — simultaneously. All-simultaneous composition (ɢ=ɢ^∧). Moderate kinetics (⊤=𐑤) — responds at human-relevant timescales. Self-written microarchitecture (⊢=𐑦) — each thread contains its own knitting pattern generator.",
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑤", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
    {
        "name": "ouroboric_cell",
        "description": "Synthetic cell whose genome writes and rewrites itself in response to environmental signals. Self-referential topology (⊣=𐑶) — genome encodes its own modification machinery. Frobenius-closed rewrite (<=𐑹) — each edit is a fixed point. Self-written state space (⊢=𐑦). Eternal generational memory (Ħ=𐑫).",
        "⊢": "𐑦", "⊣": "𐑶", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
    {
        "name": "quantum_bioelectric_tissue",
        "description": "Engineered tissue using quantum-coherent bioelectric fields to guide regeneration. Bidirectional feedback (>=𐑾) — electric field and tissue state mutually determine each other. Quantum coherent ion channels (⋈=𐑐) maintain coherence at tissue scale. Eternal chirality (Ħ=𐑫) protects bodyplan blueprint.",
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
    {
        "name": "universal_symbiont",
        "description": "Consortium of 12 engineered microbial strains providing all metabolic support functions. Many-heterogeneous stoichiometry (Σ=𐑳) — 12 distinct complementary strains. All-simultaneous composition (ɢ=ɢ^∧) — all metabolic pathways active at once. Long-range mesoscale signaling (∈=𐑲) coordinates consortium.",
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
    {
        "name": "topological_morphogenesis",
        "description": "Organ development driven by topological winding numbers rather than chemical gradients. Integer winding (Ω=𐑭) — each organ primordium characterized by conserved winding number. Self-written field (⊢=𐑦) — developmental program writes itself as embryo grows. Eternal chirality (Ħ=𐑫) topologically protects bilateral symmetry.",
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "ɢ^∧", "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭"
    },
]

# Add/update catalog entries
existing_names = {e['name'] for e in catalog}
added, updated = 0, 0
for d in DESIGNS:
    if d['name'] in existing_names:
        # Update existing
        for i, e in enumerate(catalog):
            if e['name'] == d['name']:
                catalog[i] = d
                updated += 1
                break
    else:
        catalog.append(d)
        added += 1

# Write catalog
with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Catalog updated: {added} added, {updated} updated")
print(f"Total entries: {len(catalog)}")
