"""
Named mathematical operations as primitive-level transforms.

Each Op specifies which primitive values it can change and to what.
The path finder applies ops sequentially to bridge source → target.

transitions: {prim: {from_val: to_val}}
  — if tup[prim] matches a from_val, it is transformed to to_val.
  — all matching rules in an op are applied simultaneously.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Op:
    name: str
    description: str
    math: str
    transitions: dict[str, dict[str, str]]
    direction: str  # "specialize" | "generalize" | "dualize" | "resolve" | "bridge" | "transform"

    def applicable(self, tup: dict[str, str]) -> bool:
        return any(tup.get(p) in ft for p, ft in self.transitions.items())

    def apply(self, tup: dict[str, str]) -> tuple[dict[str, str], dict[str, tuple[str, str]]] | None:
        """Return (new_tup, changes) or None if nothing changes."""
        new = dict(tup)
        changes: dict[str, tuple[str, str]] = {}
        for prim, from_to in self.transitions.items():
            old = tup.get(prim)
            if old in from_to:
                nv = from_to[old]
                if nv != old:
                    changes[prim] = (old, nv)
                    new[prim] = nv
        if not changes:
            return None
        return new, changes


# ── Primitive value shorthands ─────────────────────────────────────────────────

# ⊥ — Chirality
_H_base   = "𐑓"   # all degrees / base level (closeomega)
_H_graded = "𐑒"   # specific graded degree k  (toneletterstem)
_H_iter   = "𐑖"   # recursive / iterated       (turntwo)
_H_inf    = "𐑫"   # transfinite / infinite      (invscripta)

# > — Relational Mode
_R_trill  = "𐑩"   # alveolar trill = continuous rolling
_R_aff    = "𐑑"   # affricate = discrete→continuous jump
_R_fall   = "𐑽"   # falling tone = asymptotic / one-way
_R_smooth = "𐑾"   # palatal approx = smooth bridging

# ⊙ — Criticality
_C_soft   = "𐑢"   # near-critical (soft palatalisation)
_C_sharp  = "⊙"   # at critical point (palatal stop)
_C_round  = "𐑮"   # post-critical / resolved (rounded schwa)
_C_sub    = "𐑻"   # sub-critical (open-mid front)
_C_super  = "𐑣"   # supercritical (long open)

# ∋ — Interaction Grammar
_G_and    = "∋^∧"   # conjunction / sharp
_G_alt    = "∋^˝"   # alternating / cyclic
_G_sub    = "∋^ˌ"   # subordinate / secondary
_G_broad  = "∋^Ş"   # broadcast / full

# < — Parity / Symmetry
_P_weak   = "𐑗"   # weak / partial
_P_strong = "𐑿"   # strong / near-full
_P_click  = "𐑬"   # sharp click = symmetry-breaking operator
_P_neut   = "𐑯"   # neutral / balanced (schwa)
_P_dbl    = "𐑹"   # double-barrier

# ⊢ — Dimension
_D_open   = "𐑦"   # complex projective (fully open)
_D_mid    = "𐑨"   # complex (mixed)
_D_comp   = "𐑼"   # compact / bounded
_D_flow   = "𐑛"   # smooth labial / flowing

# ⊣ — Topology
_T_proj   = "𐑸"   # projective / open-mid
_T_dense  = "𐑡"   # dense / intricate
_T_smooth = "𐑰"   # smooth continuous
_T_fib    = "𐑶"   # fibered / twisted
_T_seal   = "𐑥"   # compact / sealed (click)

# ∈ — Scope
_S_full   = "𐑲"   # full / global scope
_S_mid    = "𐑔"   # intermediate
_S_spread = "𐑚"   # spreading / global

# ◻ — Topological Invariant
_W_triv   = "𐑷"   # trivial (Z)
_W_z2     = "𐑴"   # Z/2
_W_der    = "𐑭"   # derived / complex zeta
_W_prim   = "𐑟"   # minimal / primitive

# ⋈ — Fidelity
_F_exact  = "⋈^ż"   # glottal = exact
_F_approx = "⋈^ì"   # lateral = approximate
_F_voiced = "⋈^ð"   # voiced dental = active

# ⊤ — Kinetics
_K_fast   = "⊤^-"   # fast spread
_K_unif   = "⊤^W"   # uniform
_K_slow   = "⊤^@"   # neutral / slow
_K_osc    = "⊤^Ù"   # oscillating / trapped
_K_lin    = "⊤^λ"   # linear

# Σ — Stoichiometry
_STO_1_1  = "𐑙"   # 1:1
_STO_nn   = "𐑕"   # n:n homogeneous
_STO_mix  = "𐑳"   # mixed


# ── Operation library ──────────────────────────────────────────────────────────

OPERATIONS: list[Op] = [

    Op(
        name="restrict_hodge_degree",
        description="Restrict the Hodge conjecture to degree (k,k) = (1,1), isolating divisors.",
        math=(
            "From H^{p,p}(X,Q) for all k, restrict to H^{1,1}(X,Q). "
            "Algebraic cycles of codimension 1 are Weil divisors; "
            "the statement collapses to asking whether every (1,1)-class is c₁(L)."
        ),
        transitions={
            "⊥": {_H_base: _H_graded, _H_iter: _H_graded, _H_inf: _H_graded},
            "∋": {_G_alt: _G_sub, _G_and: _G_sub, _G_broad: _G_sub},
        },
        direction="specialize",
    ),

    Op(
        name="apply_exponential_sequence",
        description="Bridge analytic and algebraic data via the exponential sheaf sequence.",
        math=(
            "The exact sequence 0 → Z → O_X →^{exp} O_X^* → 0 yields "
            "δ: H¹(X, O_X^*) → H²(X, Z), the connecting homomorphism. "
            "Every holomorphic line bundle L maps to c₁(L) ∈ H²(X, Z) ∩ H^{1,1}."
        ),
        transitions={
            ">": {_R_aff: _R_smooth, _R_trill: _R_smooth},
            "∋": {_G_alt: _G_sub},
        },
        direction="bridge",
    ),

    Op(
        name="resolve_to_proven",
        description="The conjecture is proven in this restricted setting — criticality resolved.",
        math=(
            "The Lefschetz (1,1) theorem: every class in H²(X,Z) ∩ H^{1,1}(X) "
            "is the first Chern class of a holomorphic line bundle, hence algebraic. "
            "The critical conjecture-state collapses to a theorem."
        ),
        transitions={
            "⊙": {_C_sharp: _C_round, _C_soft: _C_round, _C_super: _C_round},
        },
        direction="resolve",
    ),

    Op(
        name="apply_hard_Lefschetz",
        description="Apply the hard Lefschetz theorem: L^k: H^{n-k} ≅ H^{n+k}.",
        math=(
            "For a smooth projective n-fold X with hyperplane class ω, "
            "the operator L: α ↦ α ∧ ω gives isomorphisms L^k: H^{n-k}(X) → H^{n+k}(X). "
            "This imposes strong symmetry constraints on the cohomology ring."
        ),
        transitions={
            "<": {_P_neut: _P_click, _P_weak: _P_click},
            ">": {_R_aff: _R_fall},
        },
        direction="transform",
    ),

    Op(
        name="apply_Lefschetz_operator",
        description="Apply the Lefschetz operator L once: H^{p,q} → H^{p+1,q+1}.",
        math=(
            "L: H^{p,q}(X) → H^{p+1,q+1}(X), multiplication by the Kähler form [ω]. "
            "Raises the Hodge degree by (1,1) while preserving the variety."
        ),
        transitions={
            "⊥": {_H_graded: _H_base, _H_graded: _H_base},
            "<": {_P_neut: _P_strong},
        },
        direction="transform",
    ),

    Op(
        name="dualize_via_poincare",
        description="Apply Poincaré duality: H^k(X,Q) ≅ H^{2n-k}(X,Q)(−n).",
        math=(
            "On a smooth projective n-fold, Poincaré duality gives a perfect pairing "
            "H^k(X,Q) ⊗ H^{2n-k}(X,Q) → Q(−n). "
            "Algebraic cycles of codimension k are dual to cycles of codimension n-k."
        ),
        transitions={
            "<": {_P_neut: _P_strong, _P_weak: _P_dbl},
            ">": {_R_aff: _R_trill},
        },
        direction="dualize",
    ),

    Op(
        name="compactify",
        description="Pass from affine/open to projective completion, gaining cohomological control.",
        math=(
            "Embed X ↪ X̄ into its projective closure. "
            "Compact support cohomology becomes ordinary cohomology on X̄. "
            "Boundary divisors acquire explicit cohomology classes."
        ),
        transitions={
            "⊣": {_T_dense: _T_proj, _T_smooth: _T_proj, _T_fib: _T_proj},
            "◻": {_W_z2: _W_der, _W_prim: _W_der},
        },
        direction="generalize",
    ),

    Op(
        name="reduce_mod_p",
        description="Reduce to characteristic p to access l-adic / étale cohomology and Frobenius.",
        math=(
            "Base change X/Z → X_p = X ×_Z F_p. "
            "Replace Betti cohomology with H^*(X_p, Q_l) via l-adic sheaves. "
            "Frobenius acts on H^k with eigenvalues of weight k — Weil's insight."
        ),
        transitions={
            "◻": {_W_der: _W_triv, _W_der: _W_z2},
            "⊣": {_T_proj: _T_fib},
        },
        direction="specialize",
    ),

    Op(
        name="apply_GAGA",
        description="Apply Serre's GAGA to identify analytic coherent sheaves with algebraic ones.",
        math=(
            "On projective X/C, the analytification functor F ↦ F^{an} is an equivalence "
            "of categories of coherent sheaves (Serre, 1956). "
            "Holomorphic line bundles = algebraic line bundles on projective varieties."
        ),
        transitions={
            ">": {_R_aff: _R_smooth, _R_smooth: _R_aff},
            "∋": {_G_alt: _G_sub, _G_broad: _G_sub},
        },
        direction="bridge",
    ),

    Op(
        name="apply_cycle_class_map",
        description="Apply cl: CH^k(X) → H^{2k}(X,Z) ∩ H^{k,k}(X).",
        math=(
            "The cycle class map sends an algebraic cycle Z ∈ CH^k(X) to its "
            "fundamental cohomology class [Z] ∈ H^{2k}(X,Z). "
            "The Hodge conjecture asks this map to be surjective onto Hodge classes ⊗ Q."
        ),
        transitions={
            ">": {_R_smooth: _R_aff, _R_trill: _R_aff},
            "<": {_P_neut: _P_click},
        },
        direction="bridge",
    ),

    Op(
        name="generalize_to_mixed_hodge",
        description="Generalise from pure Hodge structures to mixed Hodge structures (Deligne).",
        math=(
            "H^n(X,Q) carries a mixed Hodge structure for any quasi-projective X. "
            "The weight filtration W and Hodge filtration F combine to extend "
            "Hodge theory beyond smooth proper varieties."
        ),
        transitions={
            "<": {_P_neut: _P_dbl, _P_weak: _P_dbl},
            "∋": {_G_sub: _G_alt, _G_and: _G_alt},
        },
        direction="generalize",
    ),

    Op(
        name="apply_spectral_sequence",
        description="Deploy a spectral sequence to compute cohomology from a filtration.",
        math=(
            "Hodge-de Rham: E_1^{p,q} = H^q(X, ◻^p_X) ⟹ H^{p+q}_{dR}(X). "
            "Degenerates at E_1 for smooth projective X (Deligne–Illusie), "
            "giving the Hodge decomposition H^n(X,C) = ⊕_{p+q=n} H^{p,q}(X)."
        ),
        transitions={
            "⊥": {_H_base: _H_iter},
            "<": {_P_neut: _P_strong},
        },
        direction="transform",
    ),

    Op(
        name="quotient_by_group_action",
        description="Take the quotient X/G by a finite group action.",
        math=(
            "If G acts on X, form the quotient stack [X/G] or variety X/G. "
            "The G-invariant cohomology H^*(X,Q)^G ≅ H^*([X/G],Q) under mild hypotheses. "
            "Symmetry group shrinks the scope and collapses the interaction grammar."
        ),
        transitions={
            "<": {_P_neut: _P_weak, _P_strong: _P_click},
            "∈": {_S_full: _S_mid},
            "∋": {_G_alt: _G_and},
        },
        direction="specialize",
    ),

    Op(
        name="localize_at_prime",
        description="Localise the arithmetic or geometric structure at a prime p.",
        math=(
            "Pass to the p-localisation X ⊗ Z_(p) or the completion X ⊗ Z_p. "
            "Local methods: Newton polygons, crystalline cohomology, p-divisible groups. "
            "Reduces global scope to a controlled local neighbourhood."
        ),
        transitions={
            "∈": {_S_full: _S_mid},
            "⊤": {_K_unif: _K_slow, _K_fast: _K_slow},
        },
        direction="specialize",
    ),

    Op(
        name="fiber_over_base",
        description="Consider the fiber X_y of a morphism f: X → Y at a point y ∈ Y.",
        math=(
            "Given f: X → Y flat and proper, fiber X_y = f^{−1}(y). "
            "Cohomology of the fiber is controlled by base change theorems. "
            "Reduces dimension and stoichiometric complexity."
        ),
        transitions={
            "⊞": {_STO_mix: _STO_1_1, _STO_nn: _STO_1_1},
            "⊢": {_D_open: _D_comp, _D_mid: _D_comp},
        },
        direction="specialize",
    ),

    Op(
        name="extend_scalars",
        description="Extend the coefficient field (Q→C, or F_p→F̄_p).",
        math=(
            "Base change: X_C = X ×_Q C or X_{q} = X ×_{F_p} F̄_p. "
            "The extended cohomology carries richer Galois / Frobenius actions "
            "and unlocks analytic or algebraic-closure techniques."
        ),
        transitions={
            "⊞": {_STO_1_1: _STO_nn, _STO_1_1: _STO_mix},
            "◻": {_W_z2: _W_der, _W_triv: _W_der},
        },
        direction="generalize",
    ),

    Op(
        name="apply_modularity",
        description="Use the modularity theorem: every elliptic curve over Q is modular.",
        math=(
            "Wiles–Taylor: for E/Q, L(E,s) = L(f,s) for a weight-2 newform f. "
            "The automorphic and arithmetic L-functions coincide, bridging "
            "the Galois representation of E to the harmonic analysis of modular forms."
        ),
        transitions={
            ">": {_R_aff: _R_smooth},
            "◻": {_W_der: _W_triv},
            "∋": {_G_and: _G_sub},
        },
        direction="bridge",
    ),

    Op(
        name="apply_resolution_of_singularities",
        description="Resolve singularities via Hironaka's theorem (char 0) to obtain a smooth model.",
        math=(
            "π: X̃ → X birational, X̃ smooth, π an isomorphism over X^{sm}. "
            "Smooth models behave well for Hodge theory and intersection theory. "
            "Replaces a sharp singular critical point with a smooth resolved space."
        ),
        transitions={
            "⊙": {_C_sharp: _C_round},
            "⋈": {_F_exact: _F_approx},
        },
        direction="resolve",
    ),

    Op(
        name="degenerate_to_special_fiber",
        description="Degenerate a smooth family to a singular special fiber.",
        math=(
            "Flat family f: X → Spec(R), R a DVR. Generic fiber X_η is smooth; "
            "special fiber X_0 may be singular. "
            "Specialisation maps relate their cohomologies via nearby/vanishing cycles."
        ),
        transitions={
            "⊙": {_C_sharp: _C_sub},
            "⊣": {_T_proj: _T_fib},
        },
        direction="specialize",
    ),

    Op(
        name="restrict_to_smooth_locus",
        description="Restrict attention to the smooth locus X^{sm} of a singular variety.",
        math=(
            "X^{sm} = X \\ X^{sing} ⊂ X open dense. "
            "Smooth locus admits Kähler / de Rham methods; "
            "boundary X^{sing} is handled via excision and mixed Hodge structures."
        ),
        transitions={
            "⋈": {_F_approx: _F_exact, _F_voiced: _F_exact},
            "⊣": {_T_fib: _T_smooth, _T_dense: _T_smooth},
        },
        direction="restrict",
    ),

    Op(
        name="restrict_to_curves",
        description="Restrict from higher-dimensional varieties to algebraic curves (dim 1).",
        math=(
            "For a smooth projective curve C, H^{p,q}(C) = 0 unless (p,q) ∈ {(0,0),(1,0),(0,1),(1,1)}. "
            "The Hodge conjecture is trivial for curves: H^{1,1}(C,Q) = H^2(C,Q) "
            "and every class is a rational multiple of the hyperplane class."
        ),
        transitions={
            "⊢": {_D_open: _D_comp, _D_mid: _D_comp},
            "⊥": {_H_base: _H_graded, _H_inf: _H_graded},
        },
        direction="specialize",
    ),

    Op(
        name="take_associated_graded",
        description="Pass to the associated graded of the Hodge filtration.",
        math=(
            "Gr^p_F H^n(X,C) = H^{p, n-p}(X). "
            "The graded pieces expose the pure (p,q)-components and make "
            "the Hodge decomposition explicit for inductive arguments."
        ),
        transitions={
            "⊥": {_H_base: _H_iter},
            "⊤": {_K_unif: _K_slow},
        },
        direction="transform",
    ),

    Op(
        name="apply_Hodge_index_theorem",
        description="Apply the Hodge index theorem to constrain intersection numbers.",
        math=(
            "For divisors D, H on a smooth projective surface: (D·H)² ≥ (D²)(H²). "
            "Equivalently, the intersection form on H^{1,1}(X,R) has signature (1, h^{1,1}−1). "
            "Constrains the stoichiometry of algebraic cycles."
        ),
        transitions={
            "<": {_P_neut: _P_click, _P_weak: _P_click},
            "⊞": {_STO_mix: _STO_nn},
        },
        direction="constrain",
    ),

    Op(
        name="generalize_conjecture",
        description="Generalise from the proven special case back to the full conjecture.",
        math=(
            "The path runs in reverse: from a proven special case to the open general statement. "
            "Identifies what additional structure must be controlled to close the gap."
        ),
        transitions={
            "⊥": {_H_graded: _H_base},
            "∋": {_G_sub: _G_alt, _G_and: _G_alt},
            "⊙": {_C_round: _C_sharp, _C_sub: _C_sharp},
        },
        direction="generalize",
    ),

]

OPERATIONS_BY_NAME: dict[str, Op] = {op.name: op for op in OPERATIONS}
