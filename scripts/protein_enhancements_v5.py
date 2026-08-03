#!/usr/bin/env python3
"""
protein_enhancements_v5.py — Frobenius-Guided Protein Processing Engine
========================================================================
Builds on v4 with:
  • POMC-specific fragment naming (N-POMC, joining peptide, ACTH, β-LPH, β-endorphin)
  • Context-aware merging of false-positive internal dibasic sites
  • Monobasic cleavage detection (single R/K in specific contexts)
  • Advanced fragment classification by primitive spectrum fingerprint
  • SARS-CoV-2 polyprotein test case
  • Cross-kingdom test cases (plant, insect)

Author: Lando⊗⊙perator
"""

from __future__ import annotations
import re, sys
sys.path.insert(0, '/home/mrnob0dy666')
from protein_stratified_predictor import (
    PRIMITIVE_MAP, PRIMITIVE_ORDERS, HYDROPATHY,
    RollingProfile, CleavageSite, MatureProduct, ProcessingPrediction,
    classify_module, predict_processing, analyze_spectrum
)
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field

# ══════════════════════════════════════════════════════════════════
# 1. KNOWN BIOLOGICAL FRAGMENT FINGERPRINTS
# ══════════════════════════════════════════════════════════════════
# Sequence fingerprints used to identify fragments by their
# characteristic peptide patterns, independent of position.

FINGERPRINTS = {
    # ── Insulin family ──
    'B-chain':     [r'F[^C]{0,15}HLC', r'F[^C]{0,15}H[^C]{0,3}C', r'KHL[^C]{0,5}C', r'QHL[^C]{0,5}C'],
    'A-chain':     [r'GIVEQC', r'GIVDQC', r'GIVEEC', r'GIVE[^P]{0,3}C'],
    'C-peptide':   [r'EAEDLQVG', r'VEDPQV', r'EDPQQVP', r'VEEDGSSG'],
    # ── Glucagon family ──
    'Glucagon':    [r'HSQGTFTSDYSKYL', r'HSQGTFTSD', r'KYLDSRRAQDFVQ'],
    'GLP-1':       [r'HAEGTFTSDVSS', r'HAEGTFTSD', r'KEFIAWLVKGR'],
    'GLP-2':       [r'HADGSF', r'IAAEFKEWL', r'IAEFKEWL'],
    'IP-1':        [r'RNRNNIA', r'NRNNIA$', r'RNRNNIAKR', r'^NRNNIAKR'],
    'IP-2':        [r'^[A-Z]{1,4}$'],
    'GRPP':        [r'LQDTEEK', r'SFSASQADP'],
    # ── POMC family ──
    'α-MSH':       [r'SYSMEHFRWG', r'SYSMEHFR'],
    'ACTH':        [r'SYSMEHFRWGKPV', r'SYSMEHFR'],
    'CLIP':        [r'RPVKVYPNV', r'PVKVYPNVA'],
    'β-endorphin': [r'YGGFMTSEK', r'YGGFM'],
    'β-LPH':       [r'ELTGQRLRE', r'ELTGQR'],
    'γ-LPH':       [r'LTGQRLREGD', r'GQRLREGDG'],
    'Joining_Peptide': [r'EDVSAGED', r'EDCGPLPEGG', r'DGAKPGPREG'],
    'N-POMC':      [r'GWCLESSQC', r'CLESSQCQDL', r'VMGHFRWDRF'],
    # ── Miscellaneous ──
    'Signal_Peptide': [r'^M[^S]{0,5}'],
}


def match_fingerprint(seq: str, fingerprints: list) -> bool:
    """Check if sequence matches any fingerprint pattern."""
    for pat in fingerprints:
        if re.search(pat, seq):
            return True
    return False


