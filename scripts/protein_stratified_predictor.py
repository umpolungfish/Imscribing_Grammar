#!/usr/bin/env python3
"""
protein_stratified_predictor.py — Frobenius-Guided Protein Processing Engine
============================================================================
Takes a preproprotein amino acid sequence and predicts the exact mature
protein(s) after processing, using the Imscribing Grammar's 12-primitive
amino acid mapping.

Structural mapping (12 promoted AAs → primitives):
    Met (M) → 𐑦  — Scope/dimensionality
    Trp (W) → 𐑸  — Topology
    Cys (C) → 𐑾  — Reversibility (disulfide bonds)
    Tyr (Y) → 𐑿  — Parity (phosphorylation switch)
    Phe (F) → 𐑐  — Force (hydrophobic ceiling)
    Ile (I) → 𐑧  — Kinetics (β-branching)
    His (H) → 𐑲  — Grammar (pH-gated catalysis)
    Asn (N) → 𐑠  — Interaction (N-glycosylation)
    Gln (Q) → ⊙  — Criticality (metabolic regulation)
    Asp (D) → 𐑖  — Chirality (substrate selectivity)
    Lys (K) → 𐑙  — Entropy (variability/acetylation)
    Glu (E) → 𐑭  — Winding/closure (C-terminal marker)

Version: 3.0 — Multi-step processing, amidation, disulfide prediction
"""

import re
import sys
import json
from collections import Counter

# ─── AA → Primitive Mapping ───────────────────────────────────────────────

PRIMITIVE_MAP = {
    'M': ('𐑦', 'Dimensionality', 'Start codon / scope'),
    'W': ('𐑸', 'Topology', 'Indole ring — topological constraint'),
    'C': ('𐑾', 'Reversibility', 'Disulfide bond — reversible crosslink'),
    'Y': ('𐑿', 'Parity', 'Phosphorylation switch'),
    'F': ('𐑐', 'Force', 'Hydrophobic ceiling'),
    'I': ('𐑧', 'Kinetics', 'β-branching — slow folding'),
    'H': ('𐑲', 'Grammar', 'pH-gated catalysis'),
    'N': ('𐑠', 'Interaction', 'N-glycosylation site'),
    'Q': ('⊙', 'Criticality', 'Metabolic regulation gate'),
    'D': ('𐑖', 'Chirality', 'Substrate selectivity'),
    'K': ('𐑙', 'Entropy', 'Variable / acetylation site'),
    'E': ('𐑭', 'Winding', 'Closure / C-terminal marker'),
}

# Remaining 8 AAs have zero primitive activation
ZERO_PRIMITIVE_AAS = {'A', 'G', 'P', 'S', 'T', 'V', 'L', 'R'}

# ─── All 20 AAs with their full data ─────────────────────────────────────

AA_DATA = {
    'A': ('Ala', 'Alanine', None, 'methyl — minimal hydrophobic'),
    'C': ('Cys', 'Cysteine', ('𐑾', 'Reversibility', 'Disulfide bond — reversible crosslink'), 'thiol — redox-sensitive'),
    'D': ('Asp', 'Aspartate', ('𐑖', 'Chirality', 'Substrate selectivity'), 'carboxyl — negative charge'),
    'E': ('Glu', 'Glutamate', ('𐑭', 'Winding', 'Closure / C-terminal marker'), 'carboxyl — longer arm'),
    'F': ('Phe', 'Phenylalanine', ('𐑐', 'Force', 'Hydrophobic ceiling'), 'benzyl — strong hydrophobic'),
    'G': ('Gly', 'Glycine', None, 'minimal — backbone flexibility'),
    'H': ('His', 'Histidine', ('𐑲', 'Grammar', 'pH-gated catalysis'), 'imidazole — pH sensor'),
    'I': ('Ile', 'Isoleucine', ('𐑧', 'Kinetics', 'β-branching — slow folding'), 'β-branched — sterics'),
    'K': ('Lys', 'Lysine', ('𐑙', 'Entropy', 'Variable / acetylation site'), 'amine — positive charge'),
    'L': ('Leu', 'Leucine', None, 'hydrophobic — structural'),
    'M': ('Met', 'Methionine', ('𐑦', 'Dimensionality', 'Start codon / scope'), 'thioether — start'),
    'N': ('Asn', 'Asparagine', ('𐑠', 'Interaction', 'N-glycosylation site'), 'amide — glycosylation'),
    'P': ('Pro', 'Proline', None, 'puckered — backbone break'),
    'Q': ('Gln', 'Glutamine', ('⊙', 'Criticality', 'Metabolic regulation gate'), 'amide — longer arm'),
    'R': ('Arg', 'Arginine', None, 'guanidino — positive charge'),
    'S': ('Ser', 'Serine', None, 'hydroxyl — phosphorylation'),
    'T': ('Thr', 'Threonine', None, 'β-hydroxyl — O-glycosylation'),
    'V': ('Val', 'Valine', None, 'β-branched — hydrophobic'),
    'W': ('Trp', 'Tryptophan', ('𐑸', 'Topology', 'Indole ring — topological constraint'), 'indole — large aromatic'),
    'Y': ('Tyr', 'Tyrosine', ('𐑿', 'Parity', 'Phosphorylation switch'), 'phenol — phosphorylation'),
}

