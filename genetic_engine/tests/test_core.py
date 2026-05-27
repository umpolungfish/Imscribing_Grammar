"""
test_core.py — pytest test suite for the genetic engine.

Run with: python -m pytest tests/ -v
Or:       genetic-engine test
"""

import pytest
from genetic_engine.lattice import B4Element
from genetic_engine.codon import CODON_TABLE, CODON_BY_SYMBOL, FrobeniusStratum
from genetic_engine.primitives import AA_PRIMITIVE_MAP, IGPrimitive, get_primitive_delta
from genetic_engine.editor import B4EditAnalyzer
from genetic_engine.stratum import FrobeniusStratumClassifier
from genetic_engine.guide import FrobeniusGuideDesigner
from genetic_engine.prime import PrimeEditOptimizer
from genetic_engine.chimera import ChimeraDetector
from genetic_engine.verifier import FrobeniusVerifier
from genetic_engine.compiler import EditingCompiler


class TestB4Lattice:
    def test_covering_relations(self):
        assert B4Element.B.covers(B4Element.T)
        assert B4Element.B.covers(B4Element.N)
        assert B4Element.T.covers(B4Element.F)
        assert B4Element.N.covers(B4Element.F)
        assert not B4Element.B.covers(B4Element.F)
        assert not B4Element.T.covers(B4Element.N)

    def test_distances(self):
        assert B4Element.B.lattice_distance(B4Element.F) == 2
        assert B4Element.T.lattice_distance(B4Element.N) == 2
        assert B4Element.B.lattice_distance(B4Element.T) == 1
        assert B4Element.T.lattice_distance(B4Element.F) == 1
        assert B4Element.B.lattice_distance(B4Element.B) == 0

    def test_mapping(self):
        assert B4Element.from_symbol('G') == B4Element.B
        assert B4Element.from_symbol('C') == B4Element.T
        assert B4Element.from_symbol('A') == B4Element.F
        assert B4Element.from_symbol('U') == B4Element.N
        assert B4Element.from_symbol('T') == B4Element.N  # DNA T = U

    def test_join_meet(self):
        assert B4Element.T.join(B4Element.N) == B4Element.B
        assert B4Element.T.meet(B4Element.N) == B4Element.F
        assert B4Element.B.join(B4Element.F) == B4Element.B
        assert B4Element.B.meet(B4Element.F) == B4Element.F


class TestCodonTable:
    def test_count(self):
        assert len(CODON_TABLE) == 64

    def test_stops(self):
        stops = sum(1 for c in CODON_BY_SYMBOL.values() if c.is_stop)
        assert stops == 3

    def test_exact_stratum_count(self):
        exact = sum(1 for c in CODON_BY_SYMBOL.values() if c.is_exact_stratum)
        assert exact == 32

    def test_key_codons(self):
        assert CODON_BY_SYMBOL['AUG'].amino_acid == "Met"
        assert CODON_BY_SYMBOL['AUG'].is_start
        assert CODON_TABLE['UUU'] == 'Phe'
        assert CODON_TABLE['UGG'] == 'Trp'
        assert CODON_TABLE['UAA'] == 'Stop'

    def test_exact_stratum(self):
        assert CODON_BY_SYMBOL['CUU'].is_exact_stratum
        assert CODON_BY_SYMBOL['GGC'].is_exact_stratum
        assert CODON_BY_SYMBOL['GCU'].is_exact_stratum

    def test_split_stratum(self):
        assert CODON_BY_SYMBOL['UUU'].is_split_stratum
        assert CODON_BY_SYMBOL['AAA'].is_split_stratum
        assert not CODON_BY_SYMBOL['UUU'].is_exact_stratum


class TestPrimitives:
    def test_all_aas_mapped(self):
        all_aas = set(CODON_TABLE.values())
        mapped = set(AA_PRIMITIVE_MAP.keys())
        for aa in all_aas:
            assert aa in mapped

    def test_promoted_count(self):
        promoted = sum(1 for p in AA_PRIMITIVE_MAP.values() if p is not None)
        assert promoted == 13  # 12 AAs + Stop

    def test_key_assignments(self):
        assert AA_PRIMITIVE_MAP['Met'] == IGPrimitive.SCOPE
        assert AA_PRIMITIVE_MAP['Trp'] == IGPrimitive.TOPOLOGY
        assert AA_PRIMITIVE_MAP['Cys'] == IGPrimitive.REVERSIBILITY
        assert AA_PRIMITIVE_MAP['Stop'] == IGPrimitive.WINDING

    def test_primitive_delta(self):
        d = get_primitive_delta("Met", "Ile")  # Ð→Ç
        assert d["changed"]
        d2 = get_primitive_delta("Ala", "Ala")  # same
        assert not d2["changed"]