def identify_fragment(seq: str, prev_motif: str = None,
                      next_motif: str = None, idx: int = 0,
                      total: int = 0, profile: dict = None) -> str:
    """Identify a fragment by its biological fingerprint with fallback to
    primitive-dominant naming.
    
    Priority: 1. Sequence fingerprint match
              2. Position-based logic (C-peptide-like between dibasics)
              3. Primitive-dominant generic name
    """
    core = seq.rstrip('KR')
    n_cys = core.count('C')
    n_glu = core.count('E')
    n_gln = core.count('Q')
    length = len(core)
    
    # ── 1. Fingerprint matches ──
    for name, patterns in FINGERPRINTS.items():
        if match_fingerprint(seq, patterns):
            return name.replace('_', ' ')
    
    # ── 2. Position-based logic ──
    # Insulin C-peptide: between dibasics, 25-45 AA, >=3 Glu
    if (prev_motif in ('RR', 'KR') and next_motif in ('RR', 'KR') and
        25 <= length <= 45 and n_glu >= 3 and n_cys == 0):
        return 'C-peptide'
    
    # α-MSH-like: short, SYSMEHFR pattern (short ACTH)
    if re.search(r'SYSME', core) and length <= 15:
        return 'α-MSH'
    
    # Proglucagon GRPP 
    if re.search(r'LQDTEE', core) and length >= 20:
        return 'GRPP'
    if re.search(r'SFSASQADP', core):
        return 'GRPP' 
    
    # Short connector peptides
    if length <= 6 and prev_motif and next_motif:
        return 'IP-2' if 'GLP' in str(profile or {}) else 'Connector'
    
    # ── 3. Primitive-dominant fallback ──
    if profile is None:
        cls = classify_module(seq)
        profile = cls.get('profile', {})
    
    dom = (profile or {}).get('dominant_primitive') or \
           classify_module(seq).get('dominant')
    
    desc_map = {
        '◻': 'Ω-winding module',
        'φ̂': '⊙-criticality signal',
        '>': '>-scaffold domain',
        '<': '<-switch domain',
        '⊥': 'Ħ-chiral domain',
        '⊞': 'Σ-variable region',
        '⋈': '⋈-hydrophobic core',
        '∋': 'ɢ-glycosylation target',
        '∈': 'Γ-catalytic domain',
        '⊤': '⊤-kinetic regulator',
        '⊢': '⊢-initiation bootstrap',
        '⊣': '⊣-topological anchor',
    }
    return desc_map.get(dom, f'Fragment {idx+1}')
# ══════════════════════════════════════════════════════════════════
# 2. MONOBASIC CLEAVAGE DETECTION
# ══════════════════════════════════════════════════════════════════
# Many prohormones are cleaved at single R or K in specific contexts:
#   - Proglucagon: GLP-1↔GLP-2 at single R (R at P1, P'1 is often small)
#   - POMC: some single R sites in specific tissue
#   - Pro-neuropeptides: R/K with specific upstream patterns

# Monobasic consensus: (R|K) at P1, small residue at P'1, basic P6 or P4
# Context: [RK] ↓ [GAS] where upstream has basic residues
# Monobasic sites use fixed patterns — no look-behind (Python re limitation)
# Instead we scan position-by-position in detect_monobasic_sites
MONOBASIC_PATTERNS = []

# Proglucagon-specific: the GLP-1 → GLP-2 cleavage is at single R
# after GLP-1 (pos ~160 in human proglucagon)
PROGLUCAGON_SPECIFIC = {
    'glp1_glp2_junction': (r'EGQAAKEFIAWLV', r'[KR]', r'GKGRNDL'),
}


