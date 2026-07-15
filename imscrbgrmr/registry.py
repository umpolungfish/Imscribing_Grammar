"""
Imscription Registry — Catalog and search functionality for imscriptions.

This module provides the ImscriptionCatalog class for storing, retrieving,
and searching imscriptions by their primitive values.
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
    Imscription,
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
    Raised when imscription registration is blocked due to grounding failures.
    
    See: IG_FIXES.md Fix 1 — Registration Block on Grounding Warnings
    """
    pass


@dataclass
class CatalogEntry:
    """
    Enhanced catalog entry with grounding metadata (Fix 1).
    
    Attributes:
        imscription: The imscription object
        grounding_status: "full", "partial", "override", "unverified", or "flagged_for_review"
        failed_primitives: List of primitives that failed grounding
        override_reason: Human-provided justification for grounding override
        registered_by: Model provider that generated it (e.g., "anthropic", "qwen")
        registered_at: Registration timestamp
        domain: Imscription domain (molecular, supramolecular, temporal, speculative, quantum)
    """
    imscription: Imscription
    grounding_status: str = "unverified"  # full, partial, override, unverified, flagged_for_review
    failed_primitives: List[str] = field(default_factory=list)
    override_reason: Optional[str] = None
    registered_by: str = "unknown"
    registered_at: datetime = field(default_factory=datetime.now)
    domain: str = "molecular"  # molecular, supramolecular, temporal, hybrid, speculative, quantum
    excluded_from_analogies: bool = False  # Audit: exclude from analogy searches when flagged
    flagged_by: Optional[str] = None  # Audit pass that flagged this entry (e.g. "audit_pass_1")


