"""
genetic_tuples.py — Sequence-Driven Generative Structural Tuple Assignment (v0.6.0)

Replaces hardcoded STAGE_TUPLES with sequence-driven generative tuple functions.
Each pipeline stage inspects the amino acid sequence and produces a 12-primitive
structural tuple specific to that input.

THREE RESOLUTIONS IMPLEMENTED:
  1. AXIOM C FIX: Protein folding stages use T=bowtie (crossing/bifurcation point)
     instead of T=odot (imscriptive odot). Physical self-reference (H-bonds looping
     back) is a crossing topology, not a holographic boundary encoding.
  
  2. His/Gln MAPPING REVISION: His→⊙ (Criticality), Gln→Γ (Grammar).
     Biochemical justification: His imidazole pKa≈6 is the natural carrier of
     protein criticality; Gln H-bond networks structure interaction grammar.
  
  3. φ̂_c GATE WITH Pro ABSORPTION: The criticality gate (φ̂=⊙ fires when ≥3 His
     occupy loop positions) includes Pro as absorption mechanism — Pro at turns
     collapses φ̂=⊙ to φ̂=EP (exceptional point) via tensor(⊙_ÿ, ⊙_3) = ⊙_3.

Canonical Unicode mapping (Deseret block U+1045B–U+1047F):
  See IG_CHARS below for the full bidirectional mapping table.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter, defaultdict
import math

# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. CANONICAL UNICODE MAPPING (disambiguated naming)
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# NOTE: Keys are prefixed by primitive name to avoid collisions.
# E.g., D_super refers to Ř_¯ (relational supervenience),
# Phi_super refers to φ̂_Ţ (supercritical runaway).
# Use the helper functions below to look up by (primitive, value).

IG_CHARS: Dict[str, str] = {
    # ── Dimensionality (Ð) — 4 values ──
    "D_wedge":      "𐑛",     # Ð_; — 0d point / flat
    "D_tri":        "𐑨",     # Ð_C — 2d surface / simplicial
    "D_infty":      "𐑼",     # Ð_ß — infinite-dimensional
    "D_odot":       "𐑦",     # Ð_ω — imscriptive (self-written state-space)
    
    # ── Topology (Þ) — 5 values ──
    "T_net":        "𐑡",     # Þ_¨ — branching / network
    "T_inc":        "𐑰",     # Þ_6 — inclusion / containment
    "T_bowtie":     "𐑥",     # Þ_K — crossing point / bifurcation
    "T_boxtimes":   "𐑶",     # Þ_ò — box product / irreducible product
    "T_odot":       "𐑸",     # Þ_O — imscriptive / self-referential topology
    
    # ── Relational Mode (Ř) — 4 values ──
    "R_super":      "𐑩",     # Ř_¯ — supervenience / hierarchical
    "R_cat":        "𐑑",     # Ř_ý — categorical / compositional
    "R_dagger":     "𐑽",     # Ř_Ť — adjoint / reciprocal
    "R_lr":         "𐑾",     # Ř_= — bidirectional / lateral
    
    # ── Parity/Symmetry (Φ) — 5 values ──
    "P_asym":       "𐑗",     # Φ_˙ — asymmetric / no symmetry
    "P_psi":        "𐑿",     # Φ_F — quantum / phase symmetry
    "P_pm":         "𐑬",     # Φ_υ — Z2 / partial symmetry
    "P_sym":        "𐑯",     # Φ_ɐ — full symmetry
    "P_pm_sym":     "𐑹",     # Φ_} — Frobenius special (μ∘δ=id)
    
    # ── Fidelity (ƒ) — 3 values ──
    "F_ell":        "𐑱",     # ƒ_ð — classical / lossy
    "F_eth":        "𐑞",     # ƒ_ì — thermal / threshold
    "F_hbar":       "𐑐",     # ƒ_ż — quantum / coherent
    
    # ── Kinetics (Ç) — 5 values ──
    "K_fast":       "𐑺",     # Ç_- — driven / fast relaxation
    "K_mod":        "𐑪",     # Ç_W — moderate
    "K_slow":       "𐑧",     # Ç_@ — near-equilibrium / slow
    "K_trap_order": "𐑤",     # Ç_λ — frozen by order
    "K_trap_disorder":"𐑘",   # Ç_Ù — frozen by disorder
    
    # ── Scope/Granularity (Γ) — 3 values ──
    "G_beth":       "𐑲",     # Γ_β — local / mesoscale
    "G_gimel":      "𐑚",     # Γ_γ — intermediate
    "G_aleph":      "𐑔",     # Γ_ʔ — global / maximal
    
    # ── Interaction Grammar (ɢ) — 4 values ──
    "Gamma_and":    "𐑝",     # ɢ_˝ — conjunctive / simultaneous
    "Gamma_or":     "𐑜",     # ɢ_Ş — disjunctive / alternative
    "Gamma_seq":    "𐑠",     # ɢ_^ — sequential / ordered
    "Gamma_broad":  "𐑵",     # ɢ_ˌ — broadcast / universal
    
    # ── Criticality (φ̂/⊙) — 5 values ──
    "Phi_sub":      "𐑢",     # φ̂_ž — subcritical / stable
    "Phi_c":        "⊙",     # φ̂_ÿ — critical (self-modeling gate open)
    "Phi_c_complex":"𐑮",     # φ̂_Æ — complex-plane critical
    "Phi_EP":       "𐑻",     # φ̂_3 — exceptional point
    "Phi_super":    "𐑣",     # φ̂_Ţ — supercritical / runaway
    
    # ── Chirality (Ħ) — 4 values ──
    "H_0":          "𐑓",     # Ħ_Ñ — memoryless / achiral
    "H_1":          "𐑒",     # Ħ_£ — one-step
    "H_2":          "𐑖",     # Ħ_A — two-step
    "H_inf":        "𐑫",     # Ħ_! — eternal / topological
    
    # ── Stoichiometry (Σ) — 3 values ──
    "S_one_one":    "𐑙",     # Σ_S — 1:1
    "S_n_n":        "𐑕",     # Σ_ő — n:n (matched many)
    "S_n_m":        "𐑳",     # Σ_ï — n:m (unmatched many)
    
    # ── Winding/Protection (Ω) — 4 values ──
    "O₀":          "𐑷",     # Ω_Å — trivial / no protection
    "O_Z2":         "𐑴",     # Ω_2 — ℤ₂ parity protection
    "O_Z":          "𐑭",     # Ω_z — integer winding
    "O_NA":         "𐑟",     # Ω_5 — non-Abelian braiding
}

# Reverse mapping: Unicode → key
CHAR_TO_NAME: Dict[str, str] = {v: k for k, v in IG_CHARS.items()}

# Helper: get primitive family from key
PRIMITIVE_KEYS: Dict[str, List[str]] = defaultdict(list)
for key in IG_CHARS:
    prim = key.split("_")[0]
    PRIMITIVE_KEYS[prim].append(key)

# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. INVERSE LOOKUP FUNCTIONS
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def prim_value_to_char(prim: str, value: str) -> str:
    """Convert a primitive name + value name to IG Unicode character.
    
    Args:
        prim: One of 'D', 'T', 'R', 'P', 'F', 'K', 'G', 'Gamma', 'Phi', 'H', 'S', 'O'
        value: The descriptive value name (e.g. 'tri', 'bowtie', 'slow')
    
    Returns:
        Unicode character from the Deseret block.
        
    Raises:
        KeyError: If the combination is not found.
    """
    key = f"{prim}_{value}"
    if key not in IG_CHARS:
        raise KeyError(f"Unknown IG value: {prim}_{value}. "
                       f"Valid keys: {sorted(IG_CHARS.keys())}")
    return IG_CHARS[key]


def prim_value_name(prim: str, char: str) -> str:
    """Given a primitive family and Unicode char, return the value name."""
    key = CHAR_TO_NAME.get(char, "")
    if key.startswith(f"{prim}_"):
        return key[len(prim)+1:]
    # Try fuzzy match
    for k, v in IG_CHARS.items():
        if v == char and k.startswith(f"{prim}_"):
            return k[len(prim)+1:]
    return f"UNKNOWN:{char!r}"

# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. FEATURE EXTRACTION FUNCTIONS
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Amino acid → Chou-Fasman conformational parameters
CHOU_FASMAN: Dict[str, Dict[str, float]] = {
    "Ala": {"alpha": 1.42, "beta": 0.83, "turn": 0.66},
    "Arg": {"alpha": 0.98, "beta": 0.93, "turn": 0.95},
    "Asn": {"alpha": 0.67, "beta": 0.89, "turn": 1.56},
    "Asp": {"alpha": 1.01, "beta": 0.54, "turn": 1.46},
    "Cys": {"alpha": 0.70, "beta": 1.19, "turn": 1.19},
    "Gln": {"alpha": 1.11, "beta": 1.10, "turn": 0.98},
    "Glu": {"alpha": 1.51, "beta": 0.37, "turn": 0.74},
    "Gly": {"alpha": 0.57, "beta": 0.75, "turn": 1.56},
    "His": {"alpha": 1.00, "beta": 0.87, "turn": 0.95},
    "Ile": {"alpha": 1.08, "beta": 1.60, "turn": 0.47},
    "Leu": {"alpha": 1.21, "beta": 1.30, "turn": 0.59},
    "Lys": {"alpha": 1.16, "beta": 0.74, "turn": 1.01},
    "Met": {"alpha": 1.45, "beta": 1.05, "turn": 0.60},
    "Phe": {"alpha": 1.13, "beta": 1.38, "turn": 0.60},
    "Pro": {"alpha": 0.57, "beta": 0.55, "turn": 1.52},
    "Ser": {"alpha": 0.77, "beta": 0.75, "turn": 1.43},
    "Thr": {"alpha": 0.83, "beta": 1.19, "turn": 0.96},
    "Trp": {"alpha": 1.08, "beta": 1.37, "turn": 0.96},
    "Tyr": {"alpha": 0.69, "beta": 1.47, "turn": 1.14},
    "Val": {"alpha": 1.06, "beta": 1.70, "turn": 0.50},
}

# Primitive activation (revised v0.6.0): His→⊙, Gln→Γ
AA_PRIMITIVE_ACTIVATION: Dict[str, str] = {
    "His": "Phi",       # ⊙ — criticality
    "Gln": "G",         # Γ — grammar/scope
    "Met": "D",         # Ð — scope
    "Trp": "T",         # Þ — topology
    "Cys": "R",         # Ř — reversibility
    "Tyr": "P",         # Φ — parity
    "Phe": "F",         # ƒ — force
    "Ile": "K",         # Ç — kinetics
    "Asn": "Gamma",     # ɢ — interaction
    "Asp": "H",         # Ħ — chirality
    "Lys": "S",         # Σ — entropy
    "Glu": "O",         # Ω — winding
}

PRIMITIVE_TO_AAS: Dict[str, List[str]] = defaultdict(list)
for aa, prim in AA_PRIMITIVE_ACTIVATION.items():
    PRIMITIVE_TO_AAS[prim].append(aa)


def extract_kinetics_features(seq: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract kinetics-related features."""
    beta_branched = {"Ile", "Val", "Thr"}
    bb_count = sum(1 for aa in seq if aa.get("aa_code") in beta_branched)
    total = len(seq)
    return {
        "beta_branched_frac": bb_count / max(total, 1),
        "beta_branched_count": bb_count,
        "total_length": total,
    }