def detect_monobasic_sites(seq: str, known_dibasic: list,
                           proglucagon_mode: bool = False) -> list:
    """Detect monobasic cleavage sites in specific prohormone contexts.
    
    v6: Conservative. Requires ≥2 upstream basic residues AND distance
    ≥30 AA from nearest dibasic site. Suppresses internal sites within
    known protein domains (N-POMC, glucagon internal RR, etc.).
    Only high-confidence monobasic sites are returned.
    """
    sites = []
    existing_positions = {s.position for s in known_dibasic}
    
    # Known domain sequences where internal R/K should NOT be cleaved
    SUPPRESSED_CONTEXTS = [
        (r'FRWDRFGRRNSSS', 'N-POMC'),
        (r'GRRNSSSSGSSGAGQ', 'N-POMC'),
        (r'KYLDSRRAQDFVQ', 'Glucagon'),
        (r'LQDTEEKSR', 'GRPP'),
        (r'GSSGAGQKR', 'Joining Peptide'),
    ]
    
    def in_suppressed_context(pos):
        for pattern, domain in SUPPRESSED_CONTEXTS:
            for m in re.finditer(pattern, seq):
                if m.start() <= pos < m.end():
                    return True
        return False
    
    # Scan position-by-position
    for pos in range(20, len(seq) - 3):
        if seq[pos] not in 'KR':
            continue
        if pos in existing_positions:
            continue
        if in_suppressed_context(pos):
            continue
        
        upstream = seq[max(0,pos-8):pos]
        downstream = seq[pos+1] if pos+1 < len(seq) else ''
        
        upstream_basic = upstream.count('K') + upstream.count('R')
        
        # Require >= 2 upstream basic residues
        if upstream_basic < 2:
            continue
        
        # Check Pro constraints
        if 'P' in seq[max(0,pos-2):pos]:
            continue
        if pos+1 < len(seq) and seq[pos+1] == 'P':
            continue
        
        # Distance from nearest known dibasic site
        nearest = min((abs(pos - db) for db in existing_positions), default=999)
        if nearest < 30:
            continue
        
        # Classify by downstream residue
        conf = 0.0
        enzyme = 'PC2_monobasic'
        
        if downstream in 'GAS':
            conf = 0.45
        elif downstream in 'VIL':
            conf = 0.40
        elif seq[pos] == 'R' and downstream == 'G' and 'R' in upstream[-4:]:
            conf = 0.55
            enzyme = 'prohormone_monobasic'
        
        if conf > 0:
            sites.append(CleavageSite(
                position=pos+1,
                motif=f'{seq[pos]}',
                enzyme_family=enzyme,
                structural_delta=0.3,
                confidence=conf
            ))
            existing_positions.add(pos+1)
    
    # Clustering filter: if multiple monobasic sites are within 15 AA,
    # keep only the first (most N-terminal) — prevents cascading splits.
    sites.sort(key=lambda s: s.position)
    filtered = []
    last_pos = -999
    for site in sites:
        if site.position - last_pos >= 15:
            filtered.append(site)
            last_pos = site.position
    
    # Proglucagon-specific: GLP-1 to GLP-2 junction
    # Only add ONE monobasic site right before GLP-2
    if proglucagon_mode:
        # GLP-2 starts with IAAEFKEWL (conserved across mammals)
        glp2_match = list(re.finditer(r'IAAEFKEWL|IAEFKEWL|HADGSF', seq))
        if glp2_match:
            g2_start = glp2_match[0].start()
            # Look for the last K/R before GLP-2 start
            for offset in range(1, min(8, g2_start)):
                pos = g2_start - offset
                if seq[pos] in 'KR' and pos not in existing_positions:
                    # Check if we already have a site near here
                    if not any(abs(s.position - (pos+1)) < 10 for s in filtered):
                        filtered.append(CleavageSite(
                            position=pos+1,
                            motif=f'{seq[pos]}',
                            enzyme_family='PC1/3_monobasic',
                            structural_delta=0.4,
                            confidence=0.85
                        ))
                        existing_positions.add(pos+1)
                    break
    
    return filtered


# ══════════════════════════════════════════════════════════════════
# 3. CONTEXT-AWARE MERGING
# ══════════════════════════════════════════════════════════════════
# Some dibasic sites are internal to known mature products and
# should be merged. Rules are context-specific.

MERGE_RULES = {
    # Insulin: no internal dibasic sites in mature products
    'insulin': {'internal_sites': [], 'known_products': ['B-chain', 'A-chain']},
    
    # Proglucagon: the RR after glucagon's DFVQWLMNT is a processing
    # site, but RR within glucagon should be suppressed
    'proglucagon': {'internal_sites': [
        ([r'TSDYSKYLDSRRAQDFVQ'], 'Glucagon'),
    ]},
    
    # POMC: internal RK at ~75 within N-POMC should NOT be a site
    'pomc': {'internal_sites': [
        # RK~75 pattern: FRWDRFGRRNSSS - this is within N-POMC
        ([r'MHFRWDRFGRR'], 'N-POMC'),
        # RR~89 pattern: should be merged with N-POMC extension
        ([r'GRRNSSSSGSSGAGQ'], 'N-POMC'),  
        # KR~136: α-MSH/CLIP junction — sometimes processed, sometimes not
        ([r'SYSMEHFRWGKPVGKKRR'], 'ACTH'),  # full ACTH includes α-MSH + CLIP
        # KK~215: γ-LPH/β-endorphin junction — tissue-specific
    ]},
}