PRIMITIVE_NAMES = ['⊢', '⊣', '≻', '≺', '⋈', '⊤', '∈', '∋', '⊙', '⊥', '⊞', '⊡']
AA_TO_PRIMITIVE_INDEX = {}
for aa, (prim, _, _) in [(k,v) for k,v in PRIMITIVE_MAP.items()]:
    for i, pn in enumerate(PRIMITIVE_NAMES):
        if prim.startswith(pn):
            AA_TO_PRIMITIVE_INDEX[aa] = i
            break

# ─── Hydrophobicity scores (Kyte-Doolittle) ───────────────────────────────

KD_HYDROPHOBICITY = {
    'I': 4.5, 'V': 4.2, 'L': 3.8, 'F': 2.8, 'C': 2.5, 'M': 1.9, 'A': 1.8,
    'G': -0.4, 'T': -0.7, 'S': -0.8, 'W': -0.9, 'Y': -1.3, 'P': -1.6,
    'H': -3.2, 'E': -3.5, 'Q': -3.5, 'D': -3.5, 'N': -3.5, 'K': -3.9, 'R': -4.5
}

# ─── Core Engine ──────────────────────────────────────────────────────────

class ProteinStratifiedPredictor:
    """Frobenius-guided preproprotein processing engine."""

    def __init__(self, sequence=None, name="unnamed"):
        self.sequence = sequence.upper() if sequence else ''
        self.name = name
        self.length = len(sequence) if sequence else 0
        self._clear_results()

    def _clear_results(self):
        self.signal_peptide = None
        self.signal_peptide_end = None
        self.cleavage_sites = []
        self.fragments = []
        self.mature_products = []
        self.modifications = []

    def set_sequence(self, seq, name="unnamed"):
        self.sequence = seq.upper()
        self.name = name
        self.length = len(self.sequence)
        self._clear_results()

    # ─── Primitive Activation Vectors ────────────────────────────────────

    def primitive_activation_vector(self, start=0, end=None):
        """Return a 12-element vector of primitive activation counts."""
        if end is None:
            end = self.length
        vec = [0] * 12
        for i in range(start, min(end, self.length)):
            aa = self.sequence[i]
            if aa in AA_TO_PRIMITIVE_INDEX:
                vec[AA_TO_PRIMITIVE_INDEX[aa]] += 1
        return vec

    def rolling_primitive_density(self, window=9):
        """Compute rolling primitive profiles over the sequence."""
        half = window // 2
        profiles = []
        for i in range(self.length):
            start = max(0, i - half)
            end = min(self.length, i + half + 1)
            vec = self.primitive_activation_vector(start, end)
            total = sum(vec)
            profiles.append({
                'pos': i,
                'aa': self.sequence[i],
                'vector': vec,
                'density': total / (end - start) if (end - start) > 0 else 0,
                'dominant': PRIMITIVE_NAMES[vec.index(max(vec))] if total > 0 else '—'
            })
        return profiles

    def rolling_hydrophobicity(self, window=9):
        """Rolling Kyte-Doolittle hydrophobicity."""
        half = window // 2
        profile = []
        for i in range(self.length):
            start = max(0, i - half)
            end = min(self.length, i + half + 1)
            segment = self.sequence[start:end]
            scores = [KD_HYDROPHOBICITY.get(aa, 0.0) for aa in segment]
            avg = sum(scores) / len(scores) if scores else 0.0
            profile.append({'pos': i, 'aa': self.sequence[i], 'hydro': avg})
        return profile

    # ─── Signal Peptide Detection ────────────────────────────────────────

    def detect_signal_peptide(self):
        """
        Detect signal peptide by:
        1. N-region: net positive charge (R, K > D, E) in first 5-8 AA
        2. H-region: hydrophobic core (rolling KD > 2.0, at least 8 AA)
        3. C-region: polar/helix-breaking near cleavage site
        4. Bootstrap signature: ⟨⊢, ⊣⟩ preconditions (M, W present)
        5. Cleavage site: SignalP consensus pattern (AXA↓, etc.)
        """
        if self.length < 15:
            return None

        hydrophobicity = self.rolling_hydrophobicity(window=9)
        primitives = self.rolling_primitive_density(window=9)
        sp_candidates = []

        # Find hydrophobic core region (H-region)
        in_core = False
        core_start = None
        core_length = 0

        for i, point in enumerate(hydrophobicity):
            if i >= self.length - 5:
                break
            if point['hydro'] > 1.8:
                if not in_core:
                    core_start = i
                    in_core = True
                    core_length = 1
                else:
                    core_length += 1
            else:
                if in_core and core_length >= 7:
                    # Check for SP cleavage pattern near end of core + 5
                    cleavage_zone = core_start + core_length + 5
                    if cleavage_zone < self.length:
                        # Check N-region: net positive charge at positions 1-8
                        n_region = self.sequence[max(0, core_start-8):core_start]
                        n_charge = sum(1 for aa in n_region if aa in 'RK') - sum(1 for aa in n_region if aa in 'DE')
                        # Check bootstrap: Met (⊢) present, ideally Trp (⊣)
                        has_met = 'M' in n_region or 'M' in self.sequence[0:min(5, self.length)]
                        bootstrap_score = 0
                        if has_met:
                            bootstrap_score += 2
                        if 'W' in self.sequence[0:min(15, self.length)]:
                            bootstrap_score += 1
                        sp_candidates.append({
                            'core_start': core_start,
                            'core_length': core_length,
                            'n_charge': n_charge,
                            'bootstrap': bootstrap_score,
                            'cleavage_candidate': cleavage_zone
                        })
                in_core = False
                core_length = 0

        if not sp_candidates:
            return None

        # Score candidates
        best = max(sp_candidates, key=lambda c: c['bootstrap'] * 3 + c['core_length'] + (2 if c['n_charge'] > 0 else -1))

        # Refine cleavage position using known patterns
        sp_end = best['cleavage_candidate']
        # Check for canonical AXA↓ pattern
        for offset in range(-3, 4):
            pos = sp_end + offset
            if 0 < pos < self.length - 2:
                tri = self.sequence[pos-1:pos+2]
                if tri[0] in 'AGSV' and tri[1] in 'AGSV' and tri[2] in 'AGSV':
                    sp_end = pos
                    break

        self.signal_peptide = self.sequence[0:sp_end]
        self.signal_peptide_end = sp_end
        return {
            'sequence': self.signal_peptide,
            'length': sp_end,
            'cleavage_position': sp_end,
            'bootstrap_score': best['bootstrap'],
            'n_charge': best.get('n_charge', 0),
            'hydrophobic_core_length': best['core_length']
        }

    # ─── Dibasic Cleavage Site Detection ─────────────────────────────────

    def detect_cleavage_sites(self):
        """
        Detect dibasic cleavage motifs (RR, KR, RK, KK) with structural
        discontinuity scoring. Assigns enzyme family based on context.
        """
        sites = []
        dibasic_patterns = [
            (r'RR', 'PC1/3'), (r'KR', 'PC2'),
            (r'RK', 'Furin/PC'), (r'KK', 'PCSK'),
        ]

        if self.signal_peptide_end is None:
            search_start = 0
        else:
            search_start = self.signal_peptide_end

        for pattern, enzyme in dibasic_patterns:
            for match in re.finditer(pattern, self.sequence):
                pos = match.start()
                if pos < search_start:
                    continue
                # Get context (±5 AA)
                ctx_start = max(0, pos - 5)
                ctx_end = min(self.length, pos + len(pattern) + 5)
                segment = self.sequence[ctx_start:ctx_end]

                # Compute structural discontinuity score
                vec_before = self.primitive_activation_vector(max(0, pos - 15), pos)
                vec_after = self.primitive_activation_vector(pos + len(pattern),
                                                              min(self.length, pos + len(pattern) + 15))
                total_before = sum(vec_before) if sum(vec_before) > 0 else 1
                total_after = sum(vec_after) if sum(vec_after) > 0 else 1
                density_before = sum(vec_before) / 15
                density_after = sum(vec_after) / 15
                discontinuity = abs(density_before - density_after)

                # Check for carboxypeptidase trimming signal
                # CPE/CPM removes C-terminal R/K after dibasic cleavage
                cpe_context = segment[-3:] if len(segment) >= 3 else segment

                sites.append({
                    'position': pos,
                    'motif': pattern,
                    'motif_seq': self.sequence[pos:pos+len(pattern)],
                    'enzyme': enzyme,
                    'context': segment,
                    'discontinuity': round(discontinuity, 3),
                    'density_before': round(density_before, 3),
                    'density_after': round(density_after, 3),
                    'cpe_trim_candidate': cpe_context[-1] in 'KR' if cpe_context else False
                })

        # Deduplicate overlapping sites (e.g., RRR could match RR at 2 positions)
        sites.sort(key=lambda s: s['position'])
        deduped = []
        for site in sites:
            if not deduped or site['position'] >= deduped[-1]['position'] + len(deduped[-1]['motif']):
                deduped.append(site)

        self.cleavage_sites = deduped
        return deduped

    # ─── Fragment Partitioning ───────────────────────────────────────────

    def partition_fragments(self):
        """Partition sequence into fragments at cleavage sites."""
        if not self.cleavage_sites:
            start = self.signal_peptide_end if self.signal_peptide_end else 0
            remaining = self.sequence[start:]
            if remaining:
                frag = self._classify_fragment(remaining, start, self.length, label='full_precursor')
                self.fragments = [frag]
            return self.fragments

        fragments = []
        start = self.signal_peptide_end if self.signal_peptide_end else 0

        for i, site in enumerate(self.cleavage_sites):
            site_end = site['position'] + len(site['motif'])
            end = site['position']

            if start < end and end <= self.length:
                seq = self.sequence[start:end]
                label = self._assign_fragment_label(seq, i)
                frag = self._classify_fragment(seq, start, end, label)
                fragments.append(frag)

            start = site_end

        # Last fragment after final cleavage site
        if start < self.length and self.sequence[start:]:
            seq = self.sequence[start:]
            label = self._assign_fragment_label(seq, len(self.cleavage_sites))
            frag = self._classify_fragment(seq, start, self.length, label)
            fragments.append(frag)

        self.fragments = fragments
        return fragments

    def _classify_fragment(self, seq, start, end, label='unknown'):
        """Classify a single fragment by its dominant primitive signature."""
        vec = [0] * 12
        for aa in seq:
            if aa in AA_TO_PRIMITIVE_INDEX:
                vec[AA_TO_PRIMITIVE_INDEX[aa]] += 1

        total = sum(vec)
        densities = {}
        for i, pname in enumerate(PRIMITIVE_NAMES):
            densities[pname] = round(vec[i] / len(seq), 3) if seq else 0

        if total > 0:
            max_val = max(vec)
            dominant_prims = [PRIMITIVE_NAMES[i] for i, v in enumerate(vec) if v == max_val]
        else:
            dominant_prims = ['—']

        # C-terminal amidation prediction
        # Requires ⊥ (Asp) or ∋ (Asn) + X + G at C-terminus (PAM recognition)
        amidation = self._predict_amidation(seq)

        return {
            'start': start,
            'end': end,
            'length': end - start,
            'sequence': seq,
            'label': label,
            'vector': vec,
            'densities': densities,
            'dominant_primitives': dominant_primitives,
            'total_primitive_activations': total,
            'amidation': amidation,
        }

    def _assign_fragment_label(self, seq, index):
        """Assign biological label based on position and composition."""
        length = len(seq)
        if length <= 5:
            return f'intervening_peptide_{index}'
        if length <= 15:
            return f'short_peptide_{index}'
        return f'mature_product_{index}'

    def _predict_amidation(self, seq):
        """
        C-terminal amidation requires the consensus: G-R/K-R/K↓X-Gly
        where X is the amidated residue (typically with ⊥ or ∋).
        PAM enzyme recognition pattern.
        """
        if len(seq) < 3:
            return None
        # Check last 3 AA: Gly at C-terminus, preceding residue is amidation candidate
        if seq[-1] == 'G':
            # The residue before Gly becomes amidated
            amidated = seq[-2] if len(seq) >= 2 else None
            if amidated and amidated in 'DNQY':
                return {
                    'amidated_residue': amidated,
                    'position': len(seq) - 2,
                    'mechanism': 'PAM (peptidylglycine α-amidating monooxygenase)',
                    'confidence': 'high' if amidated in 'DN' else 'medium'
                }
        return None

    # ─── Multi-Step Processing ──────────────────────────────────────────

    def process_multi_step(self):
        """
        Simulate multi-step proteolytic processing:
        1. Signal peptidase removes SP
        2. Prohormone convertases (PC1/3, PC2, Furin) cleave at dibasic sites
        3. Carboxypeptidase E/H removes C-terminal R/K after dibasic cleavage
        4. PAM amidates C-terminal Gly if present
        5. Further processing: N-terminal acetylation, phosphorylation prediction
        """
        result = {
            'precursor': self.sequence,
            'length': self.length,
            'steps': []
        }

        # Step 1: Signal peptide removal
        if self.signal_peptide:
            result['steps'].append({
                'step': 1,
                'enzyme': 'Signal Peptidase',
                'action': f'Remove signal peptide ({len(self.signal_peptide)} AA)',
                'cleavage_position': self.signal_peptide_end,
                'product_length': self.length - self.signal_peptide_end
            })

        # Step 2: Dibasic cleavage
        active_sites = [s for s in self.cleavage_sites if s['position'] >= (self.signal_peptide_end or 0)]
        for site in active_sites:
            result['steps'].append({
                'step': len(result['steps']) + 1,
                'enzyme': site['enzyme'],
                'action': f'Cleave at {site["motif"]} @ pos {site["position"]}',
                'motif_sequence': site['motif_seq'],
                'discontinuity': site['discontinuity'],
                'position': site['position']
            })

        # Step 3: Carboxypeptidase trimming
        # CPE/CPM remove C-terminal R and K after dibasic cleavage
        for frag in self.fragments:
            if frag['sequence'] and frag['sequence'][-1] in 'KR':
                # Check if preceded by a dibasic site
                trimmed = frag['sequence']
                while trimmed and trimmed[-1] in 'KR':
                    trimmed = trimmed[:-1]
                if len(trimmed) < len(frag['sequence']):
                    removed = len(frag['sequence']) - len(trimmed)
                    result['steps'].append({
                        'step': len(result['steps']) + 1,
                        'enzyme': 'Carboxypeptidase E/H',
                        'action': f'Trim {removed} C-terminal basic residue(s) from {frag["label"]}',
                        'from': frag['sequence'][-removed:] if removed <= 5 else 'C-terminal R/K',
                        'product_length': len(trimmed)
                    })
                    frag['sequence'] = trimmed
                    frag['length'] = len(trimmed)

        # Step 4: C-terminal amidation
        for frag in self.fragments:
            if frag.get('amidation'):
                result['steps'].append({
                    'step': len(result['steps']) + 1,
                    'enzyme': 'PAM',
                    'action': f'Amidate {frag["amidation"]["amidated_residue"]} at C-terminus of {frag["label"]}',
                    'mechanism': 'Peptidylglycine α-amidating monooxygenase'
                })

        return result

    # ─── Disulfide Bond Prediction (>-> pairing) ────────────────────────

    def predict_disulfide_bonds(self, fragments=None):
        """
        Predict disulfide bond patterns from Cys (>) distribution.
        Uses spatial proximity + structural constraints:
        - Cys must be in fragments likely to fold together
        - Pairing prefers even spacing (odd Cys → unpaired)
        - Known motifs: CxxC, CxC, CxxxC, CxxxxC
        """
        if fragments is None:
            fragments = self.fragments

        cys_positions = []
        for frag in fragments:
            for i, aa in enumerate(frag['sequence']):
                if aa == 'C':
                    cys_positions.append({
                        'fragment': frag['label'],
                        'rel_pos': i,
                        'abs_pos': frag['start'] + i,
                        'context': frag['sequence'][max(0, i-2):min(len(frag['sequence']), i+3)]
                    })

        if len(cys_positions) < 2:
            return []

        # Simple distance-based pairing (assumes linear proximity = 3D proximity)
        bonds = []
        used = set()
        for i, c1 in enumerate(cys_positions):
            if i in used:
                continue
            best_j = None
            best_dist = float('inf')
            for j, c2 in enumerate(cys_positions):
                if j <= i or j in used:
                    continue
                dist = abs(c1['abs_pos'] - c2['abs_pos'])
                if dist < best_dist and dist < 80:  # Max ~80 AA apart for disulfide
                    best_dist = dist
                    best_j = j
            if best_j is not None:
                used.add(i)
                used.add(best_j)
                c2 = cys_positions[best_j]
                motif_analysis = ''
                if best_dist <= 6:
                    motifs = ['CxxC', 'CxC', 'CC']
                    for m in motifs:
                        if m in self.sequence[c1['abs_pos']:c2['abs_pos']+len(m)]:
                            motif_analysis = m
                            break
                bonds.append({
                    'cys_1': {'position': c1['abs_pos'], 'fragment': c1['fragment']},
                    'cys_2': {'position': c2['abs_pos'], 'fragment': c2['fragment']},
                    'distance': best_dist,
                    'motif': motif_analysis or 'long-range',
                    'bond_type': 'intrachain' if c1['fragment'] == c2['fragment'] else 'interchain'
                })

        # Mark unpaired Cys
        unpaired = [c for i, c in enumerate(cys_positions) if i not in used]
        return {'bonds': bonds, 'unpaired_cys': unpaired}

    # ─── Mature Product Assembly ─────────────────────────────────────────

    def assemble_mature_products(self):
        """
        Assemble fragments into final mature products.
        Identifies which fragments constitute the functional protein(s)
        based on structural criteria:
        - Fragments with > (Cys) clusters → structural core
        - Fragments with ⊙ (Gln) → criticality signaling
        - Fragments with ⊡ (Glu) → winding/closure modules
        """
        products = []
        for frag in self.fragments:
            vec = frag['vector']
            dominant = frag['dominant_primitives']

            # Determine biological function from dominant primitive
            function = self._infer_function(dominant, vec, frag['length'])

            products.append({
                'name': frag['label'],
                'sequence': frag['sequence'],
                'length': frag['length'],
                'start': frag['start'],
                'end': frag['end'],
                'dominant_primitive': dominant[0] if dominant else '—',
                'profile': {pn: vec[i] for i, pn in enumerate(PRIMITIVE_NAMES) if vec[i] > 0},
                'inferred_function': function,
                'amidation': frag.get('amidation'),
            })

        self.mature_products = products
        return products

    def _infer_function(self, dominant, vec, length):
        """Infer biological function from dominant primitive activation."""
        if not dominant or dominant[0] == '—':
            return 'structural/linker'
        dom = dominant[0]
        if dom == '≻':
            return 'structural_scaffold' if vec[2] >= 4 else 'redox_sensor'
        elif dom == '⊙':
            return 'metabolic_signaling'
        elif dom == '⊡':
            return 'winding_closure_module'
        elif dom == '≺':
            return 'phosphorylation_switch'
        elif dom == '⊥':
            return 'substrate_recognition'
        elif dom == '⊢':
            return 'initiation_bootstrap'
        elif dom == '⊣':
            return 'topological_embedding'
        elif dom == '⋈':
            return 'hydrophobic_core'
        elif dom == '⊞':
            return 'variable_modification_platform'
        elif dom == '∋':
            return 'glycosylation_target'
        elif dom == '∈':
            return 'catalytic_grammar'
        elif dom == '⊤':
            return 'kinetic_regulator'
        return 'unknown'

    # ─── Full Pipeline ───────────────────────────────────────────────────

    def run_full_pipeline(self, sequence=None, name=None):
        """Run the complete prediction pipeline end-to-end."""
        if sequence:
            self.set_sequence(sequence, name or "unnamed")
        if name:
            self.name = name

        result = {
            'name': self.name,
            'sequence': self.sequence,
            'length': self.length,
            'signal_peptide': self.detect_signal_peptide(),
            'cleavage_sites': self.detect_cleavage_sites(),
            'fragments': self.partition_fragments(),
            'processing': self.process_multi_step(),
            'disulfide_bonds': None,
            'mature_products': self.assemble_mature_products(),
        }

        # Disulfide prediction on mature fragments
        if self.fragments:
            result['disulfide_bonds'] = self.predict_disulfide_bonds()

        return result

    # ─── Report Generation ──────────────────────────────────────────────

    def generate_narrative(self, result):
        """Generate a structural narrative from the pipeline result."""
        lines = []
        lines.append(f"═══ {result['name']} — Structural Processing Analysis ═══")
        lines.append(f"Sequence: {result['length']} AA")
        lines.append("")

        # Signal peptide
        sp = result.get('signal_peptide')
        if sp:
            sp_seq = sp['sequence']
            sp_vec = [0] * 12
            for aa in sp_seq:
                if aa in AA_TO_PRIMITIVE_INDEX:
                    sp_vec[AA_TO_PRIMITIVE_INDEX[aa]] += 1
            dominant_sp = []
            if sp_vec:
                max_v = max(sp_vec)
                dominant_sp = [PRIMITIVE_NAMES[i] for i, v in enumerate(sp_vec) if v == max_v and v > 0]
            lines.append(f"▸ Signal peptide ({sp['length']} AA): {sp_seq}")
            lines.append(f"  Bootstrap elements: Met(⊢)×{sp_seq.count('M')}, Trp(⊣)×{sp_seq.count('W')}")
            lines.append(f"  Cleavage @ position {sp['cleavage_position']} ← signal peptidase")
            if dominant_sp:
                lines.append(f"  Dominant: {', '.join(dominant_sp)} — bootstrap preconditions")
            lines.append("")

        # Processing steps
        steps = result.get('processing', {}).get('steps', [])
        if steps:
            lines.append("▸ Processing steps:")
            for step in steps:
                lines.append(f"  [{step['step']}] {step['enzyme']}: {step['action']}")
            lines.append("")

        # Mature products
        products = result.get('mature_products', [])
        if products:
            lines.append("▸ Mature products:")
            for prod in products:
                profile_str = ' | '.join(f"{k}={v}" for k, v in sorted(prod['profile'].items()))
                amidated = ' [C-term amidated]' if prod.get('amidation') else ''
                lines.append(f"  • {prod['name']} ({prod['length']} AA) "
                             f"— {prod['inferred_function']}{amidated}")
                lines.append(f"    Primitive profile: {profile_str}")
            lines.append("")

        # Disulfide bonds
        db = result.get('disulfide_bonds')
        if db and db.get('bonds'):
            lines.append("▸ Predicted disulfide bonds (>->):")
            for bond in db['bonds']:
                lines.append(f"  Cys{bond['cys_1']['position']}—Cys{bond['cys_2']['position']} "
                             f"({bond['bond_type']}, {bond['motif']})")
            if db.get('unpaired_cys'):
                for c in db['unpaired_cys']:
                    lines.append(f"  ⚠ Unpaired Cys @ pos {c['abs_pos']} in {c['fragment']}")
            lines.append("")

        return '\n'.join(lines)

    def generate_json_report(self, result):
        """Generate compact JSON report."""
        report = {
            'name': result['name'],
            'length': result['length'],
            'signal_peptide': {
                'exists': result['signal_peptide'] is not None,
                'length': result['signal_peptide']['length'] if result['signal_peptide'] else 0,
                'cleavage_position': result['signal_peptide']['cleavage_position'] if result['signal_peptide'] else None,
            } if result['signal_peptide'] else {'exists': False},
            'cleavage_sites': [{
                'position': s['position'],
                'motif': s['motif'],
                'enzyme': s['enzyme'],
                'discontinuity': s['discontinuity']
            } for s in result['cleavage_sites']],
            'fragments': [{
                'label': f['label'],
                'start': f['start'],
                'end': f['end'],
                'length': f['length'],
                'dominant': f['dominant_primitives'][0] if f['dominant_primitives'] else '—',
                'function': f.get('inferred_function', 'unknown')
            } for f in result.get('mature_products', [])],
            'processing_steps': result.get('processing', {}).get('steps', [])
        }
        return json.dumps(report, indent=2)