@dataclass
class ImscriptionCatalog:
    """
    Catalog for storing and querying imscriptions.

    Supports:
    - Registration of imscriptions by name or ID
    - Search by primitive values
    - Cross-domain queries
    - JSON persistence (auto-saves to .imscrbgrmr_catalog.json)
    - Grounding validation with registration blocking (Fix 1)
    """
    name: str = "default_catalog"
    _imscriptions: Dict[str, Imscription] = field(default_factory=dict)
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
        self._loaded = False  # lazy: load on first access

    def _ensure_loaded(self):
        if self._loaded:
            return
        self._loaded = True
        if self._storage_path and self._storage_path.exists():
            try:
                self._load_into_self(self._storage_path)
            except Exception:
                pass
    
    def _load_into_self(self, path: Path) -> None:
        """Load catalog data from disk into this instance (preserves storage path)."""
        with open(path, "r") as f:
            data = json.load(f)

        # Clear current state
        self._imscriptions.clear()
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

        # Load imscriptions and grounding metadata
        for imscription_data in data.get("imscriptions", []):
            imscription = Imscription.from_dict(imscription_data)
            # Manually add without triggering auto-save (we'll save at the end)
            self._imscriptions[imscription.name] = imscription
            self._by_dimensionality[imscription.dimensionality].add(imscription.name)
            self._by_topology[imscription.topology].add(imscription.name)
            self._by_recognition[imscription.recognition_mode].add(imscription.name)
            self._by_polarity[imscription.polarity].add(imscription.name)
            self._by_fidelity[imscription.fidelity].add(imscription.name)
            self._by_granularity[imscription.granularity].add(imscription.name)
            self._by_grammar[imscription.interaction_grammar].add(imscription.name)
            
            # Fix 1: Load grounding metadata if present
            metadata = imscription_data.get("metadata", {})
            if metadata:
                self._entry_metadata[imscription.name] = CatalogEntry(
                    imscription=imscription,
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
        imscription: Imscription,
        grounding_result: Optional[Any] = None,
        strict_grounding: bool = False,
        override_grounding: bool = False,
        override_reason: Optional[str] = None,
        registered_by: str = "unknown",
        domain: str = "molecular",
    ) -> None:
        self._ensure_loaded()
        """
        Register a imscription in the catalog. Auto-saves to disk if storage path is set.
        
        Fix 1 (IG_FIXES.md): Added grounding validation with registration blocking.
        
        Args:
            imscription: The imscription to register
            grounding_result: GroundingResult object with per-primitive pass/fail flags
            strict_grounding: If True, block registration on any grounding failure
            override_grounding: If True, allow registration despite grounding failure
                               (requires override_reason)
            override_reason: Human-provided justification for override (logged to audit trail)
            registered_by: Model provider that generated it (e.g., "anthropic", "qwen")
            domain: Imscription domain (molecular, supramolecular, temporal, speculative, quantum)
            
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
                self._log_grounding_override(imscription.name, failed, override_reason)
        
        # Register the imscription
        self._imscriptions[imscription.name] = imscription

        # Update indices
        self._by_dimensionality[imscription.dimensionality].add(imscription.name)
        self._by_topology[imscription.topology].add(imscription.name)
        self._by_recognition[imscription.recognition_mode].add(imscription.name)
        self._by_polarity[imscription.polarity].add(imscription.name)
        self._by_fidelity[imscription.fidelity].add(imscription.name)
        self._by_granularity[imscription.granularity].add(imscription.name)
        self._by_grammar[imscription.interaction_grammar].add(imscription.name)
        
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
        
        self._entry_metadata[imscription.name] = CatalogEntry(
            imscription=imscription,
            grounding_status=grounding_status,
            failed_primitives=failed_primitives,
            override_reason=override_reason,
            registered_by=registered_by,
            domain=domain,
        )

        # Auto-save to disk if storage path is configured and batch mode is off
        if self._storage_path and not getattr(self, '_batch_loading', False):
            try:
                self.save(self._storage_path)
            except Exception as e:
                logging.warning(f"Failed to auto-save catalog: {e}")
    
    def _log_grounding_override(self, imscription_name: str, failed_primitives: List[str], reason: str) -> None:
        """
        Log grounding override to audit trail.
        
        Args:
            imscription_name: Name of the imscription being registered
            failed_primitives: List of primitives that failed grounding
            reason: Human-provided justification for override
        """
        logging.warning(
            f"GROUNDING OVERRIDE: Imscription '{imscription_name}' registered with "
            f"ungrounded primitives {failed_primitives}. Reason: {reason}"
        )
    
    def get(self, name: str) -> Optional[Imscription]:
        """Retrieve a imscription by name."""
        self._ensure_loaded()
        return self._imscriptions.get(name)
    
    def get_entry_metadata(self, name: str) -> Optional[CatalogEntry]:
        """
        Get grounding metadata for a registered imscription (Fix 1).
        
        Args:
            name: Imscription name
            
        Returns:
            CatalogEntry with grounding status, failed primitives, etc.
        """
        return self._entry_metadata.get(name)
    
    def get_grounding_status(self, name: str) -> str:
        """
        Get grounding status for a imscription (Fix 1).
        
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
            name: Imscription name to flag
            pass_id: Audit pass identifier (e.g. 'audit_pass_1', 'audit_pass_3')
            dry_run: If True, don't write changes

        Returns:
            True if entry was found and flagged (or would be flagged in dry_run)
        """
        entry = self._entry_metadata.get(name)
        imscription = self._imscriptions.get(name)
        if not entry or not imscription:
            return False
        if not dry_run:
            entry.grounding_status = "flagged_for_review"
            entry.excluded_from_analogies = True
            entry.flagged_by = pass_id
            imscription.metadata["flagged_for_review"] = True
            imscription.metadata["excluded_from_analogies"] = True
            imscription.metadata["flagged_by"] = pass_id
        return True

    def remove(self, name: str) -> bool:
        """
        Remove a imscription from the catalog by name. Auto-saves if storage path is set.

        Returns:
            True if the imscription was found and removed, False if not found.
        """
        if name not in self._imscriptions:
            return False
        imscription = self._imscriptions.pop(name)
        self._by_dimensionality[imscription.dimensionality].discard(name)
        self._by_topology[imscription.topology].discard(name)
        self._by_recognition[imscription.recognition_mode].discard(name)
        self._by_polarity[imscription.polarity].discard(name)
        self._by_fidelity[imscription.fidelity].discard(name)
        self._by_granularity[imscription.granularity].discard(name)
        self._by_grammar[imscription.interaction_grammar].discard(name)
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

    def update_imscription_reasoning(self, name: str, reasoning: str, provider: str = "unknown") -> bool:
        """
        Update grounding/reasoning text for an existing catalog entry.

        Used by the reconstruct command to back-fill reasoning from discovery_history files.

        Returns:
            True if entry was found and updated
        """
        imscription = self._imscriptions.get(name)
        if not imscription:
            return False
        if imscription.grounding is None:
            imscription.grounding = {}
        imscription.grounding["reasoning"] = reasoning
        imscription.grounding["provider"] = provider
        imscription.is_grounded = bool(reasoning)
        entry = self._entry_metadata.get(name)
        if entry and entry.grounding_status == "unverified" and reasoning:
            entry.grounding_status = "partial"
            if entry.registered_by == "unknown" and provider != "unknown":
                entry.registered_by = provider
        return True
    
    def __getitem__(self, name: str) -> Imscription:
        imscription = self.get(name)
        if imscription is None:
            raise KeyError(f"Imscription '{name}' not found in catalog")
        return imscription
    
    def __contains__(self, name: str) -> bool:
        self._ensure_loaded()
        return name in self._imscriptions

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._imscriptions)

    def __iter__(self) -> Iterator[Imscription]:
        self._ensure_loaded()
        return iter(self._imscriptions.values())

    def search(
        self,
        dimensionality: Optional[Dimensionality] = None,
        topology: Optional[Topology] = None,
        recognition_mode: Optional[RecognitionMode] = None,
        polarity: Optional[Polarity] = None,
        fidelity: Optional[Fidelity] = None,
        granularity: Optional[Granularity] = None,
        interaction_grammar: Optional[InteractionGrammar] = None,
    ) -> List[Imscription]:
        self._ensure_loaded()
        """
        Search for imscriptions matching specified primitive values.
        
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
            return list(self._imscriptions.values())
        
        # Intersect all candidate sets
        candidate_names = candidate_sets[0]
        for s in candidate_sets[1:]:
            candidate_names = candidate_names & s
        
        return [self._imscriptions[name] for name in candidate_names]
    
    def search_by_domain(self, domain: str) -> List[Imscription]:
        """
        Search for imscriptions by domain (molecular, supramolecular, temporal).
        """
        results = []
        for imscription in self._imscriptions.values():
            if domain in imscription.dimensionality.domains:
                results.append(imscription)
        return results
    
    def find_similar(self, imscription: Imscription, match_primitives: int = 5) -> List[Imscription]:
        """
        Find imscriptions similar to the given one.
        
        Args:
            imscription: Reference imscription
            match_primitives: Minimum number of primitives that must match
        
        Returns:
            List of similar imscriptions, sorted by similarity score
        """
        similar = []
        
        for other in self._imscriptions.values():
            if other.name == imscription.name:
                continue
            
            # Count matching primitives
            matches = 0
            if other.dimensionality == imscription.dimensionality:
                matches += 1
            if other.topology == imscription.topology:
                matches += 1
            if other.recognition_mode == imscription.recognition_mode:
                matches += 1
            if other.polarity == imscription.polarity:
                matches += 1
            if other.fidelity == imscription.fidelity:
                matches += 1
            if other.granularity == imscription.granularity:
                matches += 1
            if other.interaction_grammar == imscription.interaction_grammar:
                matches += 1
            
            if matches >= match_primitives:
                similar.append((matches, other))
        
        # Sort by number of matches (descending)
        similar.sort(key=lambda x: -x[0])
        return [s[1] for s in similar]
    
    def find_cross_domain_analogs(
        self,
        imscription: Imscription,
        target_domain: str,
    ) -> List[Imscription]:
        """
        Find imscriptions in a different domain with similar primitive patterns.
        
        This enables the cross-domain similarity search described in
        QUANTIG.md — e.g., finding "temporal imscriptions with a
        regeneration mechanism analogous to the self-complementarity of
        a carboxylic acid homodimer."
        
        Args:
            imscription: Reference imscription
            target_domain: Target domain ('molecular', 'supramolecular', 'temporal')
        
        Returns:
            List of analog imscriptions in the target domain
        """
        analogs = []
        
        for other in self._imscriptions.values():
            # Must be in target domain
            if target_domain not in other.dimensionality.domains:
                continue
            
            # Must NOT be in the same domain as reference
            if imscription.dimensionality.domains == other.dimensionality.domains:
                continue
            
            # Score based on matching non-dimensionality primitives
            score = 0
            
            if other.topology == imscription.topology:
                score += 2  # Topology is highly significant
            if other.recognition_mode == imscription.recognition_mode:
                score += 2
            if other.polarity == imscription.polarity:
                score += 1
            if other.fidelity == imscription.fidelity:
                score += 2  # Fidelity is key for cross-domain comparison
            if other.granularity == imscription.granularity:
                score += 1
            if other.interaction_grammar == imscription.interaction_grammar:
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
            "imscriptions": [],
        }
        
        # Fix 1: Include grounding metadata in serialization
        for imscription in self._imscriptions.values():
            imscription_dict = imscription.to_dict()
            
            # Add grounding metadata if present
            metadata = self._entry_metadata.get(imscription.name)
            if metadata:
                imscription_dict["metadata"] = {
                    "grounding_status": metadata.grounding_status,
                    "failed_primitives": metadata.failed_primitives,
                    "override_reason": metadata.override_reason,
                    "registered_by": metadata.registered_by,
                    "domain": metadata.domain,
                    "excluded_from_analogies": metadata.excluded_from_analogies,
                    "flagged_by": metadata.flagged_by,
                }
            
            result["imscriptions"].append(imscription_dict)
        
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize catalog to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ImscriptionCatalog:
        """Create catalog from dictionary."""
        catalog = cls(name=data.get("name", "default_catalog"))
        for imscription_data in data.get("imscriptions", []):
            imscription = Imscription.from_dict(imscription_data)
            catalog.register(imscription)
        return catalog
    
    @classmethod
    def from_json(cls, json_str: str) -> ImscriptionCatalog:
        """Create catalog from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def save(self, path: str | Path) -> None:
        """Save catalog to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, path: str | Path) -> ImscriptionCatalog:
        """Load catalog from JSON file."""
        path = Path(path)
        with open(path, "r") as f:
            return cls.from_json(f.read())
    
    def summary(self) -> Dict[str, Any]:
        """Return catalog summary statistics."""
        return {
            "name": self.name,
            "total_imscriptions": len(self._imscriptions),
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
                    s for s in self._imscriptions.values()
                    if len(s.dimensionality.domains) > 1
                ]),
            },
        }

    def populate_defaults(self) -> None:
        """Populate the catalog with default imscriptions from QUANTIG.md."""
        self._ensure_loaded()
        from .models import (
            Dimensionality, Topology, RecognitionMode, Polarity, Fidelity,
            Granularity, InteractionGrammar, KineticCharacter, Imscription,
            Criticality, Protection, Stoichiometry, Chirality,
        )

        defaults = [
            Imscription(
                name="carboxylic_acid_dimer",
                dimensionality=Dimensionality.dead,
                topology=Topology.mime,
                recognition_mode=RecognitionMode.ado,
                polarity=Polarity.yew,
                fidelity=Fidelity.peep,
                kinetic_character=KineticCharacter.yea,
                granularity=Granularity.ice,
                grammar=InteractionGrammar.vow,
                criticality_phase=Criticality.woe,
                protection=Protection.awe,
                stoichiometry=Stoichiometry.hung,
                chirality=Chirality.fee,
                description="Classic R₂²(8) hydrogen-bonded dimer",
            ),
            Imscription(
                name="adenine_thymine_pair",
                dimensionality=Dimensionality.dead,
                topology=Topology.mime,
                recognition_mode=RecognitionMode.ado,
                polarity=Polarity.church,
                fidelity=Fidelity.peep,
                kinetic_character=KineticCharacter.yea,
                granularity=Granularity.bib,
                grammar=InteractionGrammar.vow,
                criticality_phase=Criticality.woe,
                protection=Protection.awe,
                stoichiometry=Stoichiometry.hung,
                chirality=Chirality.fee,
                description="Canonical DNA A-T base pair",
            ),
            Imscription(
                name="proline_aldol_cycle",
                dimensionality=Dimensionality.array,
                topology=Topology.mime,
                recognition_mode=RecognitionMode.ear,
                polarity=Polarity.church,
                fidelity=Fidelity.they,
                kinetic_character=KineticCharacter.loll,
                granularity=Granularity.bib,
                grammar=InteractionGrammar.measure,
                criticality_phase=Criticality.woe,
                protection=Protection.awe,
                stoichiometry=Stoichiometry.up,
                chirality=Chirality.kick,
                description="Proline-catalyzed aldol reaction cycle",
            ),
            Imscription(
                name="enolate_imscription",
                dimensionality=Dimensionality.dead,
                topology=Topology.T_linear,
                recognition_mode=RecognitionMode.tot,
                polarity=Polarity.yew,
                fidelity=Fidelity.they,
                kinetic_character=KineticCharacter.loll,
                granularity=Granularity.ice,
                grammar=InteractionGrammar.vow,
                criticality_phase=Criticality.woe,
                protection=Protection.awe,
                stoichiometry=Stoichiometry.hung,
                chirality=Chirality.fee,
                description="Nucleophilic enolate fragment",
            ),
            Imscription(
                name="carbonyl_imscription",
                dimensionality=Dimensionality.dead,
                topology=Topology.T_linear,
                recognition_mode=RecognitionMode.tot,
                polarity=Polarity.yew,
                fidelity=Fidelity.they,
                kinetic_character=KineticCharacter.loll,
                granularity=Granularity.ice,
                grammar=InteractionGrammar.vow,
                criticality_phase=Criticality.woe,
                protection=Protection.awe,
                stoichiometry=Stoichiometry.hung,
                chirality=Chirality.fee,
                description="Electrophilic carbonyl fragment",
            ),
        ]

        self._batch_loading = True
        try:
            for s in defaults:
                self.register(s)
        finally:
            self._batch_loading = False
            if self._storage_path:
                try:
                    self.save(self._storage_path)
                except Exception:
                    pass