def should_merge_fragments(products: list, cleavage_sites: list,
                           sequence: str, name: str = '') -> list:
    """Apply context-aware merge rules to consolidate fragments
    that are known to be one biological product.
    """
    if not products:
        return products
    
    # Determine protein family
    family = 'unknown'
    if 'insulin' in name.lower() or 'preproinsulin' in name.lower():
        family = 'insulin'
    elif 'glucagon' in name.lower() or 'proglucagon' in name.lower():
        family = 'proglucagon'
    elif 'pomc' in name.lower():
        family = 'pomc'
    
    # Check each fragment against merge rules
    merged = []
    skip = set()
    
    for i, prod in enumerate(products):
        if i in skip:
            continue
        
        if family == 'pomc':
            # Merge fragments 1+2+3+... (N-POMC + internal fragments + JP)
            if i == 0 and (match_fingerprint(prod.sequence, FINGERPRINTS['N-POMC']) or
                          re.search(r'GWCLESS', prod.sequence)):
                # Keep merging subsequent fragments until we hit ACTH or β-endorphin
                merged_seq = prod.sequence
                merge_end = prod.end
                for j in range(i+1, len(products)):
                    nxt = products[j]
                    # Stop if this fragment is a known active hormone
                    if any(match_fingerprint(nxt.sequence, FINGERPRINTS.get(name, []))
                           for name in ('ACTH', 'α-MSH', 'β-endorphin', 'β-LPH')):
                        break
                    # Also stop if the fragment is large (>40 AA) and has hormone-like profile
                    nxt_cls = nxt.classification if hasattr(nxt, 'classification') else {}
                    if len(nxt.sequence) > 40 and '◻' not in str(nxt_cls.get('dominant', '')):
                        break
                    merged_seq += nxt.sequence
                    merge_end = nxt.end
                    skip.add(j)
                
                if merge_end > prod.end:
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='N-POMC (pro-γ-MSH)',
                        start=prod.start, end=merge_end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                else:
                    merged.append(prod)
                continue
            
            # Merge α-MSH + CLIP → ACTH
            if i+1 < len(products):
                nxt = products[i+1]
                if (re.search(r'SYSMEHFR', prod.sequence) and 
                    re.search(r'PVKVYPNV', nxt.sequence)):
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='ACTH (containing α-MSH + CLIP)',
                        start=prod.start, end=nxt.end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
            
            # Merge β-LPH + γ-LPH (KK at ~215 splits in some tissues)
            if 'β-LPH' in prod.name and i+1 < len(products):
                nxt = products[i+1]
                # γ-LPH is typically 15-25 AA with Ħ/Ω signature
                if len(nxt.sequence.rstrip('KR')) < 30 and 'β-endorphin' not in nxt.name:
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='β-LPH',
                        start=prod.start, end=nxt.end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
            
            # Merge α-MSH + CLIP → ACTH
            if i+1 < len(products):
                nxt = products[i+1]
                if (re.search(r'SYSMEHFR', prod.sequence) and 
                    re.search(r'PVKVYPNV', nxt.sequence)):
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='ACTH (containing α-MSH + CLIP)',
                        start=prod.start, end=nxt.end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
            
            # Merge β-LPH + γ-LPH (KK at ~215 splits in some tissues)
            if 'β-LPH' in prod.name and i+1 < len(products):
                nxt = products[i+1]
                # γ-LPH is typically 15-25 AA with Ħ/Ω signature
                if len(nxt.sequence.rstrip('KR')) < 30 and 'β-endorphin' not in nxt.name:
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='β-LPH',
                        start=prod.start, end=nxt.end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
        
        if family == 'proglucagon':
            # Glucagon: merge if split by false dibasic
            if i+1 < len(products):
                nxt = products[i+1]
                if (match_fingerprint(prod.sequence, FINGERPRINTS['Glucagon']) and
                    len(nxt.sequence.rstrip('KR')) < 12):
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='Glucagon', start=prod.start, end=nxt.end,
                        sequence=merged_seq, classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
            
            # GLP-1 + intervening + GLP-2? No — these are separate products.
            # But IP-2 should be detected as connector
            if match_fingerprint(prod.sequence, FINGERPRINTS['IP-2']):
                merged.append(MatureProduct(
                    name='IP-2 (GLP-1/GLP-2 spacer)',
                    start=prod.start, end=prod.end,
                    sequence=prod.sequence,
                    classification=prod.classification,
                    is_connecting=True
                ))
                continue
        
        merged.append(prod)
    
    # If no merge rules applied, return original
    if not merged:
        return products
    return merged
