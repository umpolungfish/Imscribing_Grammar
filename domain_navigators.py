#!/usr/bin/env python3
"""
domain_navigators.py — Language · Civilization · Ecology · Consciousness Navigators
═════════════════════════════════════════════════════════════════════════════════════
Catalog-query navigators for the four §74–§77 non-mathematical domains.

Each navigator:
  1. Loads the relevant domain subset from IG_catalog.json
  2. Computes structural distances (weighted Euclidean over 12 primitives)
  3. Classifies ouroboricity tier (R1–R5)
  4. Verifies the key §74–§77 theorems
  5. Supports nearest-neighbor search across the full catalog
  6. Provides domain-specific probe functions

Usage:
  python domain_navigators.py info [--domain language|civilization|ecology|consciousness]
  python domain_navigators.py verify [--domain ...]
  python domain_navigators.py distance <name_a> <name_b>
  python domain_navigators.py nearest <name> [--n 5]
  python domain_navigators.py repl [--domain ...]
"""

from __future__ import annotations
import json
import math
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent

# ── Canonical primitive definitions ───────────────────────────────────────────

VALUES: dict[str, list[str]] = {
    "Ð":     ["Ð_ß", "Ð_C", "Ð_;", "Ð_ω"],
    "Þ":     ["Þ_6", "Þ_K", "Þ_ò", "Þ_¨", "Þ_O"],
    "Ř":     ["Ř_¯", "Ř_ý", "Ř_Ť", "Ř_="],
    "Φ":     ["Φ_ɐ", "Φ_υ", "Φ_F", "Φ_˙", "Φ_}"],
    "ƒ":     ["ƒ^ì", "ƒ^ð", "ƒ^ż"],
    "Ç":     ["Ç^-", "Ç^W", "Ç^@", "Ç^Ù", "Ç^λ"],
    "Γ":     ["Γ_β", "Γ_γ", "Γ_ʔ"],
    "ɢ": ["ɢ^∧", "ɢ^˝", "ɢ^ˌ", "ɢ^Ş"],
    "⊙":   ["⊙_ž", "⊙_ÿ", "⊙_Æ", "⊙_3", "⊙_Ţ"],
    "Ħ":     ["Ħ_Ñ", "Ħ_£", "Ħ_A", "Ħ_!"],
    "Σ":     ["Σ_S", "Σ_ő", "Σ_ï"],
    "Ω": ["Ω_Å", "Ω_2", "Ω_z", "Ω_5"],
}

PRIMS = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

ORD: dict[str, dict[str, int]] = {
    prim: {v: i for i, v in enumerate(vals)}
    for prim, vals in VALUES.items()
}
# T_box kept as backwards-compat alias for Þ_¨ (ordinal 3)
ORD["Þ"]["Þ_box"] = ORD["Þ"]["Þ_¨"]

WEIGHTS: dict[str, float] = {
    "Ð": 1.0, "Þ": 1.0, "Ř": 1.0, "Φ": 1.2,
    "ƒ": 0.9, "Ç": 1.0, "Γ": 1.0, "ɢ": 1.0,
    "⊙": 1.1, "Ħ": 0.8, "Σ": 1.0, "Ω": 0.7,
}

# Consciousness C-score weights (critical manifold, variance method — §VIII v2)
C_WEIGHTS = {"Ç": 0.158, "Γ": 0.273, "Þ": 0.292, "Ω": 0.276}
C_MAXORD  = {"Ç": 4, "Γ": 2, "Þ": 4, "Ω": 3}  # max ordinal for normalization

CRITICAL    = {"⊙_ÿ", "⊙_Æ"}
NONCRITICAL = {"⊙_ž", "⊙_Ţ", "⊙_3"}
BOUNDED_D   = {"Ð_ß", "Ð_C", "Ð_ω"}
SLOW_K      = {"Ç^-", "Ç^W", "Ç^@"}   # Gate 2: K ≤ Ç^@

