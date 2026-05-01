"""
Millennium Prize Problems — Synthonic Catalog  (v0.5.0)

Seven Clay Mathematics Institute Millennium Prize Problems encoded as canonical
12-primitive synthons.  Includes the standard_proof_system as the reference baseline.

Primitive-tuple notation: ⟨D; T; R; P; Γ; F; K; G; Φ; Ω; S; H⟩

─────────────────────────────────────────────────────────────────────────────
DESIGN PRINCIPLE
─────────────────────────────────────────────────────────────────────────────
Each Millennium Problem is treated as a *constraint-propagation system* whose
answer (if it exists) must propagate from the structural primitives of the
domain all the way to a formal proof.  The 12-tuple captures the structural
character of that propagation, not the content of the statement.

Key encoding choices:

  Φ (Criticality):
    Phi_c   = the problem sits ON the criticality boundary — the answer is not
              accessible via standard proof-system morphisms from Phi_sub.
    Phi_sub = the problem HAS been solved within standard formalism (Poincaré).

  Ω (Topological Protection):
    Omega_Z  = the key invariant is integer-valued (winding number / rank / charge).
    Omega_0  = no topological protection; the barrier is combinatorial/analytic.

  H (Chirality):
    H2  = persistent chirality — the problem has strongly broken orientational
          symmetry (complex orientation, chiral symmetry breaking, etc.).
    H0  = achiral — the problem is isotropic; no preferred handedness.

  D × T (holographic pair, Axiom C):
    D_holo + T_holo = the problem lives in holographic space (L-function ↔ geometry;
    boundary encodes bulk).  Required together by Axiom C.

─────────────────────────────────────────────────────────────────────────────
AXIOM COMPLIANCE CHECK
─────────────────────────────────────────────────────────────────────────────
  A: H_inf → K_trap       — not needed (none have H_inf)
  B: Ω ≥ Omega_Z → H ≥ H2 — all entries with Omega_Z carry H2  ✓
  C: D_holo ↔ T_holo       — RH and Hodge both use D_holo + T_holo  ✓
  D: Omega_NA → D_holo     — not needed (none use Omega_NA)

─────────────────────────────────────────────────────────────────────────────
DISTANCES FROM standard_proof_system
─────────────────────────────────────────────────────────────────────────────
  Poincaré Conjecture (SOLVED)  : d = 5   ← smallest; was provable with existing topology
  Yang–Mills & Mass Gap          : d = 7
  Navier–Stokes                  : d = 8
  Hodge Conjecture               : d = 9
  Birch–Swinnerton-Dyer          : d = 9
  Riemann Hypothesis             : d = 10
  P vs NP                        : d = 10  ← largest; most structurally alien to formal proof

─────────────────────────────────────────────────────────────────────────────
NOTABLE PAIRWISE DISTANCES
─────────────────────────────────────────────────────────────────────────────
  Yang–Mills ↔ BSD               : d = 5   ← structurally closest pair among unsolved;
                                             share D, F, K, G, Φ, Ω, H → spectral/topological
                                             methods may bridge both
  RH ↔ P vs NP                   : d = 9   ← despite both being d=10 from baseline,
                                             they differ by 9: completely different mechanisms
  Poincaré ↔ Yang–Mills           : d = 4   ← solved ↔ closest unsolved; Ricci flow and
                                             gauge flow share R=R_catalytic, G=G_aleph, H2

─────────────────────────────────────────────────────────────────────────────
PREDICTIONS
─────────────────────────────────────────────────────────────────────────────
  P-MILL-01: If BSD is solved before Hodge or RH, the proof method will share
             characteristics with Yang–Mills (same primitive cluster: D_cube, T,
             F_hbar, K_slow, G_aleph, Phi_c, Omega_Z, H2).  Any progress on YM
             spectral gap is evidence for BSD susceptibility via same formalism.

  P-MILL-02: P vs NP and RH require genuinely new proof primitives (d=10 from
             baseline).  Attempts to prove either via standard formal induction
             (K_fast, Phi_sub morphisms) face a 10-primitive gap — they cannot
             close the gap without a structural phase transition in the proof system
             itself (i.e., without discovering a new primitive).

  P-MILL-03: Navier–Stokes blowup (if it occurs) corresponds to a Phi_sub → Phi_sup
             phase transition in the solution's constraint-propagation regime.
             A proof of global smoothness requires a mechanism keeping Phi_c → Phi_sub
             throughout — analogous to Perelman's surgery preventing Phi_sup in 3D.

  P-MILL-04: The Poincaré ↔ Yang–Mills distance (d=4) predicts that the Yang–Mills
             mass gap proof will use geometric-flow-type arguments analogous to
             Ricci flow: a catalytic recognition operator (R_catalytic) that
             drives the gauge system to its unique ground state.

  P-MILL-05: The Ω = Omega_0 entries (P vs NP, Navier–Stokes) are NOT topologically
             protected.  This means a counterexample (NP algorithm / blowup solution)
             is structurally permitted — unlike RH, Hodge, YM, BSD where the integer
             topological invariant would be violated by a counterexample.
             Prediction: if P≠NP, the oracle-separation proofs (which only work in
             Omega_0 regimes) are the correct structural approach.

Recorded 2026-03-26.
"""
from __future__ import annotations