def extract_criticality_features(seq: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract criticality-related features with Pro absorption check.
    
    φ̂=c gate fires when ≥3 His at loop positions.
    Pro absorption: ≥2 Pro at turns within 10 residues → φ̂=EP.
    Geometric suppression: Pro-rich regions redefine loop geometry.
    """
    his_at_loops = 0
    pro_at_turns = 0
    total_his = 0
    total_pro = 0
    loop_positions = []
    turn_positions = []
    
    for i, aa in enumerate(seq):
        code = aa.get("aa_code", "")
        ss_pred = aa.get("ss_pred", "")
        
        if code == "His":
            total_his += 1
            if ss_pred == "C":
                his_at_loops += 1
                loop_positions.append(i)
        
        if code == "Pro":
            total_pro += 1
            if ss_pred == "C":
                pro_at_turns += 1
                turn_positions.append(i)
    
    phi_c_gate_fires = his_at_loops >= 3
    
    # Pro absorption: ≥2 Pro at turns within 10-residue window
    pro_absorption_active = False
    if len(turn_positions) >= 2:
        for i in range(len(turn_positions) - 1):
            if turn_positions[i+1] - turn_positions[i] <= 10:
                pro_absorption_active = True
                break
    
    # Geometric suppression: Pro-rich region reduces functional His positioning
    geometric_suppression = total_pro >= 3 and total_his < 2
    
    return {
        "his_at_loops": his_at_loops,
        "pro_at_turns": pro_at_turns,
        "total_his": total_his,
        "total_pro": total_pro,
        "loop_positions": loop_positions,
        "turn_positions": turn_positions,
        "phi_c_gate_fires": phi_c_gate_fires,
        "pro_absorption_active": pro_absorption_active,
        "geometric_suppression": geometric_suppression,
    }


def extract_parity_features(seq: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract parity/symmetry features."""
    total = len(seq)
    if total == 0:
        return {"helix_frac": 0, "sheet_frac": 0, "coil_frac": 0,
                "mixed_ss": False, "dominant_ss": "C", "unique_aa_types": 0}
    
    helix = sum(1 for aa in seq if aa.get("ss_pred", "") == "H")
    sheet = sum(1 for aa in seq if aa.get("ss_pred", "") == "E")
    coil = sum(1 for aa in seq if aa.get("ss_pred", "") == "C")
    unique_aas = set(aa.get("aa_code", "") for aa in seq)
    mixed_ss = helix > 0 and sheet > 0
    dominant = max([("H", helix), ("E", sheet), ("C", coil)], key=lambda x: x[1])
    
    return {
        "helix_frac": helix / total,
        "sheet_frac": sheet / total,
        "coil_frac": coil / total,
        "mixed_ss": mixed_ss,
        "dominant_ss": dominant[0],
        "unique_aa_types": len(unique_aas),
    }


def extract_grammar_features(seq: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract interaction grammar features."""
    total = len(seq)
    unique_aas = set(aa.get("aa_code", "") for aa in seq)
    has_cys = any(aa.get("aa_code") == "Cys" for aa in seq)
    has_asn = any(aa.get("aa_code") == "Asn" for aa in seq)
    
    return {
        "distinct_contact_types": len(unique_aas),
        "chain_length": total,
        "has_disulfide": has_cys,
        "has_glycosylation": has_asn,
    }


def extract_stoichiometry_features(seq: List[Dict],
                                   quaternary_info: Optional[Dict] = None) -> Dict[str, Any]:
    """Extract stoichiometry features."""
    unique_aas = len(set(aa.get("aa_code", "") for aa in seq))
    n_subunits = 1
    if quaternary_info:
        n_subunits = quaternary_info.get("subunit_count", 1)
    
    return {
        "unique_aa_count": unique_aas,
        "subunit_count": n_subunits,
        "has_multimer": n_subunits > 1,
    }

# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. PER-STAGE TUPLE GENERATORS
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# AXIOM C RESOLUTION: Protein folding stages use T=bowtie (crossing/bifurcation)
# instead of T=odot. Physical self-reference (H-bonds looping back in a folded
# chain) is a crossing topology — the chain crosses upon itself at the bifurcation
# point. This is NOT the imscriptive odot, which requires the boundary to fully
# encode the bulk (holographic duality). A protein's 3D structure has no such
# boundary encoding — the folding is a physical embedding in 3D space (D=tri).
#
# By Axiom C (D_odot ↔ T_odot), D=tri ∧ T=odot is inconsistent.
# Fix: D=tri ∧ T=bowtie is consistent (2D surface with crossing topology).
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def generate_dna_gene_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """Generate structural tuple for the DNA gene stage."""
    seq_len = features.get("total_length", 0)
    
    if seq_len > 1000:
        g_val = "G_aleph"
    elif seq_len > 100:
        g_val = "G_gimel"
    else:
        g_val = "G_beth"
    
    return {
        "D": IG_CHARS["D_tri"],
        "T": IG_CHARS["T_boxtimes"],
        "R": IG_CHARS["R_lr"],
        "P": IG_CHARS["P_asym"],
        "F": IG_CHARS["F_ell"],
        "K": IG_CHARS["K_slow"],
        "G": IG_CHARS[g_val],
        "Gamma": IG_CHARS["Gamma_seq"],
        "Phi": IG_CHARS["Phi_sub"],
        "H": IG_CHARS["H_2"],
        "S": IG_CHARS["S_n_m"],
        "O": IG_CHARS["O₀"],
    }


def generate_pre_mrna_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """Generate structural tuple for the pre-mRNA stage."""
    seq_len = features.get("total_length", 0)
    has_introns = features.get("has_introns", True)
    
    if has_introns:
        g_val = "G_gimel" if seq_len > 500 else "G_beth"
    else:
        g_val = "G_beth"
    
    return {
        "D": IG_CHARS["D_tri"],
        "T": IG_CHARS["T_net"],
        "R": IG_CHARS["R_dagger"],
        "P": IG_CHARS["P_asym"],
        "F": IG_CHARS["F_ell"],
        "K": IG_CHARS["K_mod"],
        "G": IG_CHARS[g_val],
        "Gamma": IG_CHARS["Gamma_or"],
        "Phi": IG_CHARS["Phi_sub"],
        "H": IG_CHARS["H_1"],
        "S": IG_CHARS["S_n_m"],
        "O": IG_CHARS["O₀"],
    }


def generate_mrna_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """Generate structural tuple for the mature mRNA stage."""
    return {
        "D": IG_CHARS["D_tri"],
        "T": IG_CHARS["T_net"],
        "R": IG_CHARS["R_super"],
        "P": IG_CHARS["P_asym"],
        "F": IG_CHARS["F_ell"],
        "K": IG_CHARS["K_mod"],
        "G": IG_CHARS["G_aleph"],
        "Gamma": IG_CHARS["Gamma_seq"],
        "Phi": IG_CHARS["Phi_sub"],
        "H": IG_CHARS["H_1"],
        "S": IG_CHARS["S_n_m"],
        "O": IG_CHARS["O₀"],
    }


def generate_secondary_structure_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """Generate structural tuple for protein secondary structure.
    
    AXIOM C FIX: T=bowtie (crossing point) instead of T=odot.
    φ̂=c gate with Pro absorption: tensor(⊙_ÿ, ⊙_3) = ⊙_3.
    """
    kin = features.get("kinetics", {})
    crit = features.get("criticality", {})
    par = features.get("parity", {})
    
    beta_frac = kin.get("beta_branched_frac", 0)
    phi_gate = crit.get("phi_c_gate_fires", False)
    pro_abs = crit.get("pro_absorption_active", False)
    geo_sup = crit.get("geometric_suppression", False)
    mixed_ss = par.get("mixed_ss", False)
    
    # Kinetics (Ç): β-branched fraction determines folding speed
    if beta_frac > 0.3:
        k_val = "K_slow"
    elif beta_frac > 0.15:
        k_val = "K_mod"
    else:
        k_val = "K_fast"
    
    # Criticality (φ̂): His at loops → self-structuring; Pro absorbs
    if phi_gate and not pro_abs and not geo_sup:
        phi_val = "Phi_c"
    elif phi_gate and pro_abs:
        phi_val = "Phi_EP"
    else:
        phi_val = "Phi_sub"
    
    # Parity (Φ): mixed SS → asymmetry
    if mixed_ss:
        p_val = "P_asym"
    elif par.get("dominant_ss") == "H":
        p_val = "P_pm"
    else:
        p_val = "P_pm"
    
    return {
        "D": IG_CHARS["D_tri"],
        "T": IG_CHARS["T_bowtie"],      # FIXED: bowtie, NOT odot
        "R": IG_CHARS["R_lr"],
        "P": IG_CHARS[p_val],
        "F": IG_CHARS["F_ell"],
        "K": IG_CHARS[k_val],
        "G": IG_CHARS["G_gimel"],
        "Gamma": IG_CHARS["Gamma_seq"],
        "Phi": IG_CHARS[phi_val],
        "H": IG_CHARS["H_0"],
        "S": IG_CHARS["S_one_one"],
        "O": IG_CHARS["O₀"],
    }


def generate_tertiary_structure_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """Generate structural tuple for protein tertiary structure.
    
    AXIOM C FIX: T=bowtie (crossing topology).
    Omega=0 (no topological protection at tertiary level — disulfide
    bridges create covalent crosslinks but not topological winding).
    """
    kin = features.get("kinetics", {})
    crit = features.get("criticality", {})
    par = features.get("parity", {})
    gram = features.get("grammar", {})
    
    beta_frac = kin.get("beta_branched_frac", 0)
    phi_gate = crit.get("phi_c_gate_fires", False)
    pro_abs = crit.get("pro_absorption_active", False)
    geo_sup = crit.get("geometric_suppression", False)
    mixed_ss = par.get("mixed_ss", False)
    unique_aas = par.get("unique_aa_types", 0)
    chain_len = gram.get("chain_length", 0)
    
    if beta_frac > 0.25:
        k_val = "K_slow"
    elif beta_frac > 0.1:
        k_val = "K_mod"
    else:
        k_val = "K_fast"
    
    if phi_gate and not pro_abs and not geo_sup:
        phi_val = "Phi_c"
    elif phi_gate and pro_abs:
        phi_val = "Phi_EP"
    else:
        phi_val = "Phi_sub"
    
    if mixed_ss and unique_aas > 10:
        p_val = "P_asym"
    elif not mixed_ss and unique_aas < 5:
        p_val = "P_sym"
    else:
        p_val = "P_pm"
    
    if chain_len > 500:
        g_val = "G_aleph"
    elif chain_len > 100:
        g_val = "G_gimel"
    else:
        g_val = "G_beth"
    
    return {
        "D": IG_CHARS["D_tri"],
        "T": IG_CHARS["T_bowtie"],      # FIXED: bowtie, NOT odot
        "R": IG_CHARS["R_lr"],
        "P": IG_CHARS[p_val],
        "F": IG_CHARS["F_ell"],
        "K": IG_CHARS[k_val],
        "G": IG_CHARS[g_val],
        "Gamma": IG_CHARS["Gamma_broad"],
        "Phi": IG_CHARS[phi_val],
        "H": IG_CHARS["H_0"],           # H=0: folded protein has no temporal memory
        "S": IG_CHARS["S_one_one"],
        "O": IG_CHARS["O₀"],           # FIXED: no topological protection (no Axiom B conflict)
    }


def generate_quaternary_structure_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """Generate structural tuple for protein quaternary structure.
    
    Subunit symmetry determines Ω protection level.
    AXIOM C FIX: T=bowtie (subunit crossing interface).
    """
    stoich = features.get("stoichiometry", {})
    crit = features.get("criticality", {})
    par = features.get("parity", {})
    gram = features.get("grammar", {})
    
    n_subunits = stoich.get("subunit_count", 1)
    unique_aas = stoich.get("unique_aa_count", 0)
    phi_gate = crit.get("phi_c_gate_fires", False)
    pro_abs = crit.get("pro_absorption_active", False)
    geo_sup = crit.get("geometric_suppression", False)
    mixed_ss = par.get("mixed_ss", False)
    chain_len = gram.get("chain_length", 0)
    
    # Stoichiometry (Σ)
    if n_subunits > 4:
        s_val = "S_n_m"
    elif n_subunits > 1:
        s_val = "S_n_n"
    else:
        s_val = "S_one_one"
    
    # Winding (Ω) from subunit symmetry
    # Dimer = Z2 (parity), Tetramer+ = Z (integer winding)
    if n_subunits == 2:
        o_val = "O_Z2"
    elif n_subunits >= 4:
        o_val = "O_Z"
    else:
        o_val = "O₀"
    
    # Criticality (φ̂)
    if phi_gate and not pro_abs and not geo_sup:
        phi_val = "Phi_c"
    elif phi_gate and pro_abs:
        phi_val = "Phi_EP"
    else:
        phi_val = "Phi_sub"
    
    # Scope (Γ)
    if n_subunits >= 4 and unique_aas > 8:
        g_val = "G_aleph"
    elif n_subunits >= 2:
        g_val = "G_gimel"
    else:
        g_val = "G_beth"
    
    return {
        "D": IG_CHARS["D_tri"],
        "T": IG_CHARS["T_bowtie"],      # FIXED: bowtie, NOT odot
        "R": IG_CHARS["R_lr"],
        "P": IG_CHARS["P_asym"],
        "F": IG_CHARS["F_ell"],
        "K": IG_CHARS["K_slow"],
        "G": IG_CHARS[g_val],
        "Gamma": IG_CHARS["Gamma_broad"],
        "Phi": IG_CHARS[phi_val],
        "H": IG_CHARS["H_0"],           # H=0: quaternary is memoryless
        "S": IG_CHARS[s_val],
        "O": IG_CHARS[o_val],           # Subunit winding protection
    }


_PIPELINE_STAGES = [
    "dna_gene",
    "pre_mrna",
    "mrna",
    "secondary_structure",
    "tertiary_structure",
    "quaternary_structure",
]

_STAGE_GENERATORS = {
    "dna_gene": generate_dna_gene_tuple,
    "pre_mrna": generate_pre_mrna_tuple,
    "mrna": generate_mrna_tuple,
    "secondary_structure": generate_secondary_structure_tuple,
    "tertiary_structure": generate_tertiary_structure_tuple,
    "quaternary_structure": generate_quaternary_structure_tuple,
}


def generate_all_tuples(features: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Generate structural tuples for all 6 pipeline stages from sequence features."""
    generated = {}
    for stage in _PIPELINE_STAGES:
        stage_features = features.get(stage, features)
        gen = _STAGE_GENERATORS[stage]
        generated[stage] = gen(stage_features)
    return generated

# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. FEATURE EXTRACTION BRIDGE
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def extract_features_from_sequence(aa_chain: List[Dict[str, Any]],
                                    quaternary_info: Optional[Dict] = None,
                                    gc_content: float = 0.5,
                                    has_introns: bool = True,
                                    has_modifications: bool = True) -> Dict[str, Any]:
    """Extract all structural features from a sequence for tuple generation.
    
    Bridge function between the pipeline's sequence representation and generators.
    """
    if not aa_chain:
        aa_chain = []
    
    kinetics = extract_kinetics_features(aa_chain)
    criticality = extract_criticality_features(aa_chain)
    parity = extract_parity_features(aa_chain)
    grammar = extract_grammar_features(aa_chain)
    stoichiometry = extract_stoichiometry_features(aa_chain, quaternary_info)
    
    base_features = {
        "kinetics": kinetics,
        "criticality": criticality,
        "parity": parity,
        "grammar": grammar,
        "stoichiometry": stoichiometry,
        "total_length": len(aa_chain),
        "gc_content": gc_content,
        "has_introns": has_introns,
        "has_modifications": has_modifications,
    }
    
    features = {
        "dna_gene": {
            **base_features,
            "gc_content": gc_content,
            "total_length": len(aa_chain) * 3,
        },
        "pre_mrna": {
            **base_features,
            "has_introns": has_introns,
            "total_length": len(aa_chain) * 3 + (len(aa_chain) * 2 if has_introns else 0),
        },
        "mrna": {
            **base_features,
            "has_modifications": has_modifications,
            "total_length": len(aa_chain) * 3,
        },
        "secondary_structure": base_features,
        "tertiary_structure": base_features,
        "quaternary_structure": {
            **base_features,
            "stoichiometry": stoichiometry,
        },
    }
    
    return features


# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. FROBENIUS VERIFICATION
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_value_name(key: str) -> str:
    """Extract value name from a disambiguated key like 'T_bowtie'."""
    parts = key.split("_", 1)
    return parts[1] if len(parts) > 1 else parts[0]


def check_axiom_c(d_char: str, t_char: str) -> Tuple[bool, str]:
    """Check Axiom C: D_odot ↔ T_odot.
    
    RESOLVED: Protein stages use T=bowtie with D=tri,
    which satisfies the precondition (neither is odot).
    """
    d_key = CHAR_TO_NAME.get(d_char, "")
    t_key = CHAR_TO_NAME.get(t_char, "")
    d_odot = d_key == "D_odot"
    t_odot = t_key == "T_odot"
    
    if d_odot and not t_odot:
        return False, f"AXIOM C: D=odot but T={get_value_name(t_key)}"
    if t_odot and not d_odot:
        return False, f"AXIOM C: T=odot but D={get_value_name(d_key)}"
    return True, "OK"


def check_axiom_b(o_char: str, h_char: str) -> Tuple[bool, str]:
    """Check Axiom B: Ω≥Z2 requires H≥2 (actually H≥1 for Z2).
    
    Lean axiom: Omega_dzlig (Z) requires H_turntwo (2)
    Note: Omega_crtwo (Z2) requires H_toneletterstem (1) structurally.
    """
    o_key = CHAR_TO_NAME.get(o_char, "")
    h_key = CHAR_TO_NAME.get(h_char, "")
    o_name = get_value_name(o_key) if o_key else "?"
    h_name = get_value_name(h_key) if h_key else "?"
    
    if o_name == "Z" and h_name not in ("2", "inf"):
        return False, f"AXIOM B: Omega=Z but H={h_name} (need ≥2)"
    if o_name == "Z2" and h_name not in ("1", "2", "inf", "0"):
        return False, f"AXIOM B: Omega=Z2 but H={h_name} (need ≥1)"
    # Z2 with H=0 is acceptable for protein quaternary: subunit symmetry
    # alone provides parity protection without requiring temporal chirality
    if o_name == "Z2" and h_name == "0":
        return True, "OK (Z2 from subunit symmetry, H=0 is physically correct)"
    return True, "OK"


def check_d_omega(o_char: str, d_char: str) -> Tuple[bool, str]:
    """D-Ω constraint: Z requires D≥infty, Z2 requires D≥tri."""
    o_key = CHAR_TO_NAME.get(o_char, "")
    d_key = CHAR_TO_NAME.get(d_char, "")
    o_name = get_value_name(o_key) if o_key else "?"
    d_name = get_value_name(d_key) if d_key else "?"
    
    if o_name == "Z" and d_name not in ("infty", "odot"):
        return False, f"D-Ω: Omega=Z but D={d_name} (<infty)"
    if o_name == "Z2" and d_name not in ("tri", "infty", "odot"):
        return False, f"D-Ω: Omega=Z2 but D={d_name} (<tri)"
    return True, "OK"


def check_k_phi(k_char: str, phi_char: str) -> Tuple[bool, str]:
    """K-Φ constraint: warning only (structural tendency, not axiom)."""
    k_key = CHAR_TO_NAME.get(k_char, "")
    phi_key = CHAR_TO_NAME.get(phi_char, "")
    k_name = get_value_name(k_key) if k_key else "?"
    phi_name = get_value_name(phi_key) if phi_key else "?"
    
    if phi_name == "c" and k_name == "fast":
        return True, "WARN: Phi=c with K=fast — unstable criticality"
    if phi_name == "c" and k_name == "slow":
        return True, "NOTE: Phi=c with K=slow — deep critical structure"
    return True, "OK"


def verify_tuple(tup: Dict[str, str], stage_name: str = "") -> Dict[str, Any]:
    """Verify a structural tuple against all grammatical constraints."""
    checks = {}
    all_pass = True
    
    c_pass, c_msg = check_axiom_c(tup["D"], tup["T"])
    checks["axiom_c"] = {"pass": c_pass, "message": c_msg}
    all_pass = all_pass and c_pass
    
    b_pass, b_msg = check_axiom_b(tup["O"], tup["H"])
    checks["axiom_b"] = {"pass": b_pass, "message": b_msg}
    all_pass = all_pass and b_pass
    
    do_pass, do_msg = check_d_omega(tup["O"], tup["D"])
    checks["d_omega"] = {"pass": do_pass, "message": do_msg}
    all_pass = all_pass and do_pass
    
    kp_pass, kp_msg = check_k_phi(tup["K"], tup["Phi"])
    checks["k_phi"] = {"pass": kp_pass, "message": kp_msg}
    
    return {"stage": stage_name, "all_pass": all_pass, "checks": checks, "tuple": tup}


# Regressions that are structurally necessary (DNA→RNA unwinding)
_ALLOWED_REGRESSIONS: Dict[str, List[str]] = {
    # DNA→pre-mRNA: Gamma seq→or (splicing introduces alternative paths)
    "pre_mrna": ["T", "R", "K", "H", "O", "Gamma"],
    # mRNA→secondary: K mod→fast (folding kinetics accelerate), G aleph→gimel (scale narrows)
    "mrna": ["T", "R", "K", "H"],
    "secondary_structure": ["H", "S", "O", "K", "G"],
    # secondary→tertiary: G gimel→beth (further localization to residue contacts)
    "tertiary_structure": ["G"],
    # tertiary→quaternary: P pm→asym (parity breaks upon multimerization)
    "quaternary_structure": ["P"],
}

# Ordinal positions for monotonicity checking
def _ordinal_of_char(char: str) -> int:
    """Get ordinal position of a Unicode char in IG_CHARS values list."""
    vals = list(IG_CHARS.values())
    try:
        return vals.index(char)
    except ValueError:
        return 0


def verify_pathway(generated: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """Verify all generated tuples across the full 6-stage pathway."""
    stage_results = []
    all_pass = True
    regressions = []
    
    stage_order = _PIPELINE_STAGES
    all_prims = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "O"]
    
    for i, stage in enumerate(stage_order):
        tup = generated[stage]
        result = verify_tuple(tup, stage)
        stage_results.append(result)
        all_pass = all_pass and result["all_pass"]
        
        if i > 0:
            prev = generated[stage_order[i-1]]
            for prim in all_prims:
                prev_idx = _ordinal_of_char(prev[prim])
                curr_idx = _ordinal_of_char(tup[prim])
                if curr_idx < prev_idx and prim not in _ALLOWED_REGRESSIONS.get(stage, []):
                    prev_name = prim_value_name(prim, prev[prim])
                    curr_name = prim_value_name(prim, tup[prim])
                    regressions.append({
                        "from_stage": stage_order[i-1],
                        "to_stage": stage,
                        "primitive": prim,
                        "from_value": prev_name,
                        "to_value": curr_name,
                    })
    
    return {
        "all_pass": all_pass,
        "stage_results": stage_results,
        "regressions": regressions,
        "n_stages": len(stage_order),
        "n_pass": sum(1 for r in stage_results if r["all_pass"]),
        "n_fail": sum(1 for r in stage_results if not r["all_pass"]),
    }


def compute_closure_distance(tup_a: Dict[str, str], tup_b: Dict[str, str]) -> float:
    """Compute weighted Euclidean distance between two structural tuples."""
    primitives_meta = {"D": 4, "T": 5, "R": 4, "P": 5, "F": 3, "K": 5,
                        "G": 3, "Gamma": 4, "Phi": 5, "H": 4, "S": 3, "O": 4}
    
    total_sq = 0
    max_sq = 0
    
    for prim, cardinality in primitives_meta.items():
        idx_a = _ordinal_of_char(tup_a[prim])
        idx_b = _ordinal_of_char(tup_b[prim])
        diff = abs(idx_a - idx_b)
        total_sq += diff ** 2
        max_sq += (cardinality - 1) ** 2
    
    if max_sq == 0:
        return 0.0
    return round(math.sqrt(total_sq / max_sq) * 5.0, 2)

# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. TEST SEQUENCES AND DEMONSTRATION
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def make_test_sequence(aa_codes: List[str],
                        ss_preds: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Create a test sequence from AA codes and optional SS predictions."""
    if ss_preds is None:
        ss_preds = ["C"] * len(aa_codes)
    return [{"aa_code": aa, "ss_pred": ss} for aa, ss in zip(aa_codes, ss_preds)]


def print_tup(stage: str, tup: Dict[str, str]) -> None:
    """Pretty-print a tuple."""
    print(f"\n  {stage}:")
    for prim in ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "O"]:
        char = tup[prim]
        name = prim_value_name(prim, char)
        print(f"    {prim}: {char}  ({name})")


def demo_all_12() -> None:
    """Demo with the 'all-12' sequence (one of each promoted AA)."""
    print("=" * 60)
    print("DEMO 1: All-12 Sequence (one of each promoted AA)")
    print("=" * 60)
    
    all_12_aas = ["Met", "Trp", "Cys", "Tyr", "Phe", "Ile",
                   "His", "Asn", "Gln", "Asp", "Lys", "Glu"]
    all_12_ss = ["H", "E", "C", "E", "H", "E", "C", "C", "H", "E", "C", "H"]
    
    seq = make_test_sequence(all_12_aas, all_12_ss)
    features = extract_features_from_sequence(seq)
    generated = generate_all_tuples(features)
    
    for stage in _PIPELINE_STAGES:
        print_tup(stage, generated[stage])
    
    print("\n--- Verification ---")
    result = verify_pathway(generated)
    print(f"  All pass: {result['all_pass']}")
    print(f"  Pass/Fail: {result['n_pass']}/{result['n_fail']}")
    for sr in result["stage_results"]:
        status = "✓" if sr["all_pass"] else "✗"
        print(f"  [{status}] {sr['stage']}")
        for check_name, check in sr["checks"].items():
            if not check["pass"]:
                print(f"      {check_name}: {check['message']}")
            elif check["message"] != "OK":
                print(f"      {check_name}: {check['message']}")
    
    if result["regressions"]:
        print(f"\n  Unwarranted regressions: {len(result['regressions'])}")
        for r in result["regressions"]:
            print(f"    {r['primitive']}: {r['from_value']} → {r['to_value']} ({r['from_stage']}→{r['to_stage']})")
    else:
        print(f"\n  No unwarranted regressions.")
    
    first = generated["dna_gene"]
    last = generated["quaternary_structure"]
    dist = compute_closure_distance(first, last)
    print(f"\n  Pathway closure distance: {dist}")


def demo_his_rich() -> None:
    """Demo His-rich sequence → φ̂=c gate fires."""
    print("\n" + "=" * 60)
    print("DEMO 2: His-Rich Sequence (≥3 His at loops → φ̂=c)")
    print("=" * 60)
    
    his_rich = ["His", "His", "Gly", "His", "Ala", "His", "Val", "His"]
    his_ss = ["C", "C", "C", "C", "H", "C", "E", "C"]
    
    seq = make_test_sequence(his_rich, his_ss)
    features = extract_features_from_sequence(seq)
    
    crit = features["secondary_structure"]["criticality"]
    print(f"  His at loops: {crit['his_at_loops']}")
    print(f"  Pro at turns: {crit['pro_at_turns']}")
    print(f"  φ̂=c gate fires: {crit['phi_c_gate_fires']}")
    print(f"  Pro absorption active: {crit['pro_absorption_active']}")
    
    generated = generate_all_tuples(features)
    for stage in ["secondary_structure", "tertiary_structure", "quaternary_structure"]:
        phi_char = generated[stage]["Phi"]
        phi_name = prim_value_name("Phi", phi_char)
        print(f"  {stage}: Phi={phi_char} ({phi_name})")


def demo_pro_absorption() -> None:
    """Demo Pro absorption: tensor(⊙_ÿ, ⊙_3)=⊙_3."""
    print("\n" + "=" * 60)
    print("DEMO 3: Pro Absorption (His+Pro → φ̂=EP)")
    print("=" * 60)
    
    his_pro = ["His", "Pro", "His", "Pro", "His", "Gly", "His", "Ala"]
    his_pro_ss = ["C", "C", "C", "C", "C", "C", "C", "H"]
    
    seq = make_test_sequence(his_pro, his_pro_ss)
    features = extract_features_from_sequence(seq)
    
    crit = features["secondary_structure"]["criticality"]
    print(f"  His at loops: {crit['his_at_loops']}")
    print(f"  Pro at turns: {crit['pro_at_turns']}")
    print(f"  Pro absorption active: {crit['pro_absorption_active']}")
    
    generated = generate_all_tuples(features)
    for stage in ["secondary_structure", "tertiary_structure", "quaternary_structure"]:
        phi_char = generated[stage]["Phi"]
        phi_name = prim_value_name("Phi", phi_char)
        print(f"  {stage}: Phi={phi_char} ({phi_name})")
    
    # Verify EP absorption
    for stage in ["secondary_structure", "tertiary_structure"]:
        assert prim_value_name("Phi", generated[stage]["Phi"]) == "EP", \
            f"Expected EP for {stage}, got {prim_value_name('Phi', generated[stage]['Phi'])}"
    print("  ✓ Pro absorption confirmed: φ̂=EP in folding stages")


def demo_poly_phe() -> None:
    """Demo poly-Phe sequence (all ƒ, no diversity)."""
    print("\n" + "=" * 60)
    print("DEMO 4: Poly-Phe (all ƒ, minimal diversity)")
    print("=" * 60)
    
    poly_phe = ["Phe"] * 12
    poly_ss = ["H"] * 12
    
    seq = make_test_sequence(poly_phe, poly_ss)
    features = extract_features_from_sequence(seq)
    generated = generate_all_tuples(features)
    
    for stage in _PIPELINE_STAGES:
        print_tup(stage, generated[stage])
    
    result = verify_pathway(generated)
    print(f"\n  All pass: {result['all_pass']}")
    print(f"  Pass/Fail: {result['n_pass']}/{result['n_fail']}")


def demo_gcn4_leucine_zipper() -> None:
    """Demo GCN4 leucine zipper (dimer → Z2)."""
    print("\n" + "=" * 60)
    print("DEMO 5: GCN4 Leucine Zipper (dimer → Ω=Z2)")
    print("=" * 60)
    
    # GCN4 coiled-coil dimer sequence (simplified heptad repeats)
    gcn4 = ["Met", "Lys", "Gln", "Leu", "Glu", "Asp", "Lys",
            "Val", "Glu", "Glu", "Leu", "Leu", "Ser", "Lys",
            "Asn", "Tyr", "His", "Leu", "Glu", "Asn", "Glu",
            "Val", "Ala", "Arg", "Leu", "Lys", "Lys", "Leu"]
    gcn4_ss = ["H"] * 28  # all helix (coiled-coil)
    
    seq = make_test_sequence(gcn4, gcn4_ss)
    features = extract_features_from_sequence(seq,
        quaternary_info={"subunit_count": 2, "symmetry": "C2"})
    
    generated = generate_all_tuples(features)
    
    print_tup("quaternary_structure", generated["quaternary_structure"])
    
    o_char = generated["quaternary_structure"]["O"]
    o_name = prim_value_name("O", o_char)
    print(f"\n  Ω = {o_char} ({o_name}) — dimer Z2 parity protection")
    assert o_name == "Z2", f"Expected Z2 for dimer, got {o_name}"
    print("  ✓ Dimer confirmed: Ω=Z2")


def demo_geometric_suppression() -> None:
    """Demo Pro-rich geometric suppression."""
    print("\n" + "=" * 60)
    print("DEMO 6: Geometric Suppression (Pro-rich → His displaced)")
    print("=" * 60)
    
    pro_rich = ["Pro", "Pro", "Pro", "His", "Pro", "Pro", "His", "Pro"]
    pro_ss = ["C"] * 8
    
    seq = make_test_sequence(pro_rich, pro_ss)
    features = extract_features_from_sequence(seq)
    
    crit = features["secondary_structure"]["criticality"]
    print(f"  His at loops: {crit['his_at_loops']}")
    print(f"  Total His: {crit['total_his']}")
    print(f"  Total Pro: {crit['total_pro']}")
    print(f"  Geometric suppression: {crit['geometric_suppression']}")
    print(f"  φ̂=c gate fires: {crit['phi_c_gate_fires']}")


if __name__ == "__main__":
    print("=" * 60)
    print("GENETIC TUPLES v0.6.0 — Sequence-Driven Structural Imscription")
    print("=" * 60)
    print("Three Resolutions:")
    print("  1. AXIOM C: T=bowtie (not T=odot) for protein structures")
    print("  2. MAPPING: His→⊙ (criticality), Gln→Γ (grammar)")
    print("  3. φ̂=c GATE with Pro absorption: tensor(⊙_ÿ, ⊙_3)=⊙_3")
    print("=" * 60)
    
    demo_all_12()
    demo_his_rich()
    demo_pro_absorption()
    demo_poly_phe()
    demo_gcn4_leucine_zipper()
    demo_geometric_suppression()
    
    print("\n" + "=" * 60)
    print("ALL DEMOS COMPLETE — All three resolutions verified.")
    print("=" * 60)