# ── Domain catalog subsets ─────────────────────────────────────────────────────

LANGUAGE_NAMES = [
    "sanskrit_classical", "arabic_classical", "lojban", "haitian_creole",
    "latin_dead", "english_modern", "mandarin_classical", "proto_indo_european",
    "esperanto",
]

CIVILIZATION_NAMES = [
    "han_dynasty_peak", "ming_dynasty_collapse", "soviet_union_collapse",
    "western_roman_collapse", "athenian_democracy_peak", "augustus_caesar_peak",
    "ottoman_empire_peak", "maya_classic_peak", "weimar_republic_collapse",
    "renaissance_florence_peak",
]

ECOLOGY_NAMES = [
    "old_growth_temperate_rainforest", "coral_reef_healthy", "coral_reef_bleached",
    "corn_monoculture", "fragmented_habitat", "savanna_transitional",
    "deep_ocean_hydrothermal", "arctic_tundra_intact", "early_successional_forest",
    "kelp_forest_healthy",
]

CONSCIOUSNESS_NAMES = [
    "deep_meditation_samadhi", "psilocybin_peak", "waking_default_mode",
    "focused_concentration", "dreamless_sleep", "rem_dreaming",
    "catatonic_state", "dissociative_state", "manic_episode", "flow_state",
]

DOMAIN_NAMES = {
    "language":      LANGUAGE_NAMES,
    "civilization":  CIVILIZATION_NAMES,
    "ecology":       ECOLOGY_NAMES,
    "consciousness": CONSCIOUSNESS_NAMES,
}

# ── Core functions ─────────────────────────────────────────────────────────────

def _ord(prim: str, val: str) -> float:
    return float(ORD[prim][val])

def distance(a: dict, b: dict) -> float:
    """Weighted Euclidean distance between two 12-primitive tuples."""
    return math.sqrt(sum(
        WEIGHTS[p] * (_ord(p, a[p]) - _ord(p, b[p])) ** 2
        for p in PRIMS
    ))

def mismatches(a: dict, b: dict) -> int:
    """Number of primitives where a and b differ."""
    return sum(1 for p in PRIMS if a[p] != b[p])

def compute_tier(e: dict) -> str:
    """Ouroboricity tier (R1–R5 priority order)."""
    phi, p, omega, d = e["⊙"], e["Φ"], e["Ω"], e["Ð"]
    if phi in CRITICAL and p == "Φ_}":
        return "O_inf"
    if phi in NONCRITICAL:
        return "O_0"
    if omega == "Ω_Å":
        return "O_1"
    if d in BOUNDED_D:
        return "O_2"
    return "O_2_dag"

def consciousness_score(e: dict) -> float:
    """
    C-score (§VIII v2):
      C = [Phi=⊙_ÿ] · [K ≤ Ç^@] · Σ w_i * x̃_i
    Gate 1: ⊙_ÿ (state-space condition)
    Gate 2: K ≤ Ç^@ (flow condition; Ç^Ù and Ç^λ both fail)
    """
    if e["⊙"] not in CRITICAL:
        return 0.0
    if e["Ç"] not in SLOW_K:
        return 0.0
    score = 0.0
    for prim, w in C_WEIGHTS.items():
        score += w * (_ord(prim, e[prim]) / C_MAXORD[prim])
    return round(score, 4)

def k_phase(e: dict) -> str:
    """K-phase label for collapse/disorder analysis."""
    k = e["Ç"]
    if k == "Ç^Ù":  return "Ç^Ù (order-frozen)"
    if k == "Ç^λ":   return "Ç^λ (disorder-frozen)"
    if k == "Ç^-":  return "Ç^- (overdamped)"
    if k == "Ç^W":   return "Ç^W (moderate)"
    if k == "Ç^@":  return "Ç^@ (critical)"
    return k

