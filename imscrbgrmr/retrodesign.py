"""
IG_RETRODESIGN — Constraint-Directed Retrosynthetic Decomposition

The inverse of IG_HOTSWAP. Given a target constraint architecture
Ψ_target, decomposes it into a minimal set of constituent imscriptions whose
composition axioms are mutually satisfiable.

Decomposition is pruned by Axiom Violation rather than chemical intuition:
  Axiom 1  — Fidelity Floor (T_⋈ + P_± + F_ℓ → PRUNE)
  Axiom 2  — Propagation Barrier (G_ב + Γ_∧(SPECIFIC) → cannot propagate to G_ℵ)
  Axiom 4  — Grammar Mismatch (Γ_→ without D_∞ or R_‡ → PRUNE)
  Axiom 6  — Grounding Fail (D_∞ without reset text → FLAG)

See IG_RETRODESIGN.md for protocol specification.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

from .models import (
    Imscription, Dimensionality, Topology,
    RecognitionMode, Polarity, Fidelity, KineticCharacter,
    Granularity, InteractionGrammar, GrammarOperator, CriticalityPhase,
    Grammar, KineticChar, Criticality, Protection, Stoichiometry, Chirality, Recognition,
)
from .constraints import (
    ConstraintEngine, AxiomValidator, CompatibilityResult, AxiomResult,
)


# ---------------------------------------------------------------------------
# Notation string parser
# ---------------------------------------------------------------------------

_DIM_DOMAINS: Dict[str, frozenset] = {
    "Ð_point": frozenset({"point"}),
    "Ð_line":  frozenset({"line"}),
    "Ð_wynn": frozenset({"molecular"}),
    "Ð_cube":  frozenset({"supramolecular"}),
    "Ð_invomega": frozenset({"temporal"}),
    "Ð_omega":  frozenset({"holographic", "imscriptive"}),
}


def _domains(dim: Dimensionality) -> frozenset:
    """Return the domain tag set for a Dimensionality enum value."""
    return _DIM_DOMAINS.get(dim.value, frozenset({"molecular"}))


def _parse_notation_to_imscription(notation_str: str, name: str = "target") -> Imscription:
    """
    Parse a ⟨D=...; T=...; ...⟩ notation string into a Imscription.
    Accepts both 'KEY=VALUE' and positional (value-only) formats.
    """
    s = notation_str.strip().lstrip("⟨<").rstrip("⟩>").strip()
    parts = [p.strip() for p in s.split(";") if p.strip()]

    # Build a dict keyed by short primitive name
    d: Dict[str, str] = {"name": name}
    key_order = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]

    for i, part in enumerate(parts):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k.strip()] = v.strip()
        else:
            # Positional: map by index to key_order
            if i < len(key_order):
                d[key_order[i]] = part.strip()

    return Imscription.from_dict(d)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_PRUNE_AXIOMS = frozenset({1, 2, 4, 6})


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PruningViolation:
    """A pruning event at a decomposition node."""
    axiom: Union[int, str]
    rule: str
    condition: str

    def to_dict(self) -> Dict[str, Any]:
        return {"axiom": self.axiom, "rule": self.rule, "condition": self.condition}


@dataclass
class DecompositionNode:
    """A node in the retrosynthetic decomposition tree."""
    node_id: str
    branch_name: str
    notation: Optional[str]        # compact notation string for this sub-system
    imscription: Optional[Imscription]     # resolved Imscription if available
    is_pruned: bool = False
    is_leaf: bool = False          # True if terminal valid imscription tuple
    violations: List[PruningViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    children: List["DecompositionNode"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.node_id,
            "branch": self.branch_name,
            "notation": self.notation,
            "is_pruned": self.is_pruned,
            "is_leaf": self.is_leaf,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": self.warnings,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class DecompositionTree:
    """Full retrosynthetic decomposition tree."""
    target_notation: str
    root: Optional[DecompositionNode]
    valid_leaves: List[DecompositionNode]
    pruned_count: int
    prune_axioms: List[int]
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target_notation,
            "prune_axioms": self.prune_axioms,
            "valid_decompositions": len(self.valid_leaves),
            "pruned_branches": self.pruned_count,
            "tree": self.root.to_dict() if self.root else None,
            "valid_imscription_set": [
                (leaf.imscription.name if leaf.imscription else leaf.notation)
                for leaf in self.valid_leaves
            ],
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# Axiom pruning helpers
# ---------------------------------------------------------------------------

def _check_axioms(
    imscription: Imscription,
    prune_set: frozenset,
) -> List[PruningViolation]:
    """Run specified axioms on a imscription and return any violations."""
    violations: List[PruningViolation] = []

    if 1 in prune_set:
        r = AxiomValidator.validate_axiom1_cyclic_closure(imscription)
        if r.get("applies") and r.get("violated"):
            violations.append(PruningViolation(
                axiom=1,
                rule="Fidelity Floor",
                condition="T_⋈ + P_± + F_ℓ → PRUNE (Axiom 1)",
            ))

    if 2 in prune_set:
        # Only prune if the sub-tuple CLAIMS global granularity (G_ℵ) but
        # lacks the grammar to support it. Axiom 2 does not prune G_ב sub-tuples
        # that don't claim global scope — those are valid local components.
        if imscription.granularity == Granularity.GLOBAL:
            r = AxiomValidator.validate_axiom2_local_grammar_barrier(
                imscription, target_granularity=Granularity.GLOBAL
            )
            if r.get("applies") and r.get("violated"):
                violations.append(PruningViolation(
                    axiom=2,
                    rule="Propagation Barrier",
                    condition=(
                        "G_ℵ claimed but G_ב + Γ_∧(SPECIFIC) lacks Γ_∨ or T_nrleg "
                        "→ PRUNE (Axiom 2)"
                    ),
                ))

    if 4 in prune_set:
        r = AxiomValidator.validate_axiom4_sequential_grammar(imscription)
        if r.get("applies") and r.get("violated"):
            violations.append(PruningViolation(
                axiom=4,
                rule="Grammar Mismatch",
                condition="Γ_→ without D_∞ or R_‡ → PRUNE (Axiom 4)",
            ))

    if 6 in prune_set:
        r = AxiomValidator.validate_axiom6_temporal_grounding(imscription)
        if isinstance(r, AxiomResult) and r.violated:
            violations.append(PruningViolation(
                axiom=6,
                rule="Grounding Fail",
                condition="D_∞ without reset mechanism → FLAG (Axiom 6)",
            ))

    return violations


# ---------------------------------------------------------------------------
# Candidate generation
# ---------------------------------------------------------------------------

_DIM_TO_R = {
    Dimensionality.MOLECULAR:     RecognitionMode.COVALENT,
    Dimensionality.SUPRAMOLECULAR: RecognitionMode.NON_COVALENT,
    Dimensionality.TEMPORAL:      RecognitionMode.DYNAMIC_CATALYTIC,
}


def _split_candidates(target: Imscription) -> List[Dict[str, Any]]:
    """
    Generate candidate sub-tuple overrides for a given target.

    Strategy priority:
      1. Hybrid D → split along dimensional axes
      2. Single D → find similar from catalog, filtered to same domain(s)
      3. Fallback → two generic branches with target dimensionality

    Domain filter (fix for cross-domain semantic drift):
      Catalog search results are restricted to imscriptions whose dimensionality
      shares at least one domain with the target.  A molecular/temporal target
      will not receive supramolecular or cross-domain catalog hits as candidates.
    """
    candidates: List[Dict[str, Any]] = []
    domains = _domains(target.dimensionality)

    if len(domains) >= 2:
        domain_list = list(domains)
        dim_map = {
            "molecular":      Dimensionality.MOLECULAR,
            "supramolecular": Dimensionality.SUPRAMOLECULAR,
            "temporal":       Dimensionality.TEMPORAL,
        }
        for domain in domain_list:
            dim = dim_map.get(domain, target.dimensionality)
            candidates.append({
                "branch": f"{domain.capitalize()} Component",
                "dimensionality": dim,
                "recognition_mode": _DIM_TO_R.get(dim, target.recognition_mode),
            })
    else:
        from .registry import global_catalog
        similar = global_catalog.search(
            dimensionality=target.dimensionality,
            recognition_mode=target.recognition_mode,
        )
        # Domain filter: only include catalog hits that share a domain with the target
        # and are not cross-domain (non-chemical) entries.
        target_domains = _domains(target.dimensionality)
        domain_filtered = [
            s for s in similar
            if (_domains(s.dimensionality) & target_domains)  # same domain(s)
            and not (getattr(s, "metadata", None) or {}).get("cross_domain", False)
        ]
        for s in domain_filtered[:4]:
            candidates.append({"branch": s.name, "_imscription": s})

    if not candidates:
        candidates = [
            {"branch": "Branch_A", "dimensionality": target.dimensionality},
            {"branch": "Branch_B", "dimensionality": target.dimensionality},
        ]

    return candidates


def _build_sub_imscription(target: Imscription, overrides: Dict[str, Any], branch: str) -> Imscription:
    """Construct a sub-Imscription from target notation with selective overrides."""
    return Imscription(
        name=branch.lower().replace(" ", "_"),
        dimensionality=overrides.get("dimensionality", target.dimensionality),
        topology=overrides.get("topology", target.topology),
        recognition_mode=overrides.get("recognition_mode", target.recognition_mode),
        polarity=overrides.get("polarity", target.polarity),
        fidelity=overrides.get("fidelity", target.fidelity),
        kinetic_character=overrides.get("kinetic_character", target.kinetic_character),
        granularity=overrides.get("granularity", target.granularity),
        interaction_grammar=overrides.get("interaction_grammar", target.interaction_grammar),
        criticality_phase=overrides.get("criticality_phase", target.criticality_phase),
        description=f"Retrodesign sub-tuple: {branch}",
    )


# ---------------------------------------------------------------------------
# RetrodesignEngine
# ---------------------------------------------------------------------------

class RetrodesignEngine:
    """
    Constraint-directed retrosynthetic decomposition engine.

    Recursively splits a target notation into sub-tuples, pruning branches
    on axiom violation or pairwise incompatibility.

    Example::

        engine = RetrodesignEngine()
        tree = engine.decompose(
            "⟨{D_turnthree, D_infinity}; T_cage; R_superset+ddagger; "
            "P_pipevar; F_dh; K_turnm; G_gamma; Gamma_and(SELECTIVE); Phi_softsign; 4:4⟩",
            max_depth=3,
            prune_axioms=[1, 2, 4, 6],
        )
        print(tree.valid_imscription_set)
    """

    def __init__(self):
        self._engine = ConstraintEngine()
        self._counter = 0

    def _uid(self, prefix: str = "node") -> str:
        self._counter += 1
        return f"{prefix}_{self._counter}"

    def _resolve_target(
        self, target_notation: str
    ) -> tuple[Optional[Imscription], Optional[Imscription], List[str]]:
        """Parse or look up the target, returning (parsed_imscription, catalog_imscription, warnings)."""
        warnings: List[str] = []

        # Try notation parse
        if target_notation.strip().startswith(("⟨", "<")):
            try:
                parsed = _parse_notation_to_imscription(target_notation, name="target")
                return parsed, None, warnings
            except Exception as exc:
                warnings.append(f"Notation parse failed: {exc}. Falling back to catalog.")

        # Catalog lookup
        from .registry import global_catalog
        s = global_catalog.get(target_notation)
        if s:
            return s, s, warnings

        warnings.append(
            f"Could not resolve '{target_notation}'. "
            "Provide a valid ⟨...⟩ notation string or a catalog imscription name."
        )
        return None, None, warnings

    def decompose(
        self,
        target_notation: str,
        max_depth: int = 3,
        prune_axioms: Optional[List[int]] = None,
        strict_grounding: bool = False,
        prune_ktrap: bool = True,
    ) -> DecompositionTree:
        """
        Decompose a target notation into valid sub-tuples.

        Args:
            target_notation:  ⟨...⟩ string or catalog imscription name
            max_depth:        maximum recursion depth (default 3)
            prune_axioms:     axiom numbers to enforce (default [1, 2, 4, 6])
            strict_grounding: if True, abort decomposition when the target has
                              D_∞ but no Axiom 6 grounding metadata (default False)
            prune_ktrap:      if True, prune leaf nodes with K_teshlig kinetics
                              (no escape pathway specified); default True

        Returns:
            DecompositionTree with full tree + list of valid leaf nodes
        """
        if prune_axioms is None:
            prune_axioms = list(DEFAULT_PRUNE_AXIOMS)
        prune_set = frozenset(prune_axioms)
        self._counter = 0

        target_parsed, target_imscription, warnings = self._resolve_target(target_notation)
        if target_parsed is None:
            return DecompositionTree(
                target_notation=target_notation,
                root=None,
                valid_leaves=[],
                pruned_count=0,
                prune_axioms=prune_axioms,
                warnings=warnings,
            )

        # Build root imscription
        root_imscription = target_imscription or _build_sub_imscription(
            target_parsed, {}, "Target Root"
        )
        root_imscription.name = "target_root"

        # Grounding check: D∞ target without axiom6_grounding or grounding.reset
        grounding_absent = False
        if "temporal" in _domains(target_parsed.dimensionality):
            meta = getattr(root_imscription, "metadata", None) or {}
            sg = getattr(root_imscription, "grounding", None) or {}
            has_grounding = (
                sg.get("reset")                              # primary: imscription.grounding["reset"] (persisted)
                or meta.get("axiom6_grounding")              # legacy structured metadata block
                or meta.get("grounding", {}).get("reset")    # legacy metadata-nested path
                or meta.get("grounding", {}).get("cycle_steps")
            )
            if not has_grounding:
                grounding_absent = True
                msg = (
                    "Target has D_∞ (temporal) but no Axiom 6 grounding "
                    "(missing imscription.grounding['reset'] block). "
                    "Run 'imscribe audit --axiom 6' to backfill grounding before decomposition."
                )
                if strict_grounding:
                    warnings.append(f"[BLOCKED] {msg}")
                    return DecompositionTree(
                        target_notation=target_notation,
                        root=None,
                        valid_leaves=[],
                        pruned_count=0,
                        prune_axioms=prune_axioms,
                        warnings=warnings,
                    )
                warnings.append(f"[WARNING] {msg} Decomposition proceeds but leaf validation may be unreliable.")

        root = DecompositionNode(
            node_id=self._uid("root"),
            branch_name="Root (Target)",
            notation=target_notation,
            imscription=root_imscription,
        )

        valid_leaves: List[DecompositionNode] = []
        pruned_count = [0]

        self._expand(root, target_parsed, prune_set, 0, max_depth, valid_leaves, pruned_count, prune_ktrap=prune_ktrap)

        return DecompositionTree(
            target_notation=target_notation,
            root=root,
            valid_leaves=valid_leaves,
            pruned_count=pruned_count[0],
            prune_axioms=prune_axioms,
            warnings=warnings,
        )

    def _expand(
        self,
        node: DecompositionNode,
        target: Imscription,
        prune_set: frozenset,
        depth: int,
        max_depth: int,
        valid_leaves: list,
        pruned_count: list,
        prune_ktrap: bool = True,
    ) -> None:
        """Recursively expand a node into candidate sub-tuples.

        Root node (depth=0) is never added to valid_leaves — it is the
        decomposition target, not a retrosynthetic route.
        """
        if depth >= max_depth:
            # Root at max_depth means no expansion possible — still not a route
            if node.branch_name != "Root (Target)":
                node.is_leaf = True
                valid_leaves.append(node)
            return

        candidates = _split_candidates(target)

        # Name of the root target (for self-reference exclusion)
        root_name = node.imscription.name if node.imscription else None

        for candidate in candidates:
            # Use existing imscription from catalog if available
            existing = candidate.get("_imscription")
            if existing:
                # Skip self-references: a imscription cannot be its own precursor
                if root_name and existing.name == root_name:
                    continue
                child_imscription = existing
            else:
                child_imscription = _build_sub_imscription(
                    target, candidate, candidate.get("branch", "component")
                )

            violations = _check_axioms(child_imscription, prune_set)
            node_warnings: List[str] = []

            # K_teshlig: prune by default (no escape pathway); warn only if prune_ktrap=False
            if child_imscription.kinetic_character == KineticCharacter.TRAP:
                if prune_ktrap:
                    violations.append(PruningViolation(
                        axiom="Kinetics",
                        rule="K_teshlig without escape pathway",
                        condition=(
                            "K_teshlig assigned with no escape pathway metadata. "
                            "Specify metadata['escape_pathway'] or use prune_ktrap=False "
                            "to demote to warning. See IG_HOTSWAP.md §2.2."
                        ),
                    ))
                else:
                    node_warnings.append(
                        "K_teshlig detected — escape pathway not specified "
                        "(IG_HOTSWAP.md §2.2); +0.5 nat accessibility penalty applied"
                    )

            child = DecompositionNode(
                node_id=self._uid("node"),
                branch_name=candidate.get("branch", child_imscription.name),
                notation=(
                    child_imscription.to_notation()
                    if hasattr(child_imscription, "to_notation") else None
                ),
                imscription=child_imscription,
                violations=violations,
                warnings=node_warnings,
            )

            if violations:
                child.is_pruned = True
                pruned_count[0] += 1
            else:
                # Siblings are alternative retrosynthetic routes (OR logic), not
                # concurrent components — no sibling compatibility check here.
                child.is_leaf = True
                valid_leaves.append(child)

            node.children.append(child)


# ---------------------------------------------------------------------------
# parse_notation_from_string — public alias for _parse_notation_to_imscription
# ---------------------------------------------------------------------------

def parse_notation_from_string(notation_str: str) -> Imscription:
    """
    Parse a ⟨...⟩ notation string into a Imscription.

        target = parse_notation_from_string("⟨D_turnthree; T_cage; ...⟩")
    """
    return _parse_notation_to_imscription(notation_str)
