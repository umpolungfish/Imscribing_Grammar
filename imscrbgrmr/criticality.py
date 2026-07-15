"""
Criticality Detection — Utilities for identifying scale-free behavior.

Implements methods to detect when a imscription operates at the G-D degeneracy locus
(from QUANTIG.md Section VIII).

At criticality:
- Correlation length ξ → ∞
- System becomes scale-free and self-similar
- G and D primitives degenerate (cannot be independently assigned)
- Behavior at molecular scale predicts supramolecular and temporal behavior
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

from imscrbgrmr.models import (
    Imscription,
    Granularity,
    Dimensionality,
    CriticalityPhase,
)


@dataclass
class CriticalityAnalysis:
    """Results of criticality analysis."""
    is_critical: bool
    correlation_length: float  # Estimated ξ
    scaling_exponent: Optional[float]  # Critical exponent if determinable
    universality_class: Optional[str]  # If identifiable
    confidence: float  # 0.0-1.0
    indicators: Dict[str, Any]
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_critical": self.is_critical,
            "correlation_length": self.correlation_length,
            "scaling_exponent": self.scaling_exponent,
            "universality_class": self.universality_class,
            "confidence": self.confidence,
            "indicators": self.indicators,
            "recommendation": self.recommendation,
        }


def estimate_correlation_length(
    imscription: Imscription,
    system_size: float,
    order_parameter_fluctuation: float,
) -> float:
    """
    Estimate correlation length ξ from order parameter fluctuations.
    
    Near criticality, ξ diverges as:
        ξ ~ |T - T_c|^(-ν)
    
    where ν is the critical exponent (typically 0.5-1.0).
    
    Args:
        imscription: Imscription to analyze
        system_size: Characteristic system size
        order_parameter_fluctuation: Variance in order parameter
    
    Returns:
        Estimated correlation length in same units as system_size
    """
    # Simple estimator: large fluctuations → large ξ
    # This is a placeholder for proper statistical analysis
    base_xi = system_size * math.sqrt(order_parameter_fluctuation)
    
    # Cap at reasonable maximum (1000× system size indicates criticality)
    return min(base_xi, system_size * 1000)


def detect_scale_free_behavior(
    measurements: Dict[float, float],
) -> Tuple[bool, Optional[float]]:
    """
    Detect scale-free behavior from measurements at different scales.
    
    Args:
        measurements: Dict mapping scale (e.g., length) to observable value
    
    Returns:
        Tuple of (is_scale_free, scaling_exponent)
    """
    if len(measurements) < 3:
        return False, None
    
    # Convert to log-log space
    x_vals = np.log(list(measurements.keys()))
    y_vals = np.log(list(measurements.values()))
    
    # Fit power law: y = a * x^b → log(y) = log(a) + b*log(x)
    if len(x_vals) >= 3:
        coeffs = np.polyfit(x_vals, y_vals, 1)
        scaling_exponent = -coeffs[0]  # Negative slope for typical critical systems
        
        # Check goodness of fit (R²)
        y_pred = coeffs[0] * x_vals + coeffs[1]
        ss_res = np.sum((y_vals - y_pred) ** 2)
        ss_tot = np.sum((y_vals - np.mean(y_vals)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # High R² indicates good power-law fit (scale-free)
        is_scale_free = r_squared > 0.95
        
        return is_scale_free, scaling_exponent if is_scale_free else None
    
    return False, None


def analyze_criticality(
    imscription: Imscription,
    experimental_data: Optional[Dict[str, Any]] = None,
) -> CriticalityAnalysis:
    """
    Comprehensive criticality analysis for a imscription.
    
    Args:
        imscription: Imscription to analyze
        experimental_data: Optional experimental measurements
    
    Returns:
        CriticalityAnalysis with confidence assessment
    """
    indicators: Dict[str, Any] = {}
    confidence_factors: List[float] = []
    
    # Indicator 1: Explicit criticality phase assignment
    if imscription.criticality_phase == CriticalityPhase.CRITICAL:
        indicators["explicit_critical"] = True
        confidence_factors.append(0.9)
    else:
        indicators["explicit_critical"] = False
        confidence_factors.append(0.3)
    
    # Indicator 2: Granularity degeneracy
    # At criticality, G should be ambiguous
    if imscription.granularity == Granularity.MESOSCALE:
        # Mesoscale often indicates proximity to criticality
        indicators["granularity_ambiguous"] = True
        confidence_factors.append(0.6)
    else:
        indicators["granularity_ambiguous"] = False
        confidence_factors.append(0.3)
    
    # Indicator 3: Domain convergence
    # Critical imscriptions often span multiple domains
    num_domains = len(imscription.dimensionality.domains)
    if num_domains >= 2:
        indicators["multi_domain"] = True
        confidence_factors.append(0.7)
    else:
        indicators["multi_domain"] = False
        confidence_factors.append(0.3)
    
    # Indicator 4: Experimental data (if available)
    if experimental_data:
        if "correlation_length" in experimental_data:
            xi = experimental_data["correlation_length"]
            indicators["correlation_length"] = xi
            
            # Large ξ indicates criticality
            if xi > 100:  # Threshold depends on system
                indicators["large_xi"] = True
                confidence_factors.append(0.8)
            else:
                indicators["large_xi"] = False
                confidence_factors.append(0.2)
        
        if "scaling_data" in experimental_data:
            is_sf, exponent = detect_scale_free_behavior(
                experimental_data["scaling_data"]
            )
            indicators["scale_free"] = is_sf
            indicators["scaling_exponent"] = exponent
            
            if is_sf:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.2)
    
    # Compute overall confidence
    confidence = sum(confidence_factors) / len(confidence_factors)
    
    # Determine criticality
    is_critical = (
        indicators.get("explicit_critical", False) or
        (indicators.get("large_xi", False) and indicators.get("scale_free", False)) or
        confidence > 0.7
    )
    
    # --- Confidence fingerprint: identical scores across entries indicate shared
    # primitive pattern (attractor-tuple contamination risk).
    # Encode the pattern that produced this confidence value.
    _pattern = (
        indicators.get("explicit_critical", False),
        indicators.get("granularity_ambiguous", False),
        indicators.get("multi_domain", False),
    )
    indicators["confidence_pattern"] = str(_pattern)
    indicators["confidence_factors"] = [round(f, 3) for f in confidence_factors]

    # Generate per-imscription recommendation incorporating actual evidence
    _evidence_parts = []
    if indicators.get("explicit_critical"):
        _evidence_parts.append("⊙ explicitly assigned")
    else:
        _evidence_parts.append("no explicit ⊙ assignment")
    if indicators.get("granularity_ambiguous"):
        _evidence_parts.append(f"G=MESOSCALE (consistent with G/D ambiguity)")
    else:
        _evidence_parts.append(f"G≠MESOSCALE (atypical for critical system)")
    if indicators.get("multi_domain"):
        _evidence_parts.append(f"D spans multiple domains")
    else:
        _evidence_parts.append("D is single-domain (weakens Varma QXY case)")
    if indicators.get("large_xi"):
        _evidence_parts.append("large experimental ξ measured")
    if indicators.get("scale_free"):
        _evidence_parts.append(f"scale-free behavior confirmed (α={indicators.get('scaling_exponent', '?'):.2f})")

    _evidence_str = "; ".join(_evidence_parts)

    if is_critical:
        # Distinguish evidence-based from pattern-only criticality
        _grounded = bool(
            indicators.get("large_xi") or indicators.get("scale_free")
        )
        if _grounded:
            recommendation = (
                f"Critical assignment grounded in experimental data. Evidence: {_evidence_str}. "
                "Axiom 5: verify molecular-scale behavior predicts supramolecular/temporal behavior."
            )
        else:
            recommendation = (
                f"Critical by primitive assignment only — no ξ or scaling data. "
                f"Evidence: {_evidence_str}. "
                "To confirm: provide ξ_r and ξ_τ measurements and check ξ_r ≈ ln(ξ_τ) "
                "(Varma QXY) or power-law scaling (standard QCP)."
            )
    elif confidence > 0.5:
        recommendation = (
            f"Approaching criticality (confidence {confidence:.0%}). "
            f"Evidence: {_evidence_str}. "
            "Measure ξ_r and ξ_τ near the candidate QCP to confirm or rule out criticality."
        )
    else:
        recommendation = (
            f"Subcritical (confidence {confidence:.0%}). "
            f"Evidence: {_evidence_str}. "
            "G and D primitives remain independent."
        )
    
    # At criticality ξ diverges by definition; use inf when not measured.
    # Only use 0 as default for explicitly sub-critical systems.
    _xi_default = float("inf") if is_critical else 0.0
    return CriticalityAnalysis(
        is_critical=is_critical,
        correlation_length=indicators.get("correlation_length", _xi_default),
        scaling_exponent=indicators.get("scaling_exponent"),
        universality_class=None,  # Requires more analysis
        confidence=confidence,
        indicators=indicators,
        recommendation=recommendation,
    )


def check_axiom5_criticality(
    imscription: Imscription,
    molecular_behavior: Optional[Dict[str, Any]] = None,
    supramolecular_behavior: Optional[Dict[str, Any]] = None,
    temporal_behavior: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Check Axiom 5: Criticality contracts the primitive basis.
    
    At criticality, molecular-scale behavior should predict supramolecular
    and temporal behavior without additional primitive information.
    
    Args:
        imscription: Imscription to analyze
        molecular_behavior: Behavior metrics at molecular scale
        supramolecular_behavior: Behavior metrics at supramolecular scale
        temporal_behavior: Behavior metrics at temporal scale
    
    Returns:
        Dict with axiom validation results
    """
    is_critical = imscription.criticality_phase == CriticalityPhase.CRITICAL
    
    if not is_critical:
        return {
            "axiom": "Axiom 5 (Criticality)",
            "applies": False,
            "reason": "Imscription not at criticality",
            "is_critical": False,
        }
    
    # At criticality, check if behaviors are consistent across scales
    if molecular_behavior and supramolecular_behavior:
        # Check if ξ_CP values are similar (within 20%)
        xi_mol = molecular_behavior.get("xi_CP", 0)
        xi_supra = supramolecular_behavior.get("xi_CP", 0)
        
        if xi_mol > 0 and xi_supra > 0:
            ratio = max(xi_mol, xi_supra) / min(xi_mol, xi_supra)
            cross_scale_consistent = ratio < 1.2
        else:
            cross_scale_consistent = False
        
        return {
            "axiom": "Axiom 5 (Criticality)",
            "applies": True,
            "is_critical": True,
            "cross_scale_consistent": cross_scale_consistent,
            "xi_molecular": xi_mol,
            "xi_supramolecular": xi_supra,
            "axiom_satisfied": cross_scale_consistent,
            "note": (
                "At criticality, molecular and supramolecular ξ_CP should be similar"
                if cross_scale_consistent
                else "Cross-scale inconsistency detected - may not be truly critical"
            ),
        }
    
    return {
        "axiom": "Axiom 5 (Criticality)",
        "applies": True,
        "is_critical": True,
        "requires_verification": True,
        "note": "Provide behavior data at multiple scales for full validation",
    }


def find_criticality_candidates(
    imscriptions: List[Imscription],
    min_confidence: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Find imscriptions that may be operating at or near criticality.
    
    Args:
        imscriptions: List of imscriptions to analyze
        min_confidence: Minimum confidence threshold
    
    Returns:
        List of criticality analysis results for candidates
    """
    candidates = []
    
    for imscription in imscriptions:
        analysis = analyze_criticality(imscription)
        
        if analysis.confidence >= min_confidence:
            candidates.append({
                "imscription_name": imscription.name,
                "analysis": analysis.to_dict(),
            })
    
    # Sort by confidence (descending)
    candidates.sort(key=lambda x: -x["analysis"]["confidence"])
    
    return candidates