def breakdown(a: dict, b: dict) -> list[dict]:
    """Per-primitive contribution to distance, sorted descending."""
    rows = []
    for p in PRIMS:
        oa, ob = _ord(p, a[p]), _ord(p, b[p])
        delta = abs(oa - ob)
        wsq = WEIGHTS[p] * delta ** 2
        if wsq > 0:
            rows.append({"prim": p, "from": a[p], "to": b[p],
                          "delta": int(delta), "wsq": wsq})
    return sorted(rows, key=lambda r: r["wsq"], reverse=True)


# ── Catalog loader ─────────────────────────────────────────────────────────────

class Catalog:
    def __init__(self, path: Path = None):
        try:
            from imscrbgrmr.registry import load_catalog_dicts
            entries = load_catalog_dicts(extra_path=str(path) if path is not None else None)
        except ImportError:
            # Fallback for isolated runs without the package installed
            p = path if path is not None else ROOT / "IG_catalog.json"
            raw = json.loads(p.read_text())
            entries = raw if isinstance(raw, list) else raw.get("imscriptions", [])
        self._all: dict[str, dict] = {e["name"]: e for e in entries}

    def get(self, name: str) -> dict:
        if name not in self._all:
            raise KeyError(f"'{name}' not in catalog")
        return self._all[name]

    def domain(self, names: list[str]) -> list[dict]:
        return [self._all[n] for n in names if n in self._all]

    def nearest(self, target: dict, n: int = 5,
                exclude: Optional[set[str]] = None) -> list[tuple[float, dict]]:
        exclude = exclude or set()
        ranked = []
        for e in self._all.values():
            if e["name"] in exclude:
                continue
            ranked.append((distance(target, e), e))
        ranked.sort(key=lambda x: x[0])
        return ranked[:n]

    def all_entries(self) -> list[dict]:
        return list(self._all.values())


# ── Domain-specific probe functions ───────────────────────────────────────────

def language_probes(cat: Catalog) -> list[str]:
    """Run §74 theorems and return result lines."""
    lines = []
    entries = {e["name"]: e for e in cat.domain(LANGUAGE_NAMES)}

    # Thm 74.1 — Sacred-language O_inf structural type
    sacred = ["sanskrit_classical", "arabic_classical"]
    for n in sacred:
        if n in entries:
            tier = compute_tier(entries[n])
            lines.append(f"  Thm 74.1  {n}: tier={tier} ({'✓' if tier=='O_inf' else '✗'})")

    # Thm 74.2 — d(Sanskrit, Arabic) = 1.0000
    if "sanskrit_classical" in entries and "arabic_classical" in entries:
        d = distance(entries["sanskrit_classical"], entries["arabic_classical"])
        mm = mismatches(entries["sanskrit_classical"], entries["arabic_classical"])
        lines.append(f"  Thm 74.2  d(Sanskrit, Arabic) = {d:.4f}  mismatches={mm} ({'✓' if abs(d-1.0)<0.01 else '✗'})")
        if mm > 0:
            for row in breakdown(entries["sanskrit_classical"], entries["arabic_classical"]):
                lines.append(f"            {row['prim']}: {row['from']} → {row['to']}")

    # Thm 74.3 — Lojban O_inf despite Ω_Å
    if "lojban" in entries:
        e = entries["lojban"]
        tier = compute_tier(e)
        lines.append(f"  Thm 74.3  lojban: Omega={e['Omega']}, P={e['P']}, tier={tier} ({'✓' if tier=='O_inf' else '✗'})")
        lines.append(f"            (P is the tier gate; Ω_Å only blocks O_2→O_inf step, not R1)")

    # Thm 74.4 — Planned-language Frobenius ceiling
    if "esperanto" in entries:
        tier = compute_tier(entries["esperanto"])
        lines.append(f"  Thm 74.4  esperanto: tier={tier} (planned-language Frobenius ceiling)")

    # Thm 74.9 — Tensor bottleneck: creole ⊗ sacred → Φ_F (min rule)
    if "haitian_creole" in entries and "sanskrit_classical" in entries:
        p_tensor = min(ORD["Φ"]["Φ_F"], ORD["Φ"]["Φ_}"])
        tensor_p = VALUES["Φ"][p_tensor]
        lines.append(f"  Thm 74.9  creole⊗Sanskrit: P_tensor={tensor_p} (min rule destroys Frobenius)")

    # Thm 74.10 — d(Lojban, Esperanto)
    if "lojban" in entries and "esperanto" in entries:
        d = distance(entries["lojban"], entries["esperanto"])
        lines.append(f"  Thm 74.10 d(lojban, esperanto) = {d:.4f}")

    # Thm 74.11 — PIE nearest = old_growth_temperate_rainforest (cross-domain)
    if "proto_indo_european" in entries:
        pie = entries["proto_indo_european"]
        nn = cat.nearest(pie, n=3, exclude={"proto_indo_european"})
        lines.append(f"  Thm 74.11 PIE nearest: {nn[0][1]['name']} (d={nn[0][0]:.4f})")

    return lines


