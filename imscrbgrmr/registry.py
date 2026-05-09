"""
Synthon Registry — Catalog and search functionality for synthons.

This module provides the SynthonCatalog class for storing, retrieving,
and searching synthons by their primitive values.
"""
from __future__ import annotations

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Iterator
from dataclasses import dataclass, field
from datetime import datetime

from .models import (
    Synthon,
    Dimensionality,
    Topology,
    Recognition,
    RecognitionMode,   # backward compat alias
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
# Backward compat: InteractionGrammar was the old compound type; Grammar is canonical
InteractionGrammar = Grammar


# =============================================================================
# Grounding Validation Support (Fix 1 — IG_FIXES.md)
# =============================================================================

class GroundingValidationError(Exception):
    """
    Raised when synthon registration is blocked due to grounding failures.
    
    See: IG_FIXES.md Fix 1 — Registration Block on Grounding Warnings
    """
    pass


@dataclass
class CatalogEntry:
    """
    Enhanced catalog entry with grounding metadata (Fix 1).
    
    Attributes:
        synthon: The synthon object
        grounding_status: "full", "partial", "override", "unverified", or "flagged_for_review"
        failed_primitives: List of primitives that failed grounding
        override_reason: Human-provided justification for grounding override
        registered_by: Model provider that generated it (e.g., "anthropic", "qwen")
        registered_at: Registration timestamp
        domain: Synthon domain (molecular, supramolecular, temporal, speculative, quantum)
    """
    synthon: Synthon
    grounding_status: str = "unverified"  # full, partial, override, unverified, flagged_for_review
    failed_primitives: List[str] = field(default_factory=list)
    override_reason: Optional[str] = None
    registered_by: str = "unknown"
    registered_at: datetime = field(default_factory=datetime.now)
    domain: str = "molecular"  # molecular, supramolecular, temporal, hybrid, speculative, quantum
    excluded_from_analogies: bool = False  # Audit: exclude from analogy searches when flagged
    flagged_by: Optional[str] = None  # Audit pass that flagged this entry (e.g. "audit_pass_1")


@dataclass
class SynthonCatalog:
    """
    Catalog for storing and querying synthons.

    Supports:
    - Registration of synthons by name or ID
    - Search by primitive values
    - Cross-domain queries
    - JSON persistence (auto-saves to .imscrbgrmr_catalog.json)
    - Grounding validation with registration blocking (Fix 1)
    """
    name: str = "default_catalog"
    _synthons: Dict[str, Synthon] = field(default_factory=dict)
    _by_dimensionality: Dict[Dimensionality, Set[str]] = field(default_factory=lambda: {d: set() for d in Dimensionality})
    _by_topology: Dict[Topology, Set[str]] = field(default_factory=lambda: {t: set() for t in Topology})
    _by_recognition: Dict[RecognitionMode, Set[str]] = field(default_factory=lambda: {r: set() for r in RecognitionMode})
    _by_polarity: Dict[Polarity, Set[str]] = field(default_factory=lambda: {p: set() for p in Polarity})
    _by_fidelity: Dict[Fidelity, Set[str]] = field(default_factory=lambda: {f: set() for f in Fidelity})
    _by_granularity: Dict[Granularity, Set[str]] = field(default_factory=lambda: {g: set() for g in Granularity})
    _by_grammar: Dict[InteractionGrammar, Set[str]] = field(default_factory=lambda: {g: set() for g in InteractionGrammar})
    _storage_path: Optional[Path] = field(default=None, repr=False)
    
    # Fix 1: Grounding metadata storage
    _entry_metadata: Dict[str, CatalogEntry] = field(default_factory=dict)
    
    def __post_init__(self):
        """Auto-load catalog from disk if storage path is set."""
        if self._storage_path and self._storage_path.exists():
            try:
                self._load_into_self(self._storage_path)
            except Exception:
                pass  # Start fresh if load fails
    
    def _load_into_self(self, path: Path) -> None:
        """Load catalog data from disk into this instance (preserves storage path)."""
        with open(path, "r") as f:
            data = json.load(f)

        # Clear current state
        self._synthons.clear()
        for d in self._by_dimensionality:
            self._by_dimensionality[d].clear()
        for t in self._by_topology:
            self._by_topology[t].clear()
        for r in self._by_recognition:
            self._by_recognition[r].clear()
        for p in self._by_polarity:
            self._by_polarity[p].clear()
        for f in self._by_fidelity:
            self._by_fidelity[f].clear()
        for g in self._by_granularity:
            self._by_granularity[g].clear()
        for g in self._by_grammar:
            self._by_grammar[g].clear()
        self._entry_metadata.clear()  # Fix 1: Clear grounding metadata

        # Update name if different
        if data.get("name"):
            self.name = data["name"]

        # Load synthons and grounding metadata
        for synthon_data in data.get("synthons", []):
            synthon = Synthon.from_dict(synthon_data)
            # Manually add without triggering auto-save (we'll save at the end)
            self._synthons[synthon.name] = synthon
            self._by_dimensionality[synthon.dimensionality].add(synthon.name)
            self._by_topology[synthon.topology].add(synthon.name)
            self._by_recognition[synthon.recognition_mode].add(synthon.name)
            self._by_polarity[synthon.polarity].add(synthon.name)
            self._by_fidelity[synthon.fidelity].add(synthon.name)
            self._by_granularity[synthon.granularity].add(synthon.name)
            self._by_grammar[synthon.interaction_grammar].add(synthon.name)
            
            # Fix 1: Load grounding metadata if present
            metadata = synthon_data.get("metadata", {})
            if metadata:
                self._entry_metadata[synthon.name] = CatalogEntry(
                    synthon=synthon,
                    grounding_status=metadata.get("grounding_status", "unverified"),
                    failed_primitives=metadata.get("failed_primitives", []),
                    override_reason=metadata.get("override_reason"),
                    registered_by=metadata.get("registered_by", "unknown"),
                    domain=metadata.get("domain", "molecular"),
                    excluded_from_analogies=metadata.get("excluded_from_analogies", False),
                    flagged_by=metadata.get("flagged_by"),
                )
    
    def register(
        self, 
        synthon: Synthon, 
        grounding_result: Optional[Any] = None,
        strict_grounding: bool = False,
        override_grounding: bool = False,
        override_reason: Optional[str] = None,
        registered_by: str = "unknown",
        domain: str = "molecular",
    ) -> None:
        """
        Register a synthon in the catalog. Auto-saves to disk if storage path is set.
        
        Fix 1 (IG_FIXES.md): Added grounding validation with registration blocking.
        
        Args:
            synthon: The synthon to register
            grounding_result: GroundingResult object with per-primitive pass/fail flags
            strict_grounding: If True, block registration on any grounding failure
            override_grounding: If True, allow registration despite grounding failure
                               (requires override_reason)
            override_reason: Human-provided justification for override (logged to audit trail)
            registered_by: Model provider that generated it (e.g., "anthropic", "qwen")
            domain: Synthon domain (molecular, supramolecular, temporal, speculative, quantum)
            
        Raises:
            GroundingValidationError: If strict_grounding=True and grounding failures exist
            ValueError: If override_grounding=True but no override_reason provided
        """
        # Fix 1: Grounding validation with registration block
        if strict_grounding and grounding_result is not None:
            failed = grounding_result.ungrounded_primitives if hasattr(grounding_result, 'ungrounded_primitives') else []
            
            if failed and not override_grounding:
                raise GroundingValidationError(
                    f"Registration blocked: ungrounded primitives {failed}. "
                    f"Use --override-grounding with --override-reason to force."
                )
            
            if failed and override_grounding:
                if not override_reason:
                    raise ValueError("--override-grounding requires --override-reason")
                
                # Log to audit trail
                self._log_grounding_override(synthon.name, failed, override_reason)
        
        # Register the synthon
        self._synthons[synthon.name] = synthon

        # Update indices
        self._by_dimensionality[synthon.dimensionality].add(synthon.name)
        self._by_topology[synthon.topology].add(synthon.name)
        self._by_recognition[synthon.recognition_mode].add(synthon.name)
        self._by_polarity[synthon.polarity].add(synthon.name)
        self._by_fidelity[synthon.fidelity].add(synthon.name)
        self._by_granularity[synthon.granularity].add(synthon.name)
        self._by_grammar[synthon.interaction_grammar].add(synthon.name)
        
        # Fix 1: Store grounding metadata
        grounding_status = "unverified"
        failed_primitives = []
        
        if grounding_result is not None:
            failed_primitives = grounding_result.ungrounded_primitives if hasattr(grounding_result, 'ungrounded_primitives') else []
            
            if not failed_primitives:
                grounding_status = "full"
            elif override_grounding:
                grounding_status = "override"
            else:
                grounding_status = "partial"
        
        self._entry_metadata[synthon.name] = CatalogEntry(
            synthon=synthon,
            grounding_status=grounding_status,
            failed_primitives=failed_primitives,
            override_reason=override_reason,
            registered_by=registered_by,
            domain=domain,
        )

        # Auto-save to disk if storage path is configured
        if self._storage_path:
            try:
                self.save(self._storage_path)
            except Exception as e:
                logging.warning(f"Failed to auto-save catalog: {e}")
    
    def _log_grounding_override(self, synthon_name: str, failed_primitives: List[str], reason: str) -> None:
        """
        Log grounding override to audit trail.
        
        Args:
            synthon_name: Name of the synthon being registered
            failed_primitives: List of primitives that failed grounding
            reason: Human-provided justification for override
        """
        logging.warning(
            f"GROUNDING OVERRIDE: Synthon '{synthon_name}' registered with "
            f"ungrounded primitives {failed_primitives}. Reason: {reason}"
        )
    
    def get(self, name: str) -> Optional[Synthon]:
        """Retrieve a synthon by name."""
        return self._synthons.get(name)
    
    def get_entry_metadata(self, name: str) -> Optional[CatalogEntry]:
        """
        Get grounding metadata for a registered synthon (Fix 1).
        
        Args:
            name: Synthon name
            
        Returns:
            CatalogEntry with grounding status, failed primitives, etc.
        """
        return self._entry_metadata.get(name)
    
    def get_grounding_status(self, name: str) -> str:
        """
        Get grounding status for a synthon (Fix 1).
        
        Returns:
            "full", "partial", "override", "unverified", or "flagged_for_review"
        """
        entry = self.get_entry_metadata(name)
        return entry.grounding_status if entry else "unverified"
    
    def get_failed_primitives(self, name: str) -> List[str]:
        """
        Get list of primitives that failed grounding (Fix 1).

        Returns:
            List of primitive names that failed grounding
        """
        entry = self.get_entry_metadata(name)
        return entry.failed_primitives if entry else []

    def flag_entry(self, name: str, pass_id: str, dry_run: bool = False) -> bool:
        """
        Flag a catalog entry for review and exclude it from analogy searches.

        Sets grounding_status to 'flagged_for_review', excluded_from_analogies to True,
        and flagged_by to pass_id. Persists to disk if storage_path is set.

        Args:
            name: Synthon name to flag
            pass_id: Audit pass identifier (e.g. 'audit_pass_1', 'audit_pass_3')
            dry_run: If True, don't write changes

        Returns:
            True if entry was found and flagged (or would be flagged in dry_run)
        """
        entry = self._entry_metadata.get(name)
        synthon = self._synthons.get(name)
        if not entry or not synthon:
            return False
        if not dry_run:
            entry.grounding_status = "flagged_for_review"
            entry.excluded_from_analogies = True
            entry.flagged_by = pass_id
            synthon.metadata["flagged_for_review"] = True
            synthon.metadata["excluded_from_analogies"] = True
            synthon.metadata["flagged_by"] = pass_id
        return True

    def remove(self, name: str) -> bool:
        """
        Remove a synthon from the catalog by name. Auto-saves if storage path is set.

        Returns:
            True if the synthon was found and removed, False if not found.
        """
        if name not in self._synthons:
            return False
        synthon = self._synthons.pop(name)
        self._by_dimensionality[synthon.dimensionality].discard(name)
        self._by_topology[synthon.topology].discard(name)
        self._by_recognition[synthon.recognition_mode].discard(name)
        self._by_polarity[synthon.polarity].discard(name)
        self._by_fidelity[synthon.fidelity].discard(name)
        self._by_granularity[synthon.granularity].discard(name)
        self._by_grammar[synthon.interaction_grammar].discard(name)
        self._entry_metadata.pop(name, None)
        if self._storage_path:
            try:
                self.save(self._storage_path)
            except Exception as e:
                logging.warning(f"Failed to auto-save catalog after remove: {e}")
        return True

    def save_catalog(self) -> bool:
        """Persist catalog to its configured storage path. Returns True on success."""
        if self._storage_path:
            try:
                self.save(self._storage_path)
                return True
            except Exception as e:
                logging.warning(f"Failed to save catalog: {e}")
        return False

    def update_synthon_reasoning(self, name: str, reasoning: str, provider: str = "unknown") -> bool:
        """
        Update grounding/reasoning text for an existing catalog entry.

        Used by the reconstruct command to back-fill reasoning from discovery_history files.

        Returns:
            True if entry was found and updated
        """
        synthon = self._synthons.get(name)
        if not synthon:
            return False
        if synthon.grounding is None:
            synthon.grounding = {}
        synthon.grounding["reasoning"] = reasoning
        synthon.grounding["provider"] = provider
        synthon.is_grounded = bool(reasoning)
        entry = self._entry_metadata.get(name)
        if entry and entry.grounding_status == "unverified" and reasoning:
            entry.grounding_status = "partial"
            if entry.registered_by == "unknown" and provider != "unknown":
                entry.registered_by = provider
        return True
    
    def __getitem__(self, name: str) -> Synthon:
        synthon = self.get(name)
        if synthon is None:
            raise KeyError(f"Synthon '{name}' not found in catalog")
        return synthon
    
    def __contains__(self, name: str) -> bool:
        return name in self._synthons
    
    def __len__(self) -> int:
        return len(self._synthons)
    
    def __iter__(self) -> Iterator[Synthon]:
        return iter(self._synthons.values())
    
    def search(
        self,
        dimensionality: Optional[Dimensionality] = None,
        topology: Optional[Topology] = None,
        recognition_mode: Optional[RecognitionMode] = None,
        polarity: Optional[Polarity] = None,
        fidelity: Optional[Fidelity] = None,
        granularity: Optional[Granularity] = None,
        interaction_grammar: Optional[InteractionGrammar] = None,
    ) -> List[Synthon]:
        """
        Search for synthons matching specified primitive values.
        
        All provided criteria must match (AND logic).
        """
        candidate_sets: List[Set[str]] = []
        
        if dimensionality is not None:
            candidate_sets.append(self._by_dimensionality[dimensionality])
        if topology is not None:
            candidate_sets.append(self._by_topology[topology])
        if recognition_mode is not None:
            candidate_sets.append(self._by_recognition[recognition_mode])
        if polarity is not None:
            candidate_sets.append(self._by_polarity[polarity])
        if fidelity is not None:
            candidate_sets.append(self._by_fidelity[fidelity])
        if granularity is not None:
            candidate_sets.append(self._by_granularity[granularity])
        if interaction_grammar is not None:
            candidate_sets.append(self._by_grammar[interaction_grammar])
        
        if not candidate_sets:
            return list(self._synthons.values())
        
        # Intersect all candidate sets
        candidate_names = candidate_sets[0]
        for s in candidate_sets[1:]:
            candidate_names = candidate_names & s
        
        return [self._synthons[name] for name in candidate_names]
    
    def search_by_domain(self, domain: str) -> List[Synthon]:
        """
        Search for synthons by domain (molecular, supramolecular, temporal).
        """
        results = []
        for synthon in self._synthons.values():
            if domain in synthon.dimensionality.domains:
                results.append(synthon)
        return results
    
    def find_similar(self, synthon: Synthon, match_primitives: int = 5) -> List[Synthon]:
        """
        Find synthons similar to the given one.
        
        Args:
            synthon: Reference synthon
            match_primitives: Minimum number of primitives that must match
        
        Returns:
            List of similar synthons, sorted by similarity score
        """
        similar = []
        
        for other in self._synthons.values():
            if other.name == synthon.name:
                continue
            
            # Count matching primitives
            matches = 0
            if other.dimensionality == synthon.dimensionality:
                matches += 1
            if other.topology == synthon.topology:
                matches += 1
            if other.recognition_mode == synthon.recognition_mode:
                matches += 1
            if other.polarity == synthon.polarity:
                matches += 1
            if other.fidelity == synthon.fidelity:
                matches += 1
            if other.granularity == synthon.granularity:
                matches += 1
            if other.interaction_grammar == synthon.interaction_grammar:
                matches += 1
            
            if matches >= match_primitives:
                similar.append((matches, other))
        
        # Sort by number of matches (descending)
        similar.sort(key=lambda x: -x[0])
        return [s[1] for s in similar]
    
    def find_cross_domain_analogs(
        self,
        synthon: Synthon,
        target_domain: str,
    ) -> List[Synthon]:
        """
        Find synthons in a different domain with similar primitive patterns.
        
        This enables the cross-domain similarity search described in
        QUANTIG.md — e.g., finding "temporal synthons with a
        regeneration mechanism analogous to the self-complementarity of
        a carboxylic acid homodimer."
        
        Args:
            synthon: Reference synthon
            target_domain: Target domain ('molecular', 'supramolecular', 'temporal')
        
        Returns:
            List of analog synthons in the target domain
        """
        analogs = []
        
        for other in self._synthons.values():
            # Must be in target domain
            if target_domain not in other.dimensionality.domains:
                continue
            
            # Must NOT be in the same domain as reference
            if synthon.dimensionality.domains == other.dimensionality.domains:
                continue
            
            # Score based on matching non-dimensionality primitives
            score = 0
            
            if other.topology == synthon.topology:
                score += 2  # Topology is highly significant
            if other.recognition_mode == synthon.recognition_mode:
                score += 2
            if other.polarity == synthon.polarity:
                score += 1
            if other.fidelity == synthon.fidelity:
                score += 2  # Fidelity is key for cross-domain comparison
            if other.granularity == synthon.granularity:
                score += 1
            if other.interaction_grammar == synthon.interaction_grammar:
                score += 1
            
            if score >= 4:  # Minimum threshold
                analogs.append((score, other))
        
        # Sort by analogy score
        analogs.sort(key=lambda x: -x[0])
        return [a[1] for a in analogs]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize catalog to dictionary."""
        result = {
            "name": self.name,
            "synthons": [],
        }
        
        # Fix 1: Include grounding metadata in serialization
        for synthon in self._synthons.values():
            synthon_dict = synthon.to_dict()
            
            # Add grounding metadata if present
            metadata = self._entry_metadata.get(synthon.name)
            if metadata:
                synthon_dict["metadata"] = {
                    "grounding_status": metadata.grounding_status,
                    "failed_primitives": metadata.failed_primitives,
                    "override_reason": metadata.override_reason,
                    "registered_by": metadata.registered_by,
                    "domain": metadata.domain,
                    "excluded_from_analogies": metadata.excluded_from_analogies,
                    "flagged_by": metadata.flagged_by,
                }
            
            result["synthons"].append(synthon_dict)
        
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize catalog to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SynthonCatalog:
        """Create catalog from dictionary."""
        catalog = cls(name=data.get("name", "default_catalog"))
        for synthon_data in data.get("synthons", []):
            synthon = Synthon.from_dict(synthon_data)
            catalog.register(synthon)
        return catalog
    
    @classmethod
    def from_json(cls, json_str: str) -> SynthonCatalog:
        """Create catalog from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def save(self, path: str | Path) -> None:
        """Save catalog to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, path: str | Path) -> SynthonCatalog:
        """Load catalog from JSON file."""
        path = Path(path)
        with open(path, "r") as f:
            return cls.from_json(f.read())
    
    def summary(self) -> Dict[str, Any]:
        """Return catalog summary statistics."""
        return {
            "name": self.name,
            "total_synthons": len(self._synthons),
            "by_dimensionality": {
                d.value: len(self._by_dimensionality[d])
                for d in Dimensionality
                if self._by_dimensionality[d]
            },
            "by_fidelity": {
                f.value: len(self._by_fidelity[f])
                for f in Fidelity
                if self._by_fidelity[f]
            },
            "by_domain": {
                "molecular": len(self.search_by_domain("molecular")),
                "supramolecular": len(self.search_by_domain("supramolecular")),
                "temporal": len(self.search_by_domain("temporal")),
                "hybrid": len([
                    s for s in self._synthons.values()
                    if len(s.dimensionality.domains) > 1
                ]),
            },
        }

    def populate_defaults(self) -> None:
        """Populate the catalog with default synthons from QUANTIG.md."""
        from .models import (
            Dimensionality, Topology, RecognitionMode, Polarity, Fidelity,
            Granularity, InteractionGrammar, KineticCharacter, Synthon,
            Criticality, Protection, Stoichiometry, Chirality,
        )

        defaults = [
            Synthon(
                name="carboxylic_acid_dimer",
                dimensionality=Dimensionality.MOLECULAR,
                topology=Topology.CYCLIC_BOWTIE,
                recognition_mode=RecognitionMode.NON_COVALENT,
                polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
                fidelity=Fidelity.HIGH,
                kinetic_character=KineticCharacter.FAST,
                granularity=Granularity.LOCAL,
                grammar=InteractionGrammar.SELECTIVE_AND,
                criticality_phase=Criticality.Phi_softsign,
                protection=Protection.Omega_closeepsilon,
                stoichiometry=Stoichiometry.S_doublebaresh,
                chirality=Chirality.H_closeomega,
                description="Classic R₂²(8) hydrogen-bonded dimer",
            ),
            Synthon(
                name="adenine_thymine_pair",
                dimensionality=Dimensionality.MOLECULAR,
                topology=Topology.CYCLIC_BOWTIE,
                recognition_mode=RecognitionMode.NON_COVALENT,
                polarity=Polarity.DONOR_ACCEPTOR,
                fidelity=Fidelity.HIGH,
                kinetic_character=KineticCharacter.FAST,
                granularity=Granularity.MESOSCALE,
                grammar=InteractionGrammar.SPECIFIC_AND,
                criticality_phase=Criticality.Phi_softsign,
                protection=Protection.Omega_closeepsilon,
                stoichiometry=Stoichiometry.S_doublebaresh,
                chirality=Chirality.H_closeomega,
                description="Canonical DNA A-T base pair",
            ),
            Synthon(
                name="proline_aldol_cycle",
                dimensionality=Dimensionality.TEMPORAL,
                topology=Topology.CYCLIC_BOWTIE,
                recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
                polarity=Polarity.DONOR_ACCEPTOR,
                fidelity=Fidelity.MEDIUM,
                kinetic_character=KineticCharacter.MODERATE,
                granularity=Granularity.MESOSCALE,
                grammar=InteractionGrammar.SELECTIVE_SEQ,
                criticality_phase=Criticality.Phi_softsign,
                protection=Protection.Omega_closeepsilon,
                stoichiometry=Stoichiometry.cat,
                chirality=Chirality.H_toneletterstem,
                description="Proline-catalyzed aldol reaction cycle",
            ),
            Synthon(
                name="enolate_synthon",
                dimensionality=Dimensionality.MOLECULAR,
                topology=Topology.LINEAR,
                recognition_mode=RecognitionMode.COVALENT,
                polarity=Polarity.DONOR,
                fidelity=Fidelity.MEDIUM,
                kinetic_character=KineticCharacter.MODERATE,
                granularity=Granularity.LOCAL,
                grammar=InteractionGrammar.SELECTIVE_AND,
                criticality_phase=Criticality.Phi_softsign,
                protection=Protection.Omega_closeepsilon,
                stoichiometry=Stoichiometry.S_doublebaresh,
                chirality=Chirality.H_closeomega,
                description="Nucleophilic enolate fragment",
            ),
            Synthon(
                name="carbonyl_synthon",
                dimensionality=Dimensionality.MOLECULAR,
                topology=Topology.LINEAR,
                recognition_mode=RecognitionMode.COVALENT,
                polarity=Polarity.ACCEPTOR,
                fidelity=Fidelity.MEDIUM,
                kinetic_character=KineticCharacter.MODERATE,
                granularity=Granularity.LOCAL,
                grammar=InteractionGrammar.SELECTIVE_AND,
                criticality_phase=Criticality.Phi_softsign,
                protection=Protection.Omega_closeepsilon,
                stoichiometry=Stoichiometry.S_doublebaresh,
                chirality=Chirality.H_closeomega,
                description="Electrophilic carbonyl fragment",
            ),
        ]

        for s in defaults:
            self.register(s)


# Global shared catalog instance with auto-persistence
_global_catalog_path = Path.home() / ".imscrbgrmr" / "catalog.json"
_global_catalog_path.parent.mkdir(parents=True, exist_ok=True)
global_catalog = SynthonCatalog(name="global_synthonicon", _storage_path=_global_catalog_path)


# ---------------------------------------------------------------------------
# Validation-tier helper
# ---------------------------------------------------------------------------

def get_validation_tier(synthon: "Synthon") -> str:
    """
    Return the validation tier for a synthon.

    Tiers:
        "primary"  — Molecular / supramolecular domain. Full experimental
                     grounding available (ΔG, crystal structure, NMR/DFT).
                     Primary validation anchor for the framework.
        "extended" — Cross-domain or speculative encoding. Phase 1 or
                     analogue grounding only. Same formalism, thinner ground.

    The tier is read from ``synthon.metadata["validation_tier"]`` if set.
    Otherwise it is inferred:
      - ``metadata["cross_domain"] == True``  → "extended"
      - Dimensionality has "molecular" or "supramolecular" domains only → "primary"
      - Any other case → "extended"
    """
    meta = getattr(synthon, "metadata", None) or {}
    explicit = meta.get("validation_tier")
    if explicit in ("primary", "extended"):
        return explicit
    if meta.get("cross_domain", False):
        return "extended"
    domains = getattr(synthon.dimensionality, "domains", set())
    if domains and domains.issubset({"molecular", "supramolecular", "temporal"}):
        return "primary"
    return "extended"


def register_synthon(
    name: str,
    dimensionality: str,
    topology: str,
    recognition_mode: str,
    polarity: str,
    fidelity: str,
    granularity: str,
    interaction_grammar: str,
    kinetic_character: str = "Ç_turnm",  # NEW parameter
    criticality_phase: Optional[str] = None,  # NEW parameter
    description: str = "",
    **metadata,
) -> Synthon:
    """
    Convenience function to register a synthon using string notation.
    
    Supports both old 7-primitive and new 9-primitive notation.

    Example:
        >>> register_synthon(
        ...     name="carboxylic_acid_dimer",
        ...     dimensionality="Ð_wynn",
        ...     topology="Þ_bullseye",
        ...     recognition_mode="Ř_superset",
        ...     polarity="Φ_pm_pseudo",
        ...     fidelity="ƒ_hardsign",
        ...     granularity="Γ_beta",
        ...     interaction_grammar="Gamma_and(SELECTIVE)",
        ...     kinetic_character="Ç_frtailgamma",
        ...     description="Classic R₂²(8) hydrogen-bonded dimer",
        ... )
    """
    from .models import SynthonNotation, KineticCharacter, CriticalityPhase

    # Build notation string (9 primitives with criticality)
    notation_str = (
        f"⟨{dimensionality}; {topology}; {recognition_mode}; "
        f"{polarity}; {fidelity}; {kinetic_character}; {granularity}; "
        f"{interaction_grammar}"
    )
    if criticality_phase:
        notation_str += f"; {criticality_phase}⟩"
    else:
        # Use Phi_softsign as default for backward compatibility
        notation_str += "; Phi_softsign⟩"
    
    notation = SynthonNotation.parse(notation_str)
    synthon = notation.to_synthon(name, description, **metadata)
    global_catalog.register(synthon)
    return synthon


def load_catalog_dicts(extra_path: Optional[str] = None) -> List[dict]:
    """
    Load catalog entries as plain dicts for navigator scripts.

    Searches (first-occurrence-wins deduplication):
      1. extra_path if provided
      2. IG_catalog.json next to the imscrbgrmr package (canonical catalog)
      3. IG_catalog.json in the current working directory
    """
    import glob as _glob

    _PACKAGE_DIR = Path(__file__).resolve().parent
    _CANDIDATES = [
        str(_PACKAGE_DIR.parent / "IG_catalog.json"),
        "IG_catalog.json",
    ]
    if extra_path:
        _CANDIDATES.insert(0, extra_path)

    paths: List[str] = []
    for candidate in _CANDIDATES:
        if "*" in candidate or "?" in candidate:
            paths.extend(sorted(_glob.glob(candidate)))
        elif os.path.isfile(candidate):
            paths.append(candidate)

    if not paths:
        raise FileNotFoundError(
            "IG_catalog.json not found. Pass --catalog to specify a path."
        )

    seen_names: set = set()
    merged: List[dict] = []
    for p in paths:
        with open(p) as f:
            raw = json.load(f)
        entries = raw if isinstance(raw, list) else list(raw.values())
        for entry in entries:
            name = entry.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                merged.append(entry)
    return merged