# ══════════════════════════════════════════════════════════════════
# 4. ENHANCED PREDICTOR V5
# ══════════════════════════════════════════════════════════════════

class EnhancedPredictorV5:
    """v5 predictor with biological naming, monobasic detection, 
    context-aware merging, and cross-kingdom validation."""

    def predict(self, seq: str, name: str = "protein",
                enable_monobasic: bool = True,
                proglucagon_mode: bool = None) -> ProcessingPrediction:
        """Full enhanced prediction pipeline."""
        # Auto-detect proglucagon mode
        if proglucagon_mode is None:
            proglucagon_mode = 'glucagon' in name.lower() or 'proglucagon' in name.lower()
        
        # Base prediction
        result = predict_processing(seq, name)
        
        # ── Step 1: Monobasic detection ──
        if enable_monobasic:
            mono_sites = detect_monobasic_sites(
                seq, result.cleavage_sites, proglucagon_mode
            )
            if mono_sites:
                result.cleavage_sites.extend(mono_sites)
                result.cleavage_sites.sort(key=lambda s: s.position)
                
                # Re-partition with new sites
                sp_end = result.signal_peptide.end if result.signal_peptide else 0
                cut_positions = [sp_end]
                for site in result.cleavage_sites:
                    cut_positions.append(site.position)
                cut_positions.append(len(seq))
                
                new_products = []
                for i in range(len(cut_positions) - 1):
                    p_start, p_end = cut_positions[i], cut_positions[i+1]
                    if p_end - p_start < 3:
                        continue
                    fragment = seq[p_start:p_end]
                    cls = classify_module(fragment)
                    is_conn = (cls['type'] == 'ground_layer' or 
                               len(fragment) < 10 and cls['profile']['promoted_count'] <= 1)
                    dom = cls.get('dominant', '?')
                    name_p = f'{dom}-domain' if dom != '?' else 'Ground-layer'
                    prod = MatureProduct(
                        name=name_p, start=p_start+1, end=p_end,
                        sequence=fragment, classification=cls,
                        is_connecting=is_conn
                    )
                    if is_conn:
                        result.connecting_peptides.append(prod)
                    else:
                        new_products.append(prod)
                result.mature_products = new_products
        
        # ── Step 2: Name each fragment ──
        prev_motifs = [s.motif for s in result.cleavage_sites]
        next_motifs = prev_motifs[1:] + [None]
        
        for i, prod in enumerate(result.mature_products):
            pm = prev_motifs[i-1] if i > 0 and i-1 < len(prev_motifs) else None
            nm = next_motifs[i-1] if i > 0 and i-1 < len(next_motifs) else None
            bio_name = identify_fragment(
                prod.sequence, prev_motif=pm, next_motif=nm,
                idx=i, total=len(result.mature_products),
                profile=prod.classification.get('profile')
            )
            prod.name = bio_name
        
        # ── Step 3: Context-aware merging ──
        result.mature_products = should_merge_fragments(
            result.mature_products, result.cleavage_sites, seq, name
        )
        
        return result

    def narrative(self, result: ProcessingPrediction) -> str:
        """Generate comprehensive narrative."""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════╗")
        lines.append(f"║  v5 ENHANCED: {result.input_name}")
        lines.append("╚══════════════════════════════════════════════════════════╝")
        full = result.full_profile.summary()
        spec = " | ".join(
            f"{k}:{v}" for k, v in sorted(full['primitive_counts'].items()) if v > 0
        )
        prcnt = full['promoted_density'] * 100
        lines.append(f"Input: {full['length']} AA | Promoted: {prcnt:.1f}% | "
                      f"Dominant: {full['dominant_primitive']} | {spec}")
        if result.signal_peptide:
            sp = result.signal_peptide
            sc = sp.classification
            lines.append(f"\n▸ SIGNAL PEPTIDE: pos {sp.start}–{sp.end} "
                          f"({len(sp.sequence)} AA)")
            lines.append(f"  {sc['description']}")
            lines.append(f"  {sp.sequence}")
        if result.cleavage_sites:
            lines.append(f"\n▸ CLEAVAGE ({len(result.cleavage_sites)} sites):")
            for cs in result.cleavage_sites:
                conf_str = f"◎={cs.confidence:.2f}" if cs.confidence > 0.8 else f"○={cs.confidence:.2f}"
                tag = ' [M]' if 'monobasic' in cs.enzyme_family else ''
                lines.append(f"  pos {cs.position:3d}: {cs.motif:4s} → "
                              f"{cs.enzyme_family:25s} {conf_str}{tag}")
        if result.mature_products:
            lines.append(f"\n▸ PRODUCTS ({len(result.mature_products)}):")
            for i, p in enumerate(result.mature_products):
                seq_short = p.sequence[:40] + ('...' if len(p.sequence) > 40 else '')
                conn = " [connector]" if p.is_connecting else ""
                lines.append(f"\n  [{i+1}] {p.name} ({len(p.sequence)} AA @ "
                              f"{p.start}–{p.end}){conn}")
                lines.append(f"      {p.classification.get('description', '')}")
                lines.append(f"      {seq_short}")
        lines.append(f"\n▸ MAP:")
        if result.signal_peptide:
            lines.append(f"  [SP:{result.signal_peptide.end}] ──┐")
        for cs in result.cleavage_sites:
            symb = '[M]' if 'monobasic' in cs.enzyme_family else f'{cs.motif}'
            lines.append(f"  {symb} ↓ {cs.position}")
        for i, p in enumerate(result.mature_products):
            lines.append(f"  Chain {i+1}: [{p.start}–{p.end}] "
                          f"({len(p.sequence)} AA) {p.name}")
        return '\n'.join(lines)