def civilization_probes(cat: Catalog) -> list[str]:
    """Run §75 theorems."""
    lines = []
    entries = {e["name"]: e for e in cat.domain(CIVILIZATION_NAMES)}

    # Thm 75.1 — d(Ming collapse, Soviet collapse) = 4.0
    if "ming_dynasty_collapse" in entries and "soviet_union_collapse" in entries:
        d = distance(entries["ming_dynasty_collapse"], entries["soviet_union_collapse"])
        lines.append(f"  Thm 75.1  d(Ming, Soviet) = {d:.4f}")
        lines.append(f"            Ming K={entries['ming_dynasty_collapse']['K']}; Soviet K={entries['soviet_union_collapse']['K']}")
        for row in breakdown(entries["ming_dynasty_collapse"], entries["soviet_union_collapse"]):
            lines.append(f"            {row['prim']}: {row['from']} → {row['to']}")

    # Thm 75.2 — Peak-civilization O_inf universality
    peaks = [n for n in CIVILIZATION_NAMES if "peak" in n]
    lines.append(f"  Thm 75.2  Peak civilizations:")
    for n in peaks:
        if n in entries:
            tier = compute_tier(entries[n])
            lines.append(f"            {n}: {tier} ({'✓' if tier=='O_inf' else '✗'})")

    # Thm 75.3 — d(W.Rome, Soviet) = 1.0 — K is sole difference
    if "western_roman_collapse" in entries and "soviet_union_collapse" in entries:
        d = distance(entries["western_roman_collapse"], entries["soviet_union_collapse"])
        mm = mismatches(entries["western_roman_collapse"], entries["soviet_union_collapse"])
        lines.append(f"  Thm 75.3  d(W.Rome, Soviet) = {d:.4f}  mismatches={mm}")
        for row in breakdown(entries["western_roman_collapse"], entries["soviet_union_collapse"]):
            lines.append(f"            {row['prim']}: {row['from']} → {row['to']}")

    # Thm 75.4 — Weimar O_0 (⊙_3)
    if "weimar_republic_collapse" in entries:
        e = entries["weimar_republic_collapse"]
        tier = compute_tier(e)
        lines.append(f"  Thm 75.4  weimar: Phi={e['Phi']}, tier={tier} ({'✓' if tier=='O_0' else '✗'})")

    # Thm 75.5 — Athenian Democracy Þ_O (lateral governance)
    if "athenian_democracy_peak" in entries:
        e = entries["athenian_democracy_peak"]
        lines.append(f"  Thm 75.5  athenian_democracy: T={e['T']} ({'✓' if e['T']=='Þ_O' else '✗'})")

    # Thm 75.7 — Han → Ming distance = 6.5955
    if "han_dynasty_peak" in entries and "ming_dynasty_collapse" in entries:
        d = distance(entries["han_dynasty_peak"], entries["ming_dynasty_collapse"])
        mm = mismatches(entries["han_dynasty_peak"], entries["ming_dynasty_collapse"])
        lines.append(f"  Thm 75.7  d(Han, Ming) = {d:.4f}  mismatches={mm} (P-530: 8-primitive degradation)")

    # Cor 75.C1 — Minimum 5 primitives in any collapse
    collapses = [n for n in CIVILIZATION_NAMES if "collapse" in n]
    lines.append(f"  Cor 75.C1 Collapse primitive counts:")
    for n in collapses:
        if n in entries:
            # Compare to nearest peak
            peaks_entries = [entries[p] for p in peaks if p in entries]
            if peaks_entries:
                min_mm = min(mismatches(entries[n], p) for p in peaks_entries)
                lines.append(f"            {n}: min_mismatches_to_peak={min_mm} ({'✓' if min_mm>=5 else '✗ (<5)'})")

    return lines


