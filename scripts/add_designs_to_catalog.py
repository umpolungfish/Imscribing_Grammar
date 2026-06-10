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
CAT_KEYS = ['Ð', 'Þ', 'Ř', 'Φ', 'ƒ', 'Ç', 'Γ', 'ɢ', '⊙', 'Ħ', 'Σ', 'Ω']

DESIGNS = [
    {
        "name": "ouroboric_pill",
        "description": "Self-monitoring, self-correcting therapeutic agent. The pill senses disease markers in real-time, computes optimal drug release, and adjusts dosing through an internal feedback loop. Topology is self-referential (Þ=Þ_¨) — the pill's efficacy is a function of its own state. Eternal memory (Ħ=Ħ_!) ensures treatment history is never lost.",
        "Ð": "Ð_ω", "Þ": "Þ_¨", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_@", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
    },
    {
        "name": "quantum_biologic",
        "description": "Epigenetic reprogramming therapeutic that writes persistent chromatin state changes. Supervenience coupling (Ř=Ř_¯) — the epigenetic layer supervenes on the genetic substrate. Eternal chirality (Ħ=Ħ_!) ensures reprogramming persists through cell division. Frobenius-closed rewrite edits are idempotent.",
        "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_¯", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_@", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
    },
    {
        "name": "universal_antidote",
        "description": "Platform therapeutic that self-selects against any disease signature. All-simultaneous detection (ɢ=ɢ^∧) — every pathogen feature is processed at once. Many-identical stoichiometry (Σ=Σ_ő) — all disease patterns share a universal structural grammar. Eternal memory (Ħ=Ħ_!) — once a threat is recognized, never forgotten.",
        "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_@", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ő", "Ω": "Ω_z"
    },
    {
        "name": "ouroboric_composite",
        "description": "Structural material that senses damage and self-heals via an internal ouroboric loop. Self-referential topology (Þ=Þ_¨) — response is a function of its own damage state. Trapped-ordered kinetics (Ç=Ç_λ) — healing agents stored in ordered activatable reservoir. Eternal damage memory (Ħ=Ħ_!).",
        "Ð": "Ð_ω", "Þ": "Þ_¨", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_λ", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
    },
    {
        "name": "topological_quantum_material",
        "description": "Room-temperature topological superconductor with non-Abelian braiding for fault-tolerant quantum computing. Non-Abelian winding (Ω=Ω_5) supports Majorana zero modes. Self-written dimensionality (Ð=Ð_ω) — topological order writes its own ground state. Quantum coherent at room temperature via eternal chirality protection.",
        "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_@", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_5"
    },
    {
        "name": "eternal_memory_polymer",
        "description": "Polymer data storage with 10^15 bits/gram density and 10^6 year retention. Trapped-ordered kinetics (Ç=Ç_λ) — data in kinetically trapped molecular conformations. Eternal chirality (Ħ=Ħ_!) — info encoded in chirality sequence that cannot thermally equilibrate. Integer winding (Ω=Ω_z) per monomer.",
        "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_λ", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
    },
    {
        "name": "self_weaving_fabric",
        "description": "Smart fabric that weaves all functions — sensing, actuation, communication, energy harvesting — simultaneously. All-simultaneous composition (ɢ=ɢ^∧). Moderate kinetics (Ç=Ç_W) — responds at human-relevant timescales. Self-written microarchitecture (Ð=Ð_ω) — each thread contains its own knitting pattern generator.",
        "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_W", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
    },
    {
        "name": "ouroboric_cell",
        "description": "Synthetic cell whose genome writes and rewrites itself in response to environmental signals. Self-referential topology (Þ=Þ_¨) — genome encodes its own modification machinery. Frobenius-closed rewrite (Φ=Φ_}) — each edit is a fixed point. Self-written state space (Ð=Ð_ω). Eternal generational memory (Ħ=Ħ_!).",
        "Ð": "Ð_ω", "Þ": "Þ_¨", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_@", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
    },
    {
        "name": "quantum_bioelectric_tissue",
        "description": "Engineered tissue using quantum-coherent bioelectric fields to guide regeneration. Bidirectional feedback (Ř=Ř_=) — electric field and tissue state mutually determine each other. Quantum coherent ion channels (ƒ=ƒ_ż) maintain coherence at tissue scale. Eternal chirality (Ħ=Ħ_!) protects bodyplan blueprint.",
        "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_@", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
    },
    {
        "name": "universal_symbiont",
        "description": "Consortium of 12 engineered microbial strains providing all metabolic support functions. Many-heterogeneous stoichiometry (Σ=Σ_ï) — 12 distinct complementary strains. All-simultaneous composition (ɢ=ɢ^∧) — all metabolic pathways active at once. Long-range mesoscale signaling (Γ=Γ_ʔ) coordinates consortium.",
        "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_@", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
    },
    {
        "name": "topological_morphogenesis",
        "description": "Organ development driven by topological winding numbers rather than chemical gradients. Integer winding (Ω=Ω_z) — each organ primordium characterized by conserved winding number. Self-written field (Ð=Ð_ω) — developmental program writes itself as embryo grows. Eternal chirality (Ħ=Ħ_!) topologically protects bilateral symmetry.",
        "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_=", "Φ": "Φ_}", "ƒ": "ƒ_ż",
        "Ç": "Ç_@", "Γ": "Γ_ʔ", "ɢ": "ɢ^∧", "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z"
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