class TestEditAnalysis:
    def test_base_editor_costs(self):
        cbe = B4EditAnalyzer.base_editor_cost("CBE")
        assert cbe["lattice_distance"] == 2
        abe = B4EditAnalyzer.base_editor_cost("ABE")
        assert abe["lattice_distance"] == 2

    def test_silent_edit(self):
        r = B4EditAnalyzer.analyze("GCU", "GCC")
        assert r.silent
        assert r.aa_change == ("Ala", "Ala")

    def test_stratum_crossing(self):
        r = B4EditAnalyzer.analyze("GAA", "GUA")  # Glu→Val, split→split
        # GAA→GUA: G→G(0), A→U(F→N=2), A→A(0) = cost 2
        # Both are split stratum → no crossing
        r2 = B4EditAnalyzer.analyze("GAA", "GCA")  # Glu→Ala, split→exact
        assert r2.stratum_crossing

class TestStratumClassifier:
    def test_classify(self):
        c = FrobeniusStratumClassifier()
        assert c.classify("CUU") == FrobeniusStratum.EXACT
        assert c.classify("UUU") == FrobeniusStratum.SPLIT
        assert c.classify("UAA") == FrobeniusStratum.STOP

    def test_window_analysis(self):
        c = FrobeniusStratumClassifier()
        wr = c.analyze_window(["AUG", "CAU", "GGU", "UAA"])
        assert wr.exact_count >= 1
        assert wr.stop_count == 1
        assert wr.has_boundary


class TestGuideDesigner:
    def test_exact_guide(self):
        g = FrobeniusGuideDesigner.design("GCU")
        assert g.stratum == FrobeniusStratum.EXACT
        assert 'N' in g.guide_sequence

    def test_split_guide(self):
        g = FrobeniusGuideDesigner.design("UUU")
        assert g.stratum == FrobeniusStratum.SPLIT
        assert 'N' not in g.guide_sequence

    def test_stop_guide(self):
        assert FrobeniusGuideDesigner.design("UAA").stratum == FrobeniusStratum.STOP

    def test_off_target_risk(self):
        off = FrobeniusGuideDesigner.off_target_stratum_risk("GCU", ["GCC", "UUU"])
        assert off["cross_stratum_off_targets"] >= 1


class TestPrimeEdit:
    def test_silent_preserved(self):
        pe = PrimeEditOptimizer.optimize("GCU", "GCC")
        assert pe.stratum_preserved
        assert pe.design_score > 0.5

    def test_stratum_crossing_detected(self):
        pe = PrimeEditOptimizer.optimize("GAA", "GCA")  # Glu→Ala, split→exact
        assert not pe.stratum_preserved

    def test_primitive_change(self):
        pe = PrimeEditOptimizer.optimize("UGU", "UGG")  # Cys→Trp
        assert not pe.primitive_invariant


class TestChimera:
    def test_safe_pair(self):
        r = ChimeraDetector.analyze_edit_set([("Lys", "Arg")])
        assert not r.is_trap_state

    def test_trap_pair(self):
        r = ChimeraDetector.analyze_edit_set([("Cys", "Ser"), ("Asp", "Asn")])
        assert r.tensor_risk >= 1.5


class TestVerifier:
    def test_closed_edit(self):
        v = FrobeniusVerifier.verify("GCU", "GCC")
        assert v.frobenius_closed

    def test_open_edit(self):
        v = FrobeniusVerifier.verify("AUG", "UAA")
        assert not v.frobenius_closed

    def test_protocol(self):
        proto = FrobeniusVerifier.verify_protocol([("GCU", "GCC"), ("AUG", "AUU")])
        assert "per_edit" in proto


class TestCompiler:
    def test_simple_compile(self):
        c = EditingCompiler()
        r = c.compile("Met", "Ile")
        assert r.codon_paths
        assert r.composite_score >= 0.0

    def test_multi_compile(self):
        c = EditingCompiler()
        m = c.compile_multi([("Cys", "Ser"), ("His", "Gln")])
        assert "chimera" in m
        assert "edits" in m