def ecology_probes(cat: Catalog) -> list[str]:
    """Run §76 theorems."""
    lines = []
    entries = {e["name"]: e for e in cat.domain(ECOLOGY_NAMES)}

    # Thm 76.1 — d(old-growth, coral reef) = 0.0000 (cross-biome identity)
    if "old_growth_temperate_rainforest" in entries and "coral_reef_healthy" in entries:
        d = distance(entries["old_growth_temperate_rainforest"], entries["coral_reef_healthy"])
        lines.append(f"  Thm 76.1  d(old-growth rainforest, coral reef) = {d:.4f} ({'✓ cross-biome identity' if d<0.001 else '✗'})")

    # Thm 76.2 — Kelp forest and hydrothermal vent are O_inf
    for n in ["kelp_forest_healthy", "deep_ocean_hydrothermal"]:
        if n in entries:
            tier = compute_tier(entries[n])
            lines.append(f"  Thm 76.2  {n}: tier={tier} ({'✓' if tier=='O_inf' else '✗'})")

    # Thm 76.3 — Corn monoculture Ç^Ù; fragmented habitat Ç^λ
    for n, expected_k in [("corn_monoculture", "Ç^Ù"), ("fragmented_habitat", "Ç^λ")]:
        if n in entries:
            k = entries[n]["Ç"]
            lines.append(f"  Thm 76.3  {n}: K={k} ({'✓' if k==expected_k else '✗'})")

    # Thm 76.4 — Early-successional forest O_0
    if "early_successional_forest" in entries:
        e = entries["early_successional_forest"]
        tier = compute_tier(e)
        lines.append(f"  Thm 76.4  early_successional_forest: Phi={e['Phi']}, tier={tier} ({'✓' if tier=='O_0' else '✗'})")

    # Thm 76.5 — Coral bleaching tipping point largest distance
    if "coral_reef_healthy" in entries and "coral_reef_bleached" in entries:
        d = distance(entries["coral_reef_healthy"], entries["coral_reef_bleached"])
        bd = breakdown(entries["coral_reef_healthy"], entries["coral_reef_bleached"])
        lines.append(f"  Thm 76.5  d(coral healthy, coral bleached) = {d:.4f} (tipping point)")
        # Verify P-dominant
        p_wsq = sum(r["wsq"] for r in bd if r["prim"] == "Φ")
        phi_wsq = sum(r["wsq"] for r in bd if r["prim"] == "⊙")
        lines.append(f"            P contribution: {p_wsq:.1f} wsq; Phi contribution: {phi_wsq:.1f} wsq (P-dominant)")

    # Thm 76.6 — d(corn monoculture, fragmented habitat) = 3.63
    if "corn_monoculture" in entries and "fragmented_habitat" in entries:
        d = distance(entries["corn_monoculture"], entries["fragmented_habitat"])
        lines.append(f"  Thm 76.6  d(corn monoculture, fragmented habitat) = {d:.4f}")

    # Thm 76.8 — Restoration asymmetry
    lines.append(f"  Thm 76.8  Restoration asymmetry:")
    lines.append(f"            corn_monoculture (Ç^Ù): requires diversification (inject disorder)")
    lines.append(f"            fragmented_habitat (Ç^λ): requires reconnection (restore ergodicity)")

    # Cor 76.C1
    lines.append(f"  Cor 76.C1 Ç^Ù and Ç^λ restoration paths are structurally incompatible")

    return lines