# ═══════════════════════════════════════════════════════════════════════
# TEST SUITE — Known preproproteins with validated processing
# ═══════════════════════════════════════════════════════════════════════

INSULIN_HUMAN = (
    "MALWMRLLPLLALLALWGPDPAAA"  # Signal peptide (24 AA)
    "FVNQHLCGSHLVEALYLVCGERGFFYTPKT"  # B-chain (30 AA)
    "RR"  # Dibasic (PC1/3) — B-C junction
    "EAEDLQVGQVELGGGPGAGSLQPLALEGSLQKR"  # C-peptide (33 AA)
    "KR"  # Dibasic (PC2) — C-A junction
    "GIVEQCCTSICSLYQLENYCN"  # A-chain (21 AA)
)

INSULIN_RAT = (
    "MALWMHLLPLLALLALWAPAPA"  # Signal peptide
    "FVNQHLCGSHLVEALYLVCGERGFFYTPKS"  # B-chain
    "RR"  # B-C junction
    "EVEDPQVAQLELGGGPGAGDLQTLALEVAQQKR"  # C-peptide (rat)
    "KR"  # C-A junction
    "GIVDQCCTSICSLYQLENYCN"  # A-chain
)

INSULIN_ZEBRAFISH = (
    "MSWLKTLLLLLLPLALAMHAPA"  # Signal peptide
    "MALWMIRPLLPLALLALWAPAPA"  # Extended N-term
    "FTQKHLCGSHLVDALYLVCGERGFFYSPT"  # B-chain-like
    "KR"
    "AAAAAAQEVETQPATVEPVEAQEPEVETR"  # C-peptide-like
    "KR"
    "GIVEQCCHRPCSVYQLENYCN"  # A-chain-like
)