# ══════════════════════════════════════════════════════════════════
# 5. COMPREHENSIVE TEST SUITE — Cross-Kingdom Validation
# ══════════════════════════════════════════════════════════════════

# ── Insulin (Mammals + Fish) ──
HUMAN_INSULIN = "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN"
RAT_INSULIN = "MALWMHLLPLLALLALWAPAPAQAFVKQHLCGPHLVEALYLVCGERGFFYTPMSRREVEDPQVAQLELGGGPGAGDLQTLALEVAQQKRGIVDQCCTSICSLYQLENYCN"
GUINEA_PIG_INSULIN = "MALWMYLLPLLALLALWAPTPTRFVNQHLCGSHLVEALYLVCGERGFFYTPKSRREAEDPQQVPQELGGGPGAGDLQTLALEVVEQKRGIVDQCCTSICSLYQLENYCN"
DOGFISH_INSULIN = "MALLCFHFLLVLMLPYTSAGPGEPPQKHLCGSHLVDALYLVCGKPGFFYSPKSKRREVEEDGSSGAEPRRAKRGIVEECCRGTCTYDELKIYCI"
ZEBRAFISH_INSULIN = "MAALMMLPLSLALLLLVPLANQAFLQQHLCGSHLVEALYLVCDRGSFFYNPTRKREAEDLQVGVDELGGGPGAGSLQPLALELGKRGIVEQCCHKPCTIFELQNYCN"

# ── Proglucagon family ──
HUMAN_PROGLUCAGON = "MKSIYFVAGLFVMLVQGSWQRSLQDTEEKSRSFSASQADPLSDPDQMNEDKRHSQGTFTSDYSKYLDSRRAQDFVQWLMNTKRNRNNIAKRHDEFERHAEGTFTSDVSSYLEGQAAKEFIAWLVKGRGNRDFNEDLKASGSSERPEDLEISEDLSNVLEKKIAAEFKEWLKNGGPSSGAPPPSGSDVFLDTLLLQEK"

# ── POMC family ──
HUMAN_POMC = "MPRCCSRSGALLLALLLQASMEVRGWCLESSQCQDLTTESNLLECIRACKPDLSAETPMFPGNGDEQPLTENPRKYVMGHFRWDRFGRRNSSSSGSSGAGQKREDVSAGEDCGPLPEGGPEPRSDGAKPGPREGKRSYSMEHFRWGKPVGKKRRPVKVYPNVAENESAEAFPLEFKRELTGQRLREGDGPDGPADDGAGAQADLEHSLLVAAEKKDEGPYRMEHFRWGSPPKDKRYGGFMTSEKSQTPLVTLFKNAIVKNAHKKGQ"