# Global shared catalog instance with auto-persistence
_global_catalog_path = Path.home() / ".imscrbgrmr" / "catalog.json"
_global_catalog_path.parent.mkdir(parents=True, exist_ok=True)
global_catalog = ImscriptionCatalog(name="global_Imscriptiveon", _storage_path=_global_catalog_path)


# ---------------------------------------------------------------------------
# Validation-tier helper
# ---------------------------------------------------------------------------

def get_validation_tier(imscription: "Imscription") -> str:
    """
    Return the validation tier for a imscription.

    Tiers:
        "primary"  — Molecular / supramolecular domain. Full experimental
                     grounding available (ΔG, crystal structure, NMR/DFT).
                     Primary validation anchor for the framework.
        "extended" — Cross-domain or speculative encoding. Phase 1 or
                     analogue grounding only. Same formalism, thinner ground.

    The tier is read from ``imscription.metadata["validation_tier"]`` if set.
    Otherwise it is inferred:
      - ``metadata["cross_domain"] == True``  → "extended"
      - Dimensionality has "molecular" or "supramolecular" domains only → "primary"
      - Any other case → "extended"
    """
    meta = getattr(imscription, "metadata", None) or {}
    explicit = meta.get("validation_tier")
    if explicit in ("primary", "extended"):
        return explicit
    if meta.get("cross_domain", False):
        return "extended"
    domains = getattr(imscription.dimensionality, "domains", set())
    if domains and domains.issubset({"molecular", "supramolecular", "temporal"}):
        return "primary"
    return "extended"


def register_imscription(
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
) -> Imscription:
    """
    Convenience function to register a imscription using string notation.
    
    Supports both old 7-primitive and new 9-primitive notation.

    Example:
        >>> register_imscription(
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
    from .models import ImscriptionNotation, KineticCharacter, CriticalityPhase

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
    
    notation = ImscriptionNotation.parse(notation_str)
    imscription = notation.to_imscription(name, description, **metadata)
    global_catalog.register(imscription)
    return imscription


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
        if isinstance(raw, list):
            entries = raw
        elif "imscriptions" in raw:
            entries = raw["imscriptions"]
        else:
            entries = [v for v in raw.values() if isinstance(v, dict)]
        for entry in entries:
            name = entry.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                merged.append(entry)
    return merged