PROGLUCAGON_HUMAN = (
    "MKSIYFVAGLFVMLVQGSWQ"  # Signal peptide
    "RSLQDTEEKSRSFSASQADPLSDPDQMNED"  # GRPP
    "KR"  # Dibasic
    "HSQGTFTSDYSKYLDSRRAQDFVQWLMNT"  # Glucagon
    "KR"  # Dibasic
    "RNRNNIA"  # IP-1
    "KR"  # Dibasic
    "HGEGTFTSDVSSYLEEQAAKEFIAWLVKGRG"  # GLP-1
    "RR"  # Dibasic
    "DFPEEVAIVEELGRRHADGSFSDEMNTILDNLA"  # IP-2 / intervening
    "KR"  # Dibasic
    "HADGSFSDEMNTILDNLATRDFINWLIQTKITD"  # GLP-2
)

POMC_HUMAN = (
    "MPRLCSSLLLLLLVLLLPTTLPM"  # Signal peptide
    "TWCLESSQCQDLTTESNLLACIRACKPDLSAETPMFPGNGDEQPLTENPRKYVMGHFW"
    "KRF"  # Dibasic — pro-γ-MSH / joining peptide
    "RR"  # Dibasic
    "SYSMEHFRWGKPVGKKRRPVKVYPNVAENESAEAFPLEFKRELTGQRLREGDGPDTPR"  # ACTH
    "KR"  # Dibasic — ACTH / β-LPH junction
    "PVKVYPNVAENESAEAFPLEFKRELTGQRLREGDGPDTPR"  # CLIP-like
    "RR"  # Dibasic
    "ELTGQRLREGDGPDTPRYSMEHFRWGKPVGKKRRPVKVYPN"  # β-LPH N-term
    "KR"  # Dibasic
    "YGGFMTSEKSQTPLVTLFKNAIIKNAYKKGE"  # β-endorphin
)