# ── Cross-kingdom: Insect insulin-like (Drosophila DILP2) ──
# Drosophila insulin-like peptide 2 (DILP2)
DROSOPHILA_DILP2 = "MQLRILFCALFLLGASVHAQPPLTSGSGVDSGGLPGDYNRPSDTSLKKRTQNDQVNDCCGHLCTFEQSYLVDCVPQRRSVDGDLMAPLATTVDVNRRRGDQTPGGSRKRKGKDEPETLRPNSEHCCKPLCSYDEALKLVCAQEEFQYCNQ"

# ── Cross-kingdom: Plant prohormone (tomato systemin) ──
# Prosystemin from tomato (Solanum lycopersicum) — plant defense hormone
TOMATO_PROSYS = "METSSTVILFFLVFFTVSLSGQAVTISETPPVKDAVSNYTQMKFCFTPRKKRGARDPVQQAVVKEASGAEATRKEQGSAPEDVREEPLKKKQTDGKPLLSPVAASGGEKTSYEFDPGKEVKPPGRKMDD"

# ── Viral polyprotein: SARS-CoV-2 pp1a NSP1-3 region ──
# First ~1000 AA of SARS-CoV-2 pp1a (NSP1-3)
SARS2_PP1A_NSP1_3 = "MESLVPGFNEKTHVQLSLPVLQVRDVLVRGFGDSVEEVLSEARQHLKDGTCGLVEVEKGVLPQLEQPYVFIKRSDARTAPHGHVMVELVAELEGIQYGRSGETLGVLVPHVGEIPVAYRKVLLRKNGNKGAGGHSYGADLKSFDLGDELGTDPYEDFQENWNTKHSSGVTRELMRELNGGAYTRYVDNNFCGPDGYPLECIKDLLARAGKASCTLSEQLDFIDTKRGVYCCREHEHEIAWYTERSEKSYELQTPFEIKLAKKFDTFNGECPNFVFPLNSIIKTIQPVVEKKKLDGFMGRIRSVYPVASPNECNQMMVKRNNQLTSPAIQRNNYYNVYKPNTEATSKHLMMNLTWIWRHSSVNLYKPGNQATMATASMGVAVILVNVKINTLLLVNSRPSLQSFSFPQFDDRIPSTNTY" 

# Known fragments for validation
KNOWN_FRAGMENTS = {
    "Human Insulin": ["B-chain", "C-peptide", "A-chain"],
    "Rat Insulin": ["B-chain", "C-peptide", "A-chain"],
    "Guinea Pig Insulin": ["B-chain", "C-peptide", "A-chain"],
    "Human Proglucagon": ["GRPP", "Glucagon", "IP-1", "GLP-1", "GLP-2"],
    "Human POMC": ["N-POMC (pro-γ-MSH)", "ACTH (containing α-MSH + CLIP)", 
                   "β-LPH", "β-endorphin"],
}

# Signal peptide benchmarks (sequence start, expected length)
SP_BENCHMARKS = {
    "Human Insulin": 24,
    "Rat Insulin": 24,
    "Human Proglucagon": 20,
    "Human POMC": 22,
    "Drosophila DILP2": 19,
    "Tomato Prosystemin": 24,
}