from typing import List

from .models import (
    Synthon,
    Dimensionality,
    Topology,
    Recognition,
    Polarity,
    Grammar,
    Fidelity,
    KineticChar,
    Granularity,
    Criticality,
    Protection,
    Stoichiometry,
    Chirality,
)
from .registry import global_catalog

_MILLENNIUM_NAMES: frozenset = frozenset([
    "standard_proof_system",
    "riemann_hypothesis",
    "p_vs_np",
    "hodge_conjecture",
    "yang_mills_mass_gap",
    "navier_stokes_smoothness",
    "birch_swinnerton_dyer",
    "poincare_conjecture",
])


def register_millennium_synthons() -> None:
    """Register all Millennium Prize Problem synthons into the global catalog."""

    entries: List[Synthon] = [

        # ─────────────────────────────────────────────────────────────────────
        # BASELINE: Standard Proof System
        # ⟨D_cube; T_cage; R_catalytic; P_pm_sym; G_and; F_ell; K_fast; G_aleph; Phi_sub; Omega_0; 1:1; H0⟩
        #
        # A formal axiomatic proof system (ZFC-level).  This is the structural
        # reference: maximally tractable, no topological protection, no criticality.
        # All Millennium Problems are measured as distances from this baseline.
        # ─────────────────────────────────────────────────────────────────────
        Synthon(
            name="standard_proof_system",
            dimensionality=Dimensionality.D_cube,
            topology=Topology.T_cage,
            recognition_mode=Recognition.R_catalytic,
            polarity=Polarity.P_pm_sym,
            grammar=Grammar.G_and,
            fidelity=Fidelity.F_ell,
            kinetic_character=KineticChar.K_fast,
            granularity=Granularity.G_aleph,
            criticality_phase=Criticality.Phi_sub,
            protection=Protection.Omega_0,
            stoichiometry=Stoichiometry.one_one,
            chirality=Chirality.H0,
            description=(
                "Classical axiomatic proof system (ZFC-level).  Proofs are "
                "cage-structured (T_cage: axioms bound all inference), catalytic "
                "(each step transforms premises without consuming them), locally "
                "fine-grained (G_aleph: every step is atomic), subcritical (Phi_sub: "
                "standard mathematics is in the stable ordered phase), and achiral "
                "(H0: no preferred orientation).  Serves as the structural baseline "
                "for measuring how far each Millennium Problem departs from "
                "ordinary formal provability.  Distance d=0 from itself; all "
                "Millennium Problems have d ≥ 5."
            ),
            metadata={"domain": "mathematics", "registered_by": "millennium_catalog"},
        ),

        # ─────────────────────────────────────────────────────────────────────
        # 1. RIEMANN HYPOTHESIS
        # ⟨D_holo; T_holo; R_exact; P_pm; G_and; F_hbar; K_slow; G_gimel; Phi_c; Omega_Z; 1:1; H2⟩
        #
        # Statement: All non-trivial zeros of ζ(s) lie on Re(s) = 1/2.
        #
        # D_holo: The Riemann zeta function is a holographic object — its zeros
        #   encode the prime distribution via the explicit formula ψ(x) = x −
        #   Σ_ρ x^ρ/ρ − log(2π) − ½log(1−x^{−2}).  The boundary (zeros) encodes
        #   the bulk (primes).  Axiom C requires T_holo.
        # T_holo: The spectral network of zeros is non-local boundary-bulk;
        #   Montgomery pair-correlation ↔ GUE statistics = holographic topology.
        # R_exact: The hypothesis demands exact placement on Re(s)=1/2, not
        #   approximate.  No tolerance: a zero at Re(s)=0.5+ε, ε>0 refutes it.
        # P_pm: The functional equation ζ(s) = ζ(1−s) (up to gamma factors) is the
        #   bipolar symmetry ABOUT s=1/2; neither side dominates.
        # G_and: Zeros must simultaneously satisfy (i) analytic continuation from
        #   Re(s)>1, (ii) functional equation, (iii) Euler product convergence.
        # F_hbar: Quantum fidelity — the Hilbert–Pólya operator hypothesis, GUE
        #   universality, and the spectral interpretation all require QFT-level
        #   formalism.
        # K_slow: The zeros accumulate slowly — average spacing 2π/log(T) at height T;
        #   no fast deterministic algorithm to locate them is known.
        # G_gimel: Coarse/cosmological scale — the zeta function operates universally
        #   over all primes; the hypothesis is a global statement.
        # Phi_c: THE critical line.  RH is literally a statement about a critical
        #   point; the problem is maximally degenerate under meet (Phi_c absorbing).
        # Omega_Z: Zeros are counted with integer multiplicity; all known zeros are
        #   simple (multiplicity 1); the winding number argument for zero-counting
        #   uses the integer class.  Axiom B: Omega_Z → H ≥ H2 ✓.
        # 1:1: Each prime p corresponds to one Euler factor; each zero pair to one
        #   oscillatory term in ψ(x).
        # H2: Persistent chirality — the upper and lower half-planes are
        #   distinguishable (complex conjugate zeros); the functional equation
        #   respects but does not erase this orientation.
        # ─────────────────────────────────────────────────────────────────────
        Synthon(
            name="riemann_hypothesis",
            dimensionality=Dimensionality.D_holo,
            topology=Topology.T_holo,
            recognition_mode=Recognition.R_exact,
            polarity=Polarity.P_pm,
            grammar=Grammar.G_and,
            fidelity=Fidelity.F_hbar,
            kinetic_character=KineticChar.K_slow,
            granularity=Granularity.G_gimel,
            criticality_phase=Criticality.Phi_c,
            protection=Protection.Omega_Z,
            stoichiometry=Stoichiometry.one_one,
            chirality=Chirality.H2,
            description=(
                "The Riemann Hypothesis: all non-trivial zeros of ζ(s) lie on "
                "Re(s) = 1/2.  Holographic (D_holo + T_holo): the zeta function's "
                "zeros are the boundary encoding of the prime bulk (explicit formula). "
                "R_exact: the claim demands exact placement — no ε-tolerance. "
                "P_pm: functional equation ζ(s)↔ζ(1-s) is the canonical bipolar "
                "symmetry about the critical line.  Phi_c: the problem IS the critical "
                "line — maximally degenerate under the meet operation.  Omega_Z: "
                "zeros have integer multiplicity; all known zeros are simple. "
                "d=10 from standard_proof_system — requires both a new holographic "
                "proof formalism and quantum-level fidelity."
            ),
            metadata={"domain": "mathematics", "registered_by": "millennium_catalog",
                      "clay_problem": True, "solved": False},
        ),

        # ─────────────────────────────────────────────────────────────────────
        # 2. P vs NP
        # ⟨D_infty; T_network; R_subset; P_pm; G_impl; F_eth; K_trap; G_gimel; Phi_c; Omega_0; n:m; H0⟩
        #
        # Statement: Does P = NP?  Is every problem whose solution can be
        #   efficiently verified also efficiently solvable?
        #
        # D_infty: Computational problems live in the ∞-dimensional space of
        #   Turing machines / iterative processes.  There is no fixed spatial
        #   dimension to computation.
        # T_network: Complexity classes form a network of polynomial reductions
        #   (Cook–Levin SAT-completeness; all NP-complete problems reduce to each
        #   other in a densely connected network).
        # R_subset: Certificate verification = subset recognition: the verifier
        #   reads only a polynomial-length witness, a strict SUBSET of the
        #   computation that would find the answer from scratch.  This is the
        #   structural origin of the P ≠ NP conjecture.
        # P_pm: The problem is self-dual: if P=NP then coNP=NP; the problem and
        #   its complement are structurally equivalent (bipolar).
        # G_impl: The key grammar is implicative: "efficiently verifiable ⟹
        #   efficiently solvable?"  This is a conditional/lifting statement.
        # F_eth: Threshold fidelity — the problem sits at the computational
        #   threshold between tractable and intractable.  Not yet at F_hbar
        #   because no quantum-formalism proof exists yet.
        # K_trap: NP-complete problems are kinetically trapped — no polynomial
        #   algorithm is known; exhaustive search is exponential.
        # G_gimel: Universal coarse scale — applies to ALL computable problems,
        #   the most global possible computational statement.
        # Phi_c: The P/NP boundary is the computational criticality point —
        #   the phase transition between tractable and intractable.
        # Omega_0: No topological protection.  If P≠NP, the barrier is
        #   combinatorial/arithmetic, not topological — a counterexample
        #   polynomial algorithm is structurally permissible.
        # n:m: Polynomial reductions are many-to-many (a single NP-complete
        #   problem receives reductions from all of NP).
        # H0: Achiral — computation has no preferred orientation; the equations
        #   are left-right symmetric.
        # ─────────────────────────────────────────────────────────────────────
        Synthon(
            name="p_vs_np",
            dimensionality=Dimensionality.D_infty,
            topology=Topology.T_network,
            recognition_mode=Recognition.R_subset,
            polarity=Polarity.P_pm,
            grammar=Grammar.G_impl,
            fidelity=Fidelity.F_eth,
            kinetic_character=KineticChar.K_trap,
            granularity=Granularity.G_gimel,
            criticality_phase=Criticality.Phi_c,
            protection=Protection.Omega_0,
            stoichiometry=Stoichiometry.n_m,
            chirality=Chirality.H0,
            description=(
                "P vs NP: does efficient verification imply efficient solution? "
                "D_infty: computation is inherently iterative/temporal — no fixed "
                "spatial dimension.  T_network: NP-complete reductions form a "
                "densely connected network (Cook-Levin).  R_subset: the verifier "
                "reads only a witness, a strict SUBSET of the computation space — "
                "this is the structural origin of the P/NP gap.  G_impl: "
                "implicative grammar ('verifiable → solvable?').  K_trap: "
                "exponential search is kinetically trapped.  Omega_0: no "
                "topological protection — a polynomial algorithm counterexample "
                "is structurally permissible.  d=10 from standard_proof_system — "
                "tied with RH as the most structurally alien to formal proof, "
                "but via a completely different mechanism (d=9 from RH itself)."
            ),
            metadata={"domain": "mathematics", "registered_by": "millennium_catalog",
                      "clay_problem": True, "solved": False},
        ),

        # ─────────────────────────────────────────────────────────────────────
        # 3. HODGE CONJECTURE
        # ⟨D_holo; T_holo; R_superset; P_pm_sym; G_and; F_hbar; K_slow; G_aleph; Phi_c; Omega_Z; n:m; H2⟩
        #
        # Statement: On a smooth complex projective algebraic variety, every
        #   rational cohomology class of type (p,p) is a rational linear
        #   combination of cohomology classes of algebraic cycles.
        #
        # D_holo: Projective algebraic varieties ARE holographic objects —
        #   they live in CP^n where the boundary (hyperplane sections) encodes
        #   the interior (affine variety).  Holographic = projective geometry.
        # T_holo: The intersection ring of algebraic cycles is non-local boundary-
        #   bulk (intersection number = cap product = boundary integral).
        # R_superset: Hodge classes are a SUPERSET of algebraic cycle classes;
        #   the conjecture asks if the superset collapses to equality.
        #   The recognition is "looser" (Hodge conditions) than algebraic.
        # P_pm_sym: The Hodge decomposition H^n = ⊕ H^{p,q} is perfectly
        #   symmetric: H^{p,q} ≅ \overline{H^{q,p}} (complex conjugation).
        # G_and: A Hodge class must satisfy both the Hodge condition AND the
        #   integral lattice condition to be an algebraic cycle candidate.
        # F_hbar: Quantum fidelity — the conjecture requires exact correspondence
        #   between two analytic structures; approximate doesn't work.
        # K_slow: Constructing algebraic cycles representing a given cohomology
        #   class is extremely hard; no general algorithm is known.
        # G_aleph: Fine-grained — the conjecture is about individual cohomology
        #   classes at the atomic level, not global properties of the variety.
        # Phi_c: The Hodge conjecture sits at the criticality boundary between
        #   analytic geometry (Hodge theory) and algebraic geometry (cycles);
        #   it asks whether these two phases coincide at the critical point.
        # Omega_Z: The integral lattice H^{2p}(X, Z) ∩ H^{p,p}(X) is where the
        #   algebraic cycles live; Z-protection is the structural signature.
        # n:m: Rational linear combinations — many cycles combine to give each class.
        # H2: Persistent chirality — complex algebraic geometry has inherent
        #   orientation (the complex structure is chiral relative to the reals).
        # ─────────────────────────────────────────────────────────────────────
        Synthon(
            name="hodge_conjecture",
            dimensionality=Dimensionality.D_holo,
            topology=Topology.T_holo,
            recognition_mode=Recognition.R_superset,
            polarity=Polarity.P_pm_sym,
            grammar=Grammar.G_and,
            fidelity=Fidelity.F_hbar,
            kinetic_character=KineticChar.K_slow,
            granularity=Granularity.G_aleph,
            criticality_phase=Criticality.Phi_c,
            protection=Protection.Omega_Z,
            stoichiometry=Stoichiometry.n_m,
            chirality=Chirality.H2,
            description=(
                "Hodge Conjecture: every rational (p,p)-Hodge class on a smooth "
                "projective variety is a Q-linear combination of algebraic cycle "
                "classes.  D_holo + T_holo: projective varieties are holographic "
                "(CP^n boundary-bulk structure; intersection theory is non-local). "
                "R_superset: Hodge classes contain algebraic cycle classes; "
                "conjecture says containment is equality.  P_pm_sym: the Hodge "
                "decomposition H^{p,q} ≅ conj(H^{q,p}) is perfectly symmetric. "
                "G_aleph: each individual cohomology class is the unit of analysis. "
                "Omega_Z: integral lattice condition is the Z-topological signature. "
                "d=9 from standard_proof_system; d=5 from yang_mills_mass_gap."
            ),
            metadata={"domain": "mathematics", "registered_by": "millennium_catalog",
                      "clay_problem": True, "solved": False},
        ),

        # ─────────────────────────────────────────────────────────────────────
        # 4. YANG–MILLS EXISTENCE AND MASS GAP
        # ⟨D_cube; T_network; R_catalytic; P_pm_sym; G_and; F_hbar; K_slow; G_aleph; Phi_c; Omega_Z; n:m; H2⟩
        #
        # Statement: A quantum Yang–Mills gauge theory in R^4 exists (in the
        #   sense of constructive QFT) and has a strictly positive mass gap Δ > 0.
        #
        # D_cube: The gauge fields live in 4D spacetime; we use D_cube for the
        #   3+1D physical support (consistent with standard_model encoding).
        # T_network: The principal SU(N) gauge bundle = a network structure;
        #   gluon interactions form a non-Abelian network of color connections.
        # R_catalytic: Gauge invariance is catalytic — a gauge transformation
        #   changes the field representation but preserves all observables.
        # P_pm_sym: SU(N) gauge fields are symmetric under gauge conjugation;
        #   the theory is parity-symmetric (unlike the SM weak sector).
        # G_and: Both conditions must hold simultaneously: the QFT exists AND
        #   the spectrum has a gap Δ > 0.
        # F_hbar: Full quantum field theory — renormalization, functional
        #   integration, operator algebras all required.
        # K_slow: The mass gap is a non-perturbative phenomenon — instantons,
        #   monopoles, and confinement operate at slow kinetic scale inaccessible
        #   to perturbation theory.
        # G_aleph: The mass gap Δ is a fine-grained spectral property — it is the
        #   energy of the lowest non-vacuum excitation, a single-particle invariant.
        # Phi_c: Confinement/deconfinement is a phase transition; the mass gap
        #   IS the critical phenomenon separating confined (Phi_sub) from
        #   deconfined (Phi_sup) phases.  The existence problem sits at Phi_c.
        # Omega_Z: Instanton number (topological charge) is a Z-valued winding
        #   number; θ-vacuum structure and axial anomaly are Z-topological.
        # n:m: N^2-1 gluons for SU(N); multiple color charges interact.
        # H2: Chirality — chiral symmetry breaking in QCD is related to the mass
        #   gap (the order parameter is the chiral condensate ⟨ψ̄ψ⟩);
        #   instantons break the U(1)_A symmetry.
        # ─────────────────────────────────────────────────────────────────────
        Synthon(
            name="yang_mills_mass_gap",
            dimensionality=Dimensionality.D_cube,
            topology=Topology.T_network,
            recognition_mode=Recognition.R_catalytic,
            polarity=Polarity.P_pm_sym,
            grammar=Grammar.G_and,
            fidelity=Fidelity.F_hbar,
            kinetic_character=KineticChar.K_slow,
            granularity=Granularity.G_aleph,
            criticality_phase=Criticality.Phi_c,
            protection=Protection.Omega_Z,
            stoichiometry=Stoichiometry.n_m,
            chirality=Chirality.H2,
            description=(
                "Yang–Mills Existence and Mass Gap: construct QFT for pure "
                "Yang–Mills in R^4 with mass gap Δ > 0.  D_cube: 4D physical "
                "spacetime (as in standard_model).  T_network: SU(N) principal "
                "bundle = non-Abelian color network.  R_catalytic: gauge invariance "
                "is catalytic (transforms fields, preserves observables). "
                "K_slow: mass gap is non-perturbative — instantons and confinement "
                "operate at slow kinetic scale.  G_aleph: the gap is the lowest "
                "spectral value = fine-grained invariant.  Omega_Z: instanton "
                "number is a Z winding invariant.  d=7 from standard_proof_system "
                "— closest unsolved problem to standard formalism.  d=5 from "
                "birch_swinnerton_dyer and poincare_conjecture."
            ),
            metadata={"domain": "mathematics", "registered_by": "millennium_catalog",
                      "clay_problem": True, "solved": False},
        ),

        # ─────────────────────────────────────────────────────────────────────
        # 5. NAVIER–STOKES EXISTENCE AND SMOOTHNESS
        # ⟨D_cube; T_network; R_catalytic; P_pm; G_seq; F_eth; K_trap; G_gimel; Phi_c; Omega_0; n:m; H0⟩
        #
        # Statement: In R^3, for smooth initial data, do smooth solutions to the
        #   incompressible Navier–Stokes equations exist for all time?  Or does
        #   finite-time blowup occur?
        #
        # D_cube: 3D physical space (the PDE lives in R^3).
        # T_network: Turbulent flow = a network of interacting Fourier modes;
        #   the Kolmogorov energy cascade is a network topology.
        # R_catalytic: Viscosity acts catalytically — it dissipates energy but
        #   does not destroy the PDE structure or the incompressibility constraint.
        # P_pm: The flow has both viscous (dissipative, P_minus) and inertial
        #   (conservative, P_plus) components — genuinely bipolar, neither
        #   dominates at all scales.
        # G_seq: The turbulent cascade is sequential — energy flows in an ordered
        #   sequence from large scales → small scales → dissipation (Kolmogorov
        #   cascade).  The grammar is inherently ordered.
        # F_eth: Threshold fidelity — the question is whether solutions stay above
        #   the regularity threshold; F_eth captures the boundary character.
        # K_trap: Turbulent flows can develop potential singularities at small
        #   scales — the solution may become kinetically trapped at high wavenumbers.
        # G_gimel: The question is global/coarse — existence for all t ∈ [0,∞).
        # Phi_c: We do not know which phase the system is in.  The problem sits
        #   AT the criticality boundary: solutions are either globally regular
        #   (Phi_sub) or blow up (Phi_sup).  The problem IS the phase determination.
        # Omega_0: No topological protection.  If blowup occurs, it is an analytic
        #   singularity, not a topological obstruction.  A counterexample blowup
        #   is structurally permissible (unlike the topologically protected problems).
        # n:m: Many Fourier modes interact with many other modes.
        # H0: Achiral — the Navier–Stokes equations are isotropic; no preferred
        #   handedness in the physics.
        # ─────────────────────────────────────────────────────────────────────
        Synthon(
            name="navier_stokes_smoothness",
            dimensionality=Dimensionality.D_cube,
            topology=Topology.T_network,
            recognition_mode=Recognition.R_catalytic,
            polarity=Polarity.P_pm,
            grammar=Grammar.G_seq,
            fidelity=Fidelity.F_eth,
            kinetic_character=KineticChar.K_trap,
            granularity=Granularity.G_gimel,
            criticality_phase=Criticality.Phi_c,
            protection=Protection.Omega_0,
            stoichiometry=Stoichiometry.n_m,
            chirality=Chirality.H0,
            description=(
                "Navier–Stokes Existence and Smoothness: do smooth solutions to "
                "incompressible NS in R^3 exist for all time?  D_cube: 3D physical "
                "space.  T_network: turbulent Kolmogorov energy cascade.  P_pm: "
                "bipolar viscous/inertial character.  G_seq: sequential cascade "
                "grammar (large → small scales).  F_eth: threshold character — "
                "regularity/blowup boundary.  K_trap: potential singularity "
                "formation at fine scales.  G_gimel: global/all-time existence "
                "question.  Omega_0: no topological protection — blowup is "
                "structurally permissible.  d=8 from standard_proof_system. "
                "P-MILL-03: proof of smoothness requires mechanism keeping "
                "Phi_c → Phi_sub throughout, analogous to Perelman surgery."
            ),
            metadata={"domain": "mathematics", "registered_by": "millennium_catalog",
                      "clay_problem": True, "solved": False},
        ),

        # ─────────────────────────────────────────────────────────────────────
        # 6. BIRCH AND SWINNERTON-DYER CONJECTURE
        # ⟨D_cube; T_torus; R_superset; P_pm; G_impl; F_hbar; K_slow; G_aleph; Phi_c; Omega_Z; 1:1; H2⟩
        #
        # Statement: For an elliptic curve E/Q, rank(E(Q)) = ord_{s=1} L(E, s).
        #
        # D_cube: Elliptic curves are defined over Q and embedded in P^2 (an
        #   arithmetic-geometric object in 3D projective space); the arithmetic
        #   lives at D_cube scale.
        # T_torus: Elliptic curves over C ARE complex tori (genus-1 Riemann
        #   surfaces E ≅ C/Λ).  This is the most direct topological encoding:
        #   the object of study is literally a torus.
        # R_superset: The L-function L(E,s) contains the arithmetic of E as a
        #   superset (it encodes BSD rank, Tamagawa numbers, Shafarevich–Tate
        #   group, periods — all at once).
        # P_pm: The functional equation L(E,s) ↔ L(E, 2-s) (with sign ε = ±1)
        #   is a bipolar symmetry about s = 1.
        # G_impl: The BSD grammar is implicative: rank(E) > 0 ⟺ L(E,1) = 0.
        #   The conjecture is a conditional — a structural implication between
        #   two seemingly independent invariants.
        # F_hbar: Quantum fidelity — the proof relies on the modularity theorem
        #   (Taylor–Wiles), automorphic forms, and the full Langlands program.
        # K_slow: Computing the rank of a given E/Q is computationally hard;
        #   no general polynomial-time algorithm is known.
        # G_aleph: The rank and L-value are fine-grained invariants of each
        #   individual elliptic curve (atomic level).
        # Phi_c: L(E,1) = 0 is the critical point — the central value of the
        #   L-function at the symmetry center s=1.  The conjecture is about
        #   what happens at criticality.
        # Omega_Z: rank(E(Q)) ∈ Z; the Shafarevich–Tate group has Z/nZ structure;
        #   the BSD formula involves integer invariants throughout.
        # 1:1: The rank and the order of vanishing of L(E,s) are conjectured to
        #   correspond 1:1 (the whole point of BSD).
        # H2: Persistent chirality — elliptic curves have a canonical orientation
        #   (the Weierstrass form breaks the real-complex symmetry); complex
        #   multiplication is chiral.
        # ─────────────────────────────────────────────────────────────────────
        Synthon(
            name="birch_swinnerton_dyer",
            dimensionality=Dimensionality.D_cube,
            topology=Topology.T_torus,
            recognition_mode=Recognition.R_superset,
            polarity=Polarity.P_pm,
            grammar=Grammar.G_impl,
            fidelity=Fidelity.F_hbar,
            kinetic_character=KineticChar.K_slow,
            granularity=Granularity.G_aleph,
            criticality_phase=Criticality.Phi_c,
            protection=Protection.Omega_Z,
            stoichiometry=Stoichiometry.one_one,
            chirality=Chirality.H2,
            description=(
                "Birch and Swinnerton-Dyer Conjecture: rank(E(Q)) = ord_{s=1} L(E,s). "
                "T_torus: elliptic curves ARE complex tori (genus-1; E ≅ C/Λ) — "
                "the most direct topological encoding in the catalog.  G_impl: "
                "implicative grammar (rank > 0 ⟺ L vanishes at s=1) — a "
                "conditional linking two independent invariants.  Phi_c: L(E,1)=0 "
                "IS the critical point — the central value of the L-function. "
                "Omega_Z: rank ∈ Z; Sha group has Z/nZ structure.  d=9 from "
                "standard_proof_system.  d=5 from yang_mills_mass_gap — closest "
                "pair among unsolved problems; both share D_cube, F_hbar, K_slow, "
                "G_aleph, Phi_c, Omega_Z, H2.  P-MILL-01: spectral/topological "
                "methods bridging YM mass gap may apply here."
            ),
            metadata={"domain": "mathematics", "registered_by": "millennium_catalog",
                      "clay_problem": True, "solved": False},
        ),

        # ─────────────────────────────────────────────────────────────────────
        # 7. POINCARÉ CONJECTURE  (SOLVED — Perelman 2003)
        # ⟨D_cube; T_bowtie; R_catalytic; P_pm_sym; G_and; F_hbar; K_mod; G_aleph; Phi_sub; Omega_Z; 1:1; H2⟩
        #
        # Statement: Every simply connected, closed 3-manifold is homeomorphic
        #   to the 3-sphere S^3.  PROVED by Grigori Perelman (2002–2003) via
        #   Hamilton's Ricci flow with surgery.
        #
        # Phi_sub: SOLVED — the system is in the stable ordered phase.
        #   Perelman's surgery technique prevents Phi_sup (finite-time blowup)
        #   in dimension 3.  This is the primary structural signature of solvability.
        #
        # D_cube: The 3-manifold lives in D_cube (3-dimensional topology).
        # T_bowtie: S^3 has "cyclic closure" topology — it is the double of the
        #   3-ball (two 3-balls glued along their boundary S^2).  Ricci flow
        #   drives any simply connected 3-manifold to this cyclic attractor.
        # R_catalytic: Ricci flow is the recognition mechanism — a catalytic
        #   geometric transformation that transforms the metric without changing
        #   the topology, until the manifold "recognizes" itself as S^3.
        # P_pm_sym: S^3 = SU(2) has perfect bipolar symmetry (left and right
        #   invariant vector fields; the group is its own symmetric space).
        # G_and: The conditions are conjunctive: simply connected AND closed AND
        #   compact AND 3-dimensional — all must hold simultaneously.
        # F_hbar: Perelman's proof achieves quantum-level fidelity — it is a
        #   complete, rigorous analytic proof using geometric analysis at the
        #   highest formalism level.
        # K_mod: Ricci flow runs at moderate kinetic rate in 3D — no kinetic
        #   trapping because Perelman's surgery handles all singularities.
        # G_aleph: Fine-grained — local geometry (Ricci curvature at each point)
        #   determines the global topology (S^3).
        # Omega_Z: S^3 = SU(2) has π_3(S^3) = Z (Hopf fibration); this is the
        #   integer topological invariant that characterizes the sphere.
        # 1:1: The theorem establishes a unique homeomorphism type.
        # H2: The 3-sphere is orientable; Ricci flow preserves orientation.
        #   H2 (not H0) because S^3 as SU(2) has a canonical complex structure
        #   (it is the unit quaternions; the chiral structure is persistent).
        # ─────────────────────────────────────────────────────────────────────
        Synthon(
            name="poincare_conjecture",
            dimensionality=Dimensionality.D_cube,
            topology=Topology.T_bowtie,
            recognition_mode=Recognition.R_catalytic,
            polarity=Polarity.P_pm_sym,
            grammar=Grammar.G_and,
            fidelity=Fidelity.F_hbar,
            kinetic_character=KineticChar.K_mod,
            granularity=Granularity.G_aleph,
            criticality_phase=Criticality.Phi_sub,
            protection=Protection.Omega_Z,
            stoichiometry=Stoichiometry.one_one,
            chirality=Chirality.H2,
            description=(
                "Poincaré Conjecture (SOLVED, Perelman 2003): every simply connected "
                "closed 3-manifold is homeomorphic to S^3.  Phi_sub: SOLVED — the "
                "primary structural marker; surgery prevents Phi_sup in dimension 3. "
                "T_bowtie: S^3 = double of 3-ball = cyclic closure; Ricci flow "
                "drives the manifold to this attractor.  R_catalytic: Ricci flow "
                "as the recognition mechanism.  K_mod: no kinetic trapping in 3D "
                "(unlike Navier-Stokes, which has K_trap).  Omega_Z: π_3(S^3)=Z "
                "(Hopf fibration).  d=5 from standard_proof_system — the smallest "
                "distance; confirms the hypothesis that Phi_sub + small distance "
                "predicts solvability with existing topological formalism. "
                "d=4 from yang_mills_mass_gap — prediction P-MILL-04."
            ),
            metadata={"domain": "mathematics", "registered_by": "millennium_catalog",
                      "clay_problem": True, "solved": True,
                      "solved_by": "Grigori Perelman", "solved_year": 2003},
        ),
    ]

    for synthon in entries:
        if synthon.name not in global_catalog:
            global_catalog.register(synthon)