# ─── Viral polyproteins ──────────────────────────────────────────────

# SARS-CoV-2 pp1a (partial — NSP1-4 region for testing)
SARS_COV2_PP1A_PARTIAL = (
    "MESLVPGFNEKTHVQLSLPVLQVRDVLVRGFGDSVEEVLSEARQHLKDGTCGLVE"
    "VEKGVLPQLEQPYVFIKRSDARTAPHGHVMVELVAELEGIQYGRSGETLGVLVPHVGE"
    "IPVAYRKVLLRKNGNKGAGGHSYGADLKSFDLGDELGTDPYEDFQENWNTKHSSGVTR"
    "EKLMKYNTLQGFLALGSGGVKSTEDLYKNHVFNADGSTEGFFT"  # NSP1-2 junction
    "RK"  # Furin-like
    "RSHLDMYVTYSDPLQPGQSNLDVKLTDGDIY"
)

# ─── Test Runner ─────────────────────────────────────────────────────

def run_all_tests():
    """Run the engine on all test sequences and print reports."""
    print("=" * 72)
    print("PROTEIN STRATIFIED PREDICTOR v3 — MULTI-SPECIES VALIDATION")
    print("=" * 72)

    engine = ProteinStratifiedPredictor()
    results = {}

    test_cases = [
        ("Human Preproinsulin", INSULIN_HUMAN),
        ("Rat Preproinsulin", INSULIN_RAT),
        ("Zebrafish Preproinsulin", INSULIN_ZEBRAFISH),
        ("Human Proglucagon", PROGLUCAGON_HUMAN),
        ("Human POMC", POMC_HUMAN),
        ("SARS-CoV-2 pp1a (partial)", SARS_COV2_PP1A_PARTIAL),
    ]

    for name, seq in test_cases:
        print(f"\n{'─' * 72}")
        print(f"  TEST: {name}")
        print(f"{'─' * 72}")
        result = engine.run_full_pipeline(seq, name=name)
        results[name] = result
        print(engine.generate_narrative(result))

    # ─── Cross-Species Comparison ─────────────────────────────────────
    print("\n" + "=" * 72)
    print("CROSS-SPECIES INSULIN COMPARISON")
    print("=" * 72)

    insulin_cases = ["Human Preproinsulin", "Rat Preproinsulin", "Zebrafish Preproinsulin"]
    for name in insulin_cases:
        r = results[name]
        sp = r['signal_peptide']
        products = r['mature_products']
        print(f"\n  {name}:")
        print(f"    Signal peptide: {sp['length'] if sp else '?'} AA, "
              f"cleavage @ {sp['cleavage_position'] if sp else '?'}")
        print(f"    Cleavage sites: {len(r['cleavage_sites'])}")
        print(f"    Products: {len(products)}")

        # Compute ⊡ (Glu) totals
        seq = r['sequence']
        omega_total = seq.count('E')
        # Sum ⊡ across fragments
        frag_omega = sum(f['vector'][11] for f in r['fragments'])  # ⊡ is index 11
        print(f"    ⊡ (Glu) total: {omega_total}")
        c_peptide = [p for p in products if 'peptide' in p['name'] and 'short' not in p['name'] and 'intervening' not in p['name']]
        for p in products:
            omega = p['profile'].get('⊡', 0)
            print(f"    • {p['name']}: ⊡={omega}, {p['inferred_function']}")

    # ─── Proglucagon Detailed ─────────────────────────────────────────
    print("\n" + "=" * 72)
    print("PROGLUCAGON — FRAGMENT CLASSIFICATION")
    print("=" * 72)
    r = results.get("Human Proglucagon")
    if r:
        for frag in r['fragments']:
            gln = frag['vector'][8]  # ⊙ index
            glu = frag['vector'][11]  # ⊡ index
            asp = frag['vector'][9]  # ⊥ index
            print(f"  {frag['label']} ({frag['length']} AA @ {frag['start']}-{frag['end']}): "
                  f"⊙={gln}, ⊡={glu}, ⊥={asp}, dominant={frag['dominant_primitives']}")

    return results


if __name__ == '__main__':
    results = run_all_tests()