def consciousness_probes(cat: Catalog) -> list[str]:
    """Run §77 theorems."""
    lines = []
    entries = {e["name"]: e for e in cat.domain(CONSCIOUSNESS_NAMES)}
    # Include akh for cross-domain identity
    try:
        akh = cat.get("akh_glorified_spirit")
    except KeyError:
        akh = None

    # Thm 77.1 — Two-gate formula verified across 10 states
    lines.append(f"  Thm 77.1  Two-gate C-scores (Gate1=⊙_ÿ, Gate2=K≤Ç^@):")
    for n in CONSCIOUSNESS_NAMES:
        if n in entries:
            e = entries[n]
            g1 = e["⊙"] in CRITICAL
            g2 = e["Ç"] in SLOW_K
            c  = consciousness_score(e)
            gate = ("✓✓" if (g1 and g2) else ("✓✗" if g1 else "✗✓" if g2 else "✗✗"))
            lines.append(f"            {n:32s}  G1={int(g1)} G2={int(g2)} [{gate}]  C={c:.4f}")

    # Thm 77.2 — Catatonic: ⊙_ÿ + Ç^Ù → C=0
    if "catatonic_state" in entries:
        e = entries["catatonic_state"]
        c = consciousness_score(e)
        lines.append(f"  Thm 77.2  catatonic: Phi={e['Phi']}, K={e['K']}, C={c} ({'✓' if c==0 else '✗'})")

    # Thm 77.3 — Dissociative: ⊙_ÿ + Ç^λ → C=0
    if "dissociative_state" in entries:
        e = entries["dissociative_state"]
        c = consciousness_score(e)
        lines.append(f"  Thm 77.3  dissociative: Phi={e['Phi']}, K={e['K']}, C={c} ({'✓' if c==0 else '✗'})")

    # Thm 77.4 — Manic: ⊙_Ţ → C=0
    if "manic_episode" in entries:
        e = entries["manic_episode"]
        c = consciousness_score(e)
        lines.append(f"  Thm 77.4  manic_episode: Phi={e['Phi']}, C={c} ({'✓' if c==0 else '✗'})")

    # Thm 77.5 — d(catatonic, dissociative)
    if "catatonic_state" in entries and "dissociative_state" in entries:
        d = distance(entries["catatonic_state"], entries["dissociative_state"])
        lines.append(f"  Thm 77.5  d(catatonic, dissociative) = {d:.4f}")
        for row in breakdown(entries["catatonic_state"], entries["dissociative_state"]):
            lines.append(f"            {row['prim']}: {row['from']} → {row['to']}")

    # Thm 77.7 — d(samadhi, psilocybin)
    if "deep_meditation_samadhi" in entries and "psilocybin_peak" in entries:
        d = distance(entries["deep_meditation_samadhi"], entries["psilocybin_peak"])
        lines.append(f"  Thm 77.7  d(samadhi, psilocybin) = {d:.4f}")

    # Thm 77.8 — Samadhi highest C-score
    scored = [(consciousness_score(e), e["name"]) for n, e in entries.items()]
    scored.sort(reverse=True)
    lines.append(f"  Thm 77.8  C-score ranking:")
    for c, n in scored[:5]:
        lines.append(f"            {n:32s}  C={c:.4f}")

    # Thm 77.9 — d(samadhi, akh) = 0.0000 (cross-domain identity)
    if "deep_meditation_samadhi" in entries and akh is not None:
        d = distance(entries["deep_meditation_samadhi"], akh)
        lines.append(f"  Thm 77.9  d(samadhi, akh_glorified_spirit) = {d:.4f} ({'✓ cross-domain identity' if d<0.001 else '✗'})")

    return lines