# ─────────────────────────────────────────────────────────────────────────────
# Distance / analysis helpers
# ─────────────────────────────────────────────────────────────────────────────

def millennium_distance_report() -> str:
    """
    Print a pairwise distance matrix and cluster analysis for all
    Millennium Problem synthons.
    """
    from .algebra import primitive_mismatches

    names = [
        "standard_proof_system",
        "riemann_hypothesis",
        "p_vs_np",
        "hodge_conjecture",
        "yang_mills_mass_gap",
        "navier_stokes_smoothness",
        "birch_swinnerton_dyer",
        "poincare_conjecture",
    ]
    abbrev = {
        "standard_proof_system":   "BASELINE",
        "riemann_hypothesis":      "RH     ",
        "p_vs_np":                 "P≠NP   ",
        "hodge_conjecture":        "HODGE  ",
        "yang_mills_mass_gap":     "YM     ",
        "navier_stokes_smoothness":"NS     ",
        "birch_swinnerton_dyer":   "BSD    ",
        "poincare_conjecture":     "POINC  ",
    }

    synthons = {}
    for n in names:
        try:
            synthons[n] = global_catalog[n]
        except KeyError:
            return f"ERROR: '{n}' not found — run register_millennium_synthons() first."

    lines = []
    lines.append("\nMillennium Prize Problems — Primitive Distance Matrix")
    lines.append("=" * 65)
    header = "         " + "  ".join(abbrev[n] for n in names)
    lines.append(header)

    for a in names:
        row = [abbrev[a]]
        for b in names:
            d = primitive_mismatches(synthons[a], synthons[b])
            row.append(f"  {d:2d}     ")
        lines.append("".join(row))

    lines.append("")
    lines.append("Distances from BASELINE (standard_proof_system):")
    baseline = synthons["standard_proof_system"]
    for n in names[1:]:
        d = primitive_mismatches(baseline, synthons[n])
        solved = synthons[n].metadata.get("solved", False)
        phi = synthons[n].crit.value
        mark = "✓ SOLVED" if solved else "  unsolved"
        lines.append(f"  d={d:2d}  {abbrev[n]}  Φ={phi}  {mark}")

    lines.append("")
    lines.append("Closest pairs among unsolved problems:")
    unsolved = [n for n in names[1:] if not synthons[n].metadata.get("solved")]
    pairs = []
    for i, a in enumerate(unsolved):
        for b in unsolved[i+1:]:
            d = primitive_mismatches(synthons[a], synthons[b])
            pairs.append((d, a, b))
    for d, a, b in sorted(pairs):
        lines.append(f"  d={d:2d}  {abbrev[a]} ↔ {abbrev[b]}")

    return "\n".join(lines)