def run_validation():
    """Run comprehensive validation across all test cases."""
    predictor = EnhancedPredictorV5()
    results = {}
    sp_correct = 0; sp_total = 0
    frag_correct = 0; frag_total = 0

    print("╔" + "═" * 78 + "╗")
    print("║  PROTEIN ENHANCEMENTS v5 — CROSS-KINGDOM VALIDATION" + " " * 17 + "║")
    print("╚" + "═" * 78 + "╝")

    test_cases = {
        "Human Insulin": HUMAN_INSULIN,
        "Rat Insulin": RAT_INSULIN,
        "Guinea Pig Insulin": GUINEA_PIG_INSULIN,
        "Dogfish Insulin": DOGFISH_INSULIN,
        "Zebrafish Insulin": ZEBRAFISH_INSULIN,
        "Human Proglucagon": HUMAN_PROGLUCAGON,
        "Human POMC": HUMAN_POMC,
        "Drosophila DILP2": DROSOPHILA_DILP2,
        "Tomato Prosystemin": TOMATO_PROSYS,
        "SARS-CoV-2 NSP1-3": SARS2_PP1A_NSP1_3,
    }

    for name, seq in test_cases.items():
        print(f"\n{'─' * 80}")
        print(f"  ▶ {name} ({len(seq)} AA)")
        
        # Detect mode
        is_viral = 'sars' in name.lower() or 'cov' in name.lower()
        result = predictor.predict(seq, name=name, 
                                   enable_monobasic=not is_viral)
        results[name] = result
        print(predictor.narrative(result))
        
        prods = result.mature_products
        print(f"\n  Products: {' | '.join(f'{p.name} ({len(p.sequence)}AA)' for p in prods)}")

    # ── Signal Peptide Accuracy ──
    print(f"\n{'═' * 80}")
    print("  SIGNAL PEPTIDE ACCURACY")
    print(f"{'─' * 80}")
    for name, expected in SP_BENCHMARKS.items():
        seq = test_cases[name]
        from protein_enhancements_v4 import improved_signal_peptide_detection
        pred_end, score, _ = improved_signal_peptide_detection(RollingProfile(seq))
        ok = pred_end == expected
        sp_correct += 1 if ok else 0; sp_total += 1
        status = "✓" if ok else f"✗ (off by {abs(pred_end - expected)})" if pred_end else "✗ (none)"
        print(f"  {name:25s} expected={expected:2d} got={pred_end or 0:2d} score={score:5.1f} {status}")
    print(f"\n  SP Accuracy: {sp_correct}/{sp_total} ({100*sp_correct/sp_total:.0f}%)")

    # ── Fragment Naming Accuracy ──
    print(f"\n{'─' * 80}")
    print("  FRAGMENT NAMING ACCURACY")
    print(f"{'─' * 80}")
    for name, expected in KNOWN_FRAGMENTS.items():
        result = results.get(name)
        if result:
            got = [p.name for p in result.mature_products]
            frag_total += len(expected)
            for i, exp in enumerate(expected):
                if i < len(got):
                    ok = got[i] == exp
                    frag_correct += 1 if ok else 0
                    status = "✓" if ok else "✗"
                    print(f"  {name:25s} fragment {i+1}: expected='{exp}' got='{got[i]}' {status}")
                else:
                    print(f"  {name:25s} fragment {i+1}: expected='{exp}' got=MISSING ✗")
                    if i+1 <= len(got):
                        print(f"  {name:25s}  actual[{i+1}]='{got[i]}'")

    print(f"\n  Fragment Naming: {frag_correct}/{frag_total} ({100*frag_correct/frag_total:.0f}%)")

    # ── Primitive Spectra Comparison ──
    print(f"\n{'─' * 80}")
    print("  PRIMITIVE SPECTRA COMPARISON")
    print(f"{'─' * 80}")
    spectra = {}
    for name in test_cases:
        spectra[name] = analyze_spectrum(test_cases[name])
    print(compare_spectra(spectra))

    # ── Summary ──
    print(f"\n{'═' * 80}")
    print("  SUMMARY")
    print(f"{'─' * 80}")
    print(f"  Test cases:       {len(test_cases)} (mammal, fish, insect, plant, virus)")
    print(f"  SP Detection:     {sp_correct}/{sp_total} ({100*sp_correct/sp_total:.0f}%)")
    print(f"  Fragment Naming:  {frag_correct}/{frag_total} ({100*frag_correct/frag_total:.0f}%)")
    print(f"  Total products:   {sum(len(results[n].mature_products) for n in results)}")
    print(f"  Monobasic sites:  {sum(1 for n in results for s in results[n].cleavage_sites if 'monobasic' in s.enzyme_family)}")
    
    # Cross-species Ω analysis
    print(f"\n{'─' * 80}")
    print("  Ω (Glu) CONSERVATION IN INSULIN C-PEPTIDE")
    print(f"{'─' * 80}")
    ins_species = ['Human Insulin', 'Rat Insulin', 'Guinea Pig Insulin', 'Dogfish Insulin']
    for name in ins_species:
        result = results.get(name)
        if result:
            for p in result.mature_products:
                if 'C-peptide' in p.name:
                    glus = p.sequence.count('E')
                    glns = p.sequence.count('Q')
                    print(f"  {name:25s}: C-peptide Ω={glus}, ⊙={glns}, len={len(p.sequence)} AA")
    
    return results


if __name__ == "__main__":
    from protein_stratified_predictor import compare_spectra
    run_validation()