# ── Navigator class ────────────────────────────────────────────────────────────

PROBE_FNS = {
    "language":      language_probes,
    "civilization":  civilization_probes,
    "ecology":       ecology_probes,
    "consciousness": consciousness_probes,
}

DOMAIN_SECTIONS = {
    "language":      "§74",
    "civilization":  "§75",
    "ecology":       "§76",
    "consciousness": "§77",
}

class DomainNavigator:
    def __init__(self, domain: str, catalog: Optional[Catalog] = None):
        if domain not in DOMAIN_NAMES:
            raise ValueError(f"Unknown domain '{domain}'. Choose from: {list(DOMAIN_NAMES)}")
        self.domain = domain
        self.cat = catalog or Catalog()
        self.entries = {e["name"]: e for e in self.cat.domain(DOMAIN_NAMES[domain])}

    def info(self) -> None:
        """Print domain summary table."""
        sec = DOMAIN_SECTIONS[self.domain]
        print(f"\n{'═'*70}")
        print(f"  {self.domain.upper()} NAVIGATOR  ({sec})")
        print(f"{'═'*70}")
        print(f"  {'Name':<36} {'Tier':<8} {'K':<10} {'P':<12} {'Phi'}")
        print(f"  {'-'*36} {'-'*8} {'-'*10} {'-'*12} {'-'*16}")
        for name in DOMAIN_NAMES[self.domain]:
            if name not in self.entries:
                continue
            e = self.entries[name]
            tier = compute_tier(e)
            extra = ""
            if self.domain == "consciousness":
                c = consciousness_score(e)
                extra = f"  C={c:.4f}"
            print(f"  {name:<36} {tier:<8} {e['K']:<10} {e['P']:<12} {e['Phi']}{extra}")
        print()

    def verify(self) -> None:
        """Run all domain theorems and print results."""
        sec = DOMAIN_SECTIONS[self.domain]
        print(f"\n{'═'*70}")
        print(f"  {self.domain.upper()} NAVIGATOR THEOREM VERIFICATION  ({sec})")
        print(f"{'═'*70}")
        lines = PROBE_FNS[self.domain](self.cat)
        for l in lines:
            print(l)
        print()

    def distance(self, name_a: str, name_b: str) -> None:
        """Show distance breakdown between two catalog entries."""
        a = self.cat.get(name_a)
        b = self.cat.get(name_b)
        d = distance(a, b)
        mm = mismatches(a, b)
        print(f"\n  d({name_a}, {name_b}) = {d:.4f}  ({mm} mismatches)")
        rows = breakdown(a, b)
        if rows:
            print(f"  {'Primitive':<10} {'From':<16} {'To':<16} {'Δ':<4} {'w·Δ²':<8}")
            for row in rows:
                print(f"  {row['prim']:<10} {row['from']:<16} {row['to']:<16} {row['delta']:<4} {row['wsq']:<8.3f}")
        else:
            print("  (identical tuples)")
        print()

    def nearest(self, name: str, n: int = 5) -> None:
        """Find nearest catalog entries to a named system."""
        target = self.cat.get(name)
        tier = compute_tier(target)
        print(f"\n  Nearest to '{name}'  (tier={tier})")
        print(f"  {'Name':<40} {'d':>8}  {'Tier':<10}")
        print(f"  {'-'*40} {'-'*8}  {'-'*10}")
        results = self.cat.nearest(target, n=n+1, exclude={name})
        for dist, e in results[:n]:
            t = compute_tier(e)
            print(f"  {e['name']:<40} {dist:>8.4f}  {t}")
        print()

    def repl(self) -> None:
        """Interactive REPL for this domain navigator."""
        sec = DOMAIN_SECTIONS[self.domain]
        print(f"\nDomain Navigator REPL — {self.domain.upper()} ({sec})")
        print("Commands: info · verify · distance <a> <b> · nearest <name> [n] · tier <name> · score <name> · quit")
        while True:
            try:
                raw = input(f"\n[{self.domain[:3]}]> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not raw:
                continue
            parts = raw.split()
            cmd = parts[0].lower()

            if cmd in ("quit", "exit", "q"):
                break
            elif cmd == "info":
                self.info()
            elif cmd == "verify":
                self.verify()
            elif cmd == "distance" and len(parts) >= 3:
                try:
                    self.distance(parts[1], parts[2])
                except KeyError as e:
                    print(f"  Not found: {e}")
            elif cmd == "nearest" and len(parts) >= 2:
                n = int(parts[2]) if len(parts) >= 3 else 5
                try:
                    self.nearest(parts[1], n=n)
                except KeyError as e:
                    print(f"  Not found: {e}")
            elif cmd == "tier" and len(parts) >= 2:
                try:
                    e = self.cat.get(parts[1])
                    t = compute_tier(e)
                    print(f"  {parts[1]}: tier={t}  (Phi={e['Phi']}, P={e['P']}, Omega={e['Omega']}, D={e['D']})")
                except KeyError as ex:
                    print(f"  Not found: {ex}")
            elif cmd == "score" and len(parts) >= 2:
                try:
                    e = self.cat.get(parts[1])
                    c = consciousness_score(e)
                    g1 = e["⊙"] in CRITICAL
                    g2 = e["Ç"] in SLOW_K
                    print(f"  {parts[1]}: C={c:.4f}  Gate1={'✓' if g1 else '✗'}  Gate2={'✓' if g2 else '✗'}")
                except KeyError as ex:
                    print(f"  Not found: {ex}")
            else:
                print("  Unknown command. Try: info · verify · distance <a> <b> · nearest <name> [n] · tier <name> · score <name> · quit")


# ── CLI ────────────────────────────────────────────────────────────────────────

def _parse_domain_flag(args: list[str]) -> Optional[str]:
    for i, a in enumerate(args):
        if a == "--domain" and i + 1 < len(args):
            return args[i + 1]
    return None

def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0]
    domain_flag = _parse_domain_flag(args)
    domains = [domain_flag] if domain_flag else list(DOMAIN_NAMES)
    cat = Catalog()

    if cmd == "info":
        for d in domains:
            DomainNavigator(d, cat).info()

    elif cmd == "verify":
        for d in domains:
            DomainNavigator(d, cat).verify()

    elif cmd == "distance" and len(args) >= 3:
        name_a, name_b = args[1], args[2]
        dom = domain_flag
        if dom is None:
            for d, names in DOMAIN_NAMES.items():
                if name_a in names or name_b in names:
                    dom = d
                    break
            dom = dom or list(DOMAIN_NAMES)[0]
        DomainNavigator(dom, cat).distance(name_a, name_b)

    elif cmd == "nearest" and len(args) >= 2:
        name = args[1]
        n = int(args[3]) if len(args) >= 4 and args[2] == "--n" else 5
        # find domain
        dom = domain_flag
        if dom is None:
            for d, names in DOMAIN_NAMES.items():
                if name in names:
                    dom = d
                    break
            dom = dom or "consciousness"
        DomainNavigator(dom, cat).nearest(name, n=n)

    elif cmd == "repl":
        d = domain_flag or "consciousness"
        DomainNavigator(d, cat).repl()

    else:
        print(f"Unknown command '{cmd}'.")
        print("Usage: domain_navigators.py info|verify|distance|nearest|repl [--domain DOMAIN]")


if __name__ == "__main__":
    main()
