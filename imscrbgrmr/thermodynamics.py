"""
Thermodynamics — Constraint Propagation Efficiency and Inefficiency Index.

This module implements the thermodynamic metrics from QUANTIG.md:
- η_CP (Constraint Propagation Efficiency)
- ξ_CP (Inefficiency Index in nats)

These metrics quantify how effectively a imscription converts physical energy
expenditure into reliable information gain.

EXTENDED: Now includes kinetic fidelity computation (K primitive).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Union

from .models import Imscription, Fidelity, KineticCharacter


# =============================================================================
# Physical Constants
# =============================================================================

# Landauer cost per bit at 298 K (molar)
# E_bit = k_B * T * ln(2) * N_A
# k_B = 1.380649e-23 J/K
# T = 298 K
# N_A = 6.02214076e23 mol^-1
# E_bit_molar ≈ 1.72e-3 kJ/mol/bit
LANDAUER_COST_PER_BIT: float = 1.72e-3  # kJ/mol/bit


@dataclass
class ConstraintPropagationEfficiency:
    """
    Computes and stores constraint propagation efficiency metrics.
    
    η_CP = (I × F) / (ΔG / E_bit_molar)
    
    Where:
    - I = information gain (bits), estimated from configurational restriction
    - F = fidelity (0-1), normalized
    - ΔG = free energy cost (kJ/mol)
    - E_bit_molar ≈ 1.72×10^-3 kJ/mol/bit (Landauer cost at 298 K)
    
    ξ_CP = -ln(η_CP)  (inefficiency index in nats)
    
    η_CP = 1 represents perfect Landauer efficiency.
    Real chemical systems have η_CP << 1 due to irreversible overhead.
    """
    
    imscription_name: str
    information_gain: float  # bits
    fidelity: float  # 0-1
    delta_g: float  # kJ/mol (free energy cost)
    eta_CP: float  # efficiency
    xi_CP: float  # inefficiency index (nats)
    
    @property
    def waste_factor(self) -> float:
        """
        Return the waste factor (1/η_CP).
        
        Represents how many times more energy is used compared to
        the Landauer limit.
        """
        if self.eta_CP <= 0:
            return float('inf')
        return 1.0 / self.eta_CP
    
    @property
    def efficiency_description(self) -> str:
        """Return human-readable efficiency description."""
        if self.eta_CP >= 1e-3:
            return "Highly efficient (η_CP ≥ 10^-3)"
        elif self.eta_CP >= 1e-4:
            return "Moderately efficient (10^-4 ≤ η_CP < 10^-3)"
        elif self.eta_CP >= 1e-5:
            return "Typical efficiency (10^-5 ≤ η_CP < 10^-4)"
        elif self.eta_CP >= 1e-6:
            return "Low efficiency (10^-6 ≤ η_CP < 10^-5)"
        else:
            return "Very low efficiency (η_CP < 10^-6)"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "imscription_name": self.imscription_name,
            "information_gain_bits": self.information_gain,
            "fidelity": self.fidelity,
            "delta_g_kJ_mol": self.delta_g,
            "eta_CP": self.eta_CP,
            "xi_CP_nats": self.xi_CP,
            "waste_factor": self.waste_factor,
            "efficiency_description": self.efficiency_description,
        }
    
    def __str__(self) -> str:
        return (
            f"ConstraintPropagationEfficiency({self.imscription_name}): "
            f"η_CP = {self.eta_CP:.2e}, ξ_CP = {self.xi_CP:.2f} nats, "
            f"waste = {self.waste_factor:.1e}-fold"
        )


# =============================================================================
# Kinetic Fidelity Functions — NEW
# =============================================================================

def compute_kinetic_fidelity(
    delta_g_ddagger: float,
    k_cat: Optional[float] = None,
    k_side: Optional[float] = None,
    temperature: float = 298.0,
) -> Tuple[KineticCharacter, float]:
    """
    Compute kinetic fidelity from barrier height or rate constants.
    
    From QUANTIG.md Section III:
    - K_frtailgamma: ΔG‡ < 60 kJ/mol — spontaneous on experimental timescales
    - K_turnm: ΔG‡ ≈ 60-100 kJ/mol — accessible with mild activation
    - K_schwa: ΔG‡ > 100 kJ/mol — requires significant activation
    - K_teshlig: high pathway multiplicity — kinetic products diverge from thermodynamic
    
    Args:
        delta_g_ddagger: Activation barrier in kJ/mol
        k_cat: Catalytic rate constant (s^-1), optional
        k_side: Side reaction rate constant (s^-1), optional
        temperature: Temperature in Kelvin
    
    Returns:
        Tuple of (KineticCharacter, kinetic_fidelity_value)
    
    Example:
        >>> k_char, k_fid = compute_kinetic_fidelity(delta_g_ddagger=85.0)
        >>> print(f"K = {k_char.value}, F_kinetic = {k_fid:.3f}")
        K = K_turnm, F_kinetic = 0.700
    """
    # Assign K from barrier
    k_char = KineticCharacter.from_barrier(delta_g_ddagger)
    
    # Compute kinetic fidelity if rate constants available
    if k_cat is not None and k_side is not None:
        k_total = k_cat + k_side
        if k_total > 0:
            f_kinetic = k_cat / k_total
        else:
            f_kinetic = 0.0
    else:
        # Estimate from K character
        f_kinetic = k_char.numeric_value
    
    return k_char, f_kinetic


def compute_effective_fidelity(
    imscription: Imscription,
    delta_g_ddagger: Optional[float] = None,
    k_cat: Optional[float] = None,
    k_side: Optional[float] = None,
) -> float:
    """
    Compute effective fidelity combining thermodynamic and kinetic components.
    
    F_effective = F_thermo × F_kinetic
    
    This separation is required because a imscription can be thermodynamically
    favored (F_hardsign) yet kinetically inaccessible (K_schwa) under synthesis
    conditions (from QUANTIG.md Section III).
    
    Args:
        imscription: Imscription with F_thermo already assigned
        delta_g_ddagger: Optional barrier for kinetic computation
        k_cat, k_side: Optional rate constants
    
    Returns:
        Effective fidelity (0.0-1.0)
    
    Example:
        >>> imscription = Imscription(..., fidelity=Fidelity.peep, kinetic_character=KineticCharacter.loll)
        >>> f_eff = compute_effective_fidelity(imscription)
        >>> print(f"F_effective = {f_eff:.3f}")
    """
    f_thermo = imscription.fidelity.numeric_value
    
    if delta_g_ddagger is not None or (k_cat is not None and k_side is not None):
        _, f_kinetic = compute_kinetic_fidelity(
            delta_g_ddagger=delta_g_ddagger or 100.0,
            k_cat=k_cat,
            k_side=k_side,
        )
    else:
        # Use K primitive if available
        f_kinetic = imscription.kinetic_character.numeric_value
    
    return f_thermo * f_kinetic


def compute_information_gain(
    imscription: Imscription,
    num_coordinates: Optional[int] = None,
    method: str = "configurational",
) -> float:
    """
    Estimate information gain (I) in bits for a imscription.

    First checks the calibrated I lookup table (_CALIBRATED_I_BITS) from
    the Phase 1.1 DOF-counting pipeline.  Falls back to topology/granularity
    heuristics if not found.

    Default range: 6–11 bits (domain-dependent).
      Molecular dimers (2-HB):   6–10 bits
      Cooperativity arrays:      12–18 bits
      Temporal cycles:            6–9 bits/turn

    Methods:
    - "configurational": Calibrated lookup → coordinate-based heuristic
    - "fidelity_weighted": Based on fidelity and interaction strength
    - "topology_based": Based on topological complexity

    Args:
        imscription: The imscription to analyze
        num_coordinates: Number of coordinates restricted (default: estimated from G)
        method: Estimation method

    Returns:
        Information gain in bits (calibrated where available)
    """
    # --- Calibrated lookup (highest priority) ---
    if method == "configurational":
        calibrated = _CALIBRATED_I_BITS.get(imscription.name)
        if calibrated is not None:
            return calibrated

        # Heuristic fallback with updated coordinate scaling
        if num_coordinates is None:
            coord_map = {
                imscription.granularity.LOCAL: 2,
                imscription.granularity.MESOSCALE: 4,
                imscription.granularity.GLOBAL: 6,
            }
            num_coordinates = coord_map.get(imscription.granularity, 3)

        # Updated base: 3.5 bits/coord (previously 2.5) to reflect calibration
        base_bits = num_coordinates * 3.5

        topology_bonus = {
            imscription.topology.CYCLIC_BOWTIE: 1.5,
            imscription.topology.CHAIN: 0.5,
            imscription.topology.HUB_NODE: 2.0,
            imscription.topology.LINEAR: 0.0,
            imscription.topology.BRANCHED: 1.0,
            imscription.topology.NETWORK: 3.0,
            imscription.topology.CAGE: 2.5,
        }

        return base_bits + topology_bonus.get(imscription.topology, 0.5)

    elif method == "fidelity_weighted":
        base_bits = 6.0   # Updated base from calibration (was 4.0)
        return base_bits * imscription.fidelity.numeric_value

    elif method == "topology_based":
        return float(imscription.topology.complexity) * 1.5

    else:
        raise ValueError(f"Unknown method: {method}")


def compute_eta_CP(
    imscription: Imscription,
    delta_g: float,
    information_gain: Optional[float] = None,
    information_method: str = "configurational",
    use_effective_fidelity: bool = True,  # NEW parameter
    delta_g_ddagger: Optional[float] = None,  # NEW parameter
    k_cat: Optional[float] = None,  # NEW parameter
    k_side: Optional[float] = None,  # NEW parameter
) -> ConstraintPropagationEfficiency:
    """
    Compute constraint propagation efficiency (η_CP) for a imscription.
    
    EXTENDED: Now supports effective fidelity (F_thermo × F_kinetic).
    
    η_CP = (I × F_effective) / (ΔG / E_bit_molar)
    
    When use_effective_fidelity=True, F_effective = F_thermo × F_kinetic.
    This separation is required because a imscription can be thermodynamically
    favored (F_hardsign) yet kinetically inaccessible (K_schwa) under synthesis
    conditions (from QUANTIG.md Section III).

    Args:
        imscription: The imscription to analyze
        delta_g: Free energy cost (kJ/mol). Negative for favorable interactions.
        information_gain: Pre-computed information gain (bits). If None, estimated.
        information_method: Method for estimating information gain.
        use_effective_fidelity: If True, use F_thermo × F_kinetic (default: True)
        delta_g_ddagger: Optional barrier for kinetic fidelity computation
        k_cat, k_side: Optional rate constants for kinetic fidelity

    Returns:
        ConstraintPropagationEfficiency dataclass

    Example:
        >>> from imscrbgrmr import Imscription, ...
        >>> imscription = Imscription(...)  # carboxylic acid dimer
        >>> result = compute_eta_CP(imscription, delta_g=-64.2)
        >>> print(f"η_CP = {result.eta_CP:.2e}, ξ_CP = {result.xi_CP:.2f} nats")
    """
    # Use absolute value of ΔG (energy invested)
    delta_g_abs = abs(delta_g)

    # Estimate information gain if not provided
    if information_gain is None:
        information_gain = compute_information_gain(
            imscription, method=information_method
        )

    # Compute effective fidelity if requested
    if use_effective_fidelity:
        fidelity = compute_effective_fidelity(
            imscription,
            delta_g_ddagger=delta_g_ddagger,
            k_cat=k_cat,
            k_side=k_side,
        )
    else:
        # Use thermodynamic fidelity only
        fidelity = imscription.fidelity.numeric_value

    # Compute η_CP
    # Denominator: energy cost in units of Landauer bits
    denominator = delta_g_abs / LANDAUER_COST_PER_BIT

    if denominator <= 0:
        eta_CP = 0.0
    else:
        eta_CP = (information_gain * fidelity) / denominator

    # Compute ξ_CP (inefficiency index)
    if eta_CP <= 0:
        xi_CP = float('inf')
    else:
        xi_CP = -math.log(eta_CP)

    return ConstraintPropagationEfficiency(
        imscription_name=imscription.name,
        information_gain=information_gain,
        fidelity=fidelity,
        delta_g=delta_g,
        eta_CP=eta_CP,
        xi_CP=xi_CP,
    )


def compute_xi_CP(
    imscription: Imscription,
    delta_g: float,
    information_gain: Optional[float] = None,
) -> float:
    """
    Compute inefficiency index (ξ_CP) for a imscription.
    
    ξ_CP = -ln(η_CP)  (units: nats)
    
    This is a convenience function that returns just the ξ_CP value.
    
    Args:
        imscription: The imscription to analyze
        delta_g: Free energy cost (kJ/mol)
        information_gain: Pre-computed information gain (bits)
    
    Returns:
        Inefficiency index in nats
    
    Example values from QUANTIG.md:
    - Triple H-bond array: ξ_CP ≈ 7.1-7.6 nats (most efficient)
    - H-bond dimers: ξ_CP ≈ 8.3-10.5 nats
    - Temporal cycles: ξ_CP ≈ 9.9-11.4 nats
    - Zr-oxo proxies: ξ_CP ≈ 12.2-16.8 nats (least efficient)
    """
    result = compute_eta_CP(imscription, delta_g, information_gain)
    return result.xi_CP


def compare_efficiencies(
    imscriptions_with_energy: list[Tuple[Imscription, float]],
    information_method: str = "configurational",
) -> Dict[str, Any]:
    """
    Compare constraint propagation efficiencies across multiple imscriptions.
    
    Args:
        imscriptions_with_energy: List of (imscription, ΔG) tuples
        information_method: Method for estimating information gain
    
    Returns:
        Comparison report with rankings and statistics
    """
    results = []
    
    for imscription, delta_g in imscriptions_with_energy:
        result = compute_eta_CP(imscription, delta_g, information_method=information_method)
        results.append(result)
    
    # Sort by efficiency (descending)
    results.sort(key=lambda r: -r.eta_CP)
    
    # Compute statistics
    eta_values = [r.eta_CP for r in results]
    xi_values = [r.xi_CP for r in results if r.xi_CP != float('inf')]
    
    return {
        "num_imscriptions": len(results),
        "rankings": [
            {
                "rank": i + 1,
                "imscription": r.imscription_name,
                "eta_CP": r.eta_CP,
                "xi_CP": r.xi_CP,
                "waste_factor": r.waste_factor,
                "description": r.efficiency_description,
            }
            for i, r in enumerate(results)
        ],
        "statistics": {
            "eta_CP": {
                "min": min(eta_values),
                "max": max(eta_values),
                "mean": sum(eta_values) / len(eta_values),
            },
            "xi_CP": {
                "min": min(xi_values),
                "max": max(xi_values),
                "mean": sum(xi_values) / len(xi_values),
            },
        },
        "most_efficient": results[0].imscription_name if results else None,
        "least_efficient": results[-1].imscription_name if results else None,
    }


def benchmark_against_landauer(
    imscription: Imscription,
    delta_g: float,
) -> Dict[str, Any]:
    """
    Benchmark a imscription's efficiency against the Landauer limit.
    
    The Landauer limit represents the minimum possible energy cost
    per bit of information processing: E_bit = k_B T ln(2).
    
    Args:
        imscription: The imscription to benchmark
        delta_g: Free energy cost (kJ/mol)
    
    Returns:
        Benchmark report
    """
    result = compute_eta_CP(imscription, delta_g)
    
    # Compute theoretical minimum energy
    min_energy = result.information_gain * LANDAUER_COST_PER_BIT
    
    # Actual energy used
    actual_energy = abs(delta_g)
    
    # Overhead ratio
    overhead = actual_energy / min_energy if min_energy > 0 else float('inf')
    
    return {
        "imscription": imscription.name,
        "information_gain_bits": result.information_gain,
        "landauer_minimum_kJ_mol": min_energy,
        "actual_energy_kJ_mol": actual_energy,
        "overhead_ratio": overhead,
        "efficiency_eta_CP": result.eta_CP,
        "inefficiency_xi_CP": result.xi_CP,
        "waste_nats": result.xi_CP,
        "interpretation": (
            f"This imscription uses {overhead:.1f}× more energy than the "
            f"Landauer limit, corresponding to {result.xi_CP:.2f} nats "
            f"of wasted information per bit gained."
        ),
    }


# =============================================================================
# Calibrated I(bits) values — from Phase 1.1 DOF-counting pipeline
# These replace the prior 4–6 bit heuristic range.
# =============================================================================

_CALIBRATED_I_BITS: Dict[str, float] = {
    # Molecular domain — H-bond dimers
    "carboxylic_acid_homodimer":   9.4,   # 2-HB R²₂(8), DOF counting (vacuum)
    "acetic_acid_homodimer":       9.4,   # same motif
    "acid_amide_heterodimer":      8.2,   # 2-HB directed, lower corr. factor
    "formamide_homodimer":         6.8,   # weak 2-HB, loose geometry
    # Supramolecular domain — cooperativity
    "triple_hbond_array":         16.0,   # DAD·ADA, ×1.25 cooperativity
    "triple_hbond_DAD_ADA_array": 16.0,   # same
    # Temporal domain — catalytic cycles
    "proline_aldol_cycle":         7.5,   # 2 stereocontrol contacts × 0.85
    # σ-hole series (halogen bonds — narrower angle window ±20°)
    "iodopentafluorobenzene_dimer": 7.8,  # C-I···N, 1 contact, tight geometry
    "sigma_hole_dimer":             7.8,
    "sigma_hole_trimer":           11.2,  # 3 σ-holes, no cooperativity
}

# Uncertainty band in nats on ξ_CP arising from I calibration
_XI_CP_UNCERTAINTY_NATS: float = 1.5   # ±1.5 nats covers the calibration range


@dataclass
class CalibratedXiCPEntry:
    """
    Revised ξ_CP entry using per-system calibrated I(bits).

    Includes uncertainty band (±1–2 nats) from I calibration.
    """
    imscription_name: str
    I_calibrated_bits: float       # from _CALIBRATED_I_BITS or DOF counting
    I_uncertainty_bits: float      # ±range on calibrated I
    delta_g: float                 # kJ/mol
    fidelity: float                # 0–1
    eta_CP: float
    xi_CP: float
    xi_CP_low: float               # ξ_CP at I + I_uncertainty
    xi_CP_high: float              # ξ_CP at I – I_uncertainty (less info → worse)
    fidelity_tier: str             # "HIGH" | "MEDIUM" | "LOW"
    tier_changed: bool = False     # True if this tier differs from pre-calibration tier

    def to_dict(self) -> Dict[str, Any]:
        return {
            "imscription": self.imscription_name,
            "I_calibrated_bits": round(self.I_calibrated_bits, 3),
            "I_uncertainty_bits": round(self.I_uncertainty_bits, 3),
            "delta_g_kJ_mol": self.delta_g,
            "fidelity": round(self.fidelity, 3),
            "eta_CP": f"{self.eta_CP:.2e}",
            "xi_CP_nats": round(self.xi_CP, 2),
            "xi_CP_range": [round(self.xi_CP_low, 2), round(self.xi_CP_high, 2)],
            "fidelity_tier": self.fidelity_tier,
            "tier_changed": self.tier_changed,
        }


def _xi_from_I(
    I_bits: float,
    fidelity: float,
    delta_g: float,
) -> float:
    """Compute ξ_CP = –ln(η_CP) = –ln(I × F / (|ΔG| / E_bit))."""
    denom = abs(delta_g) / LANDAUER_COST_PER_BIT
    if denom <= 0 or I_bits <= 0 or fidelity <= 0:
        return float("inf")
    eta = (I_bits * fidelity) / denom
    return -math.log(eta)


def _fidelity_tier_from_xi(xi: float) -> str:
    """Assign fidelity tier from ξ_CP value."""
    if xi <= 8.5:
        return "HIGH"
    elif xi <= 11.0:
        return "MEDIUM"
    else:
        return "LOW"


def calibrated_xi_cp_table() -> Dict[str, CalibratedXiCPEntry]:
    """
    Recompute ξ_CP table using per-system calibrated I(bits) values.

    Covers:
    - Triple H-bond array (cooperative)
    - Proline aldol cycle (temporal)
    - Acid dimer series (2-HB molecular)
    - σ-hole series (halogen bond molecular)

    Returns:
        Dict[name, CalibratedXiCPEntry] with revised ξ_CP and ±1.5 nat bands
    """
    # Reference energy costs and fidelities from REFERENCE_VALUES
    # ΔG values from Grok literature survey (v2.2 correction, March 2026).
    # CRITICAL: prior values (−52, −95, −32 kJ/mol) were ΔE or ΔH, NOT ΔG.
    # Real ΔG at 298 K is much smaller due to entropic penalty for association.
    # acid_amide and formamide are flagged (*) as likely ΔH-not-ΔG — no lit
    # correction available yet; ITC measurement required to verify.
    # Proline: Houk group studies bracket ΔG‡ at 92–100 kJ/mol; using 97 kJ/mol.
    _params: List[Tuple[str, float, float]] = [
        # (name, delta_g kJ/mol, fidelity)
        # ΔG source noted in comment
        ("acetic_acid_homodimer",        -12.0,  0.95),   # lit ΔG(gas,298K); was −52 (ΔE) — corrected
        ("acid_amide_heterodimer",        -38.0,  0.75),   # * likely ΔH not ΔG; ITC needed
        ("formamide_homodimer",           -28.0,  0.40),   # * likely ΔH not ΔG; ITC needed
        ("triple_hbond_array",            -55.0,  0.95),   # lit ΔG(gas,298K) est; was −95 (ΔE) — corrected
        ("proline_aldol_cycle",            97.0,  0.75),   # ΔG‡; Houk studies 92–100; was 85 — corrected
        ("iodopentafluorobenzene_dimer",  -20.0,  0.75),   # ΔG(CHCl3 est); was −32 (ΔE) — corrected
        ("sigma_hole_dimer",              -20.0,  0.75),   # ΔG(CHCl3 est); was −32 (ΔE) — corrected
        ("sigma_hole_trimer",             -64.0,  0.75),   # no correction yet; ΔE/ΔH uncertain
    ]
    # Pre-calibration ξ_CP (I = 4–6 bits, used only to detect tier changes)
    _pre_calib_I = 5.0  # midpoint of old 4–6 range

    table: Dict[str, CalibratedXiCPEntry] = {}
    for name, dg, f in _params:
        I_cal = _CALIBRATED_I_BITS.get(name, 8.0)   # 8 bits generic fallback
        I_unc = 1.0                                   # ±1 bit calibration uncertainty

        xi_central = _xi_from_I(I_cal, f, dg)
        xi_low     = _xi_from_I(I_cal + I_unc, f, dg)   # better I → lower ξ
        xi_high    = _xi_from_I(I_cal - I_unc, f, dg)   # worse I → higher ξ

        tier_now  = _fidelity_tier_from_xi(xi_central)
        xi_old    = _xi_from_I(_pre_calib_I, f, dg)
        tier_old  = _fidelity_tier_from_xi(xi_old)

        table[name] = CalibratedXiCPEntry(
            imscription_name=name,
            I_calibrated_bits=I_cal,
            I_uncertainty_bits=I_unc,
            delta_g=dg,
            fidelity=f,
            eta_CP=math.exp(-xi_central) if xi_central != float("inf") else 0.0,
            xi_CP=xi_central,
            xi_CP_low=xi_low,
            xi_CP_high=xi_high,
            fidelity_tier=tier_now,
            tier_changed=(tier_now != tier_old),
        )
    return table


def audit_fidelity_tiers(
    catalog,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Re-run fidelity tier assignments with calibrated ξ_CP values.

    Iterates all catalog entries and re-derives their fidelity tier from
    ξ_CP using the calibrated I table.  Reports how many change.

    Args:
        catalog: ImscriptionCatalog instance
        verbose: If True, list all changed entries

    Returns:
        Dict with total, changed, pct_changed, changed_entries list
    """
    xi_table = calibrated_xi_cp_table()
    total = 0
    changed: List[str] = []

    for imscription in catalog:
        total += 1
        entry = xi_table.get(imscription.name)
        if entry and entry.tier_changed:
            changed.append(imscription.name)

    pct = (len(changed) / total * 100) if total > 0 else 0.0
    result: Dict[str, Any] = {
        "total_entries": total,
        "changed_tier": len(changed),
        "pct_changed": round(pct, 1),
        "stable_target": "≤5% reassignments",
        "stable": pct <= 5.0,
    }
    if verbose:
        result["changed_entries"] = changed
    return result


# =============================================================================
# Pre-computed reference values from QUANTIG.md
# =============================================================================

REFERENCE_VALUES: Dict[str, Dict[str, Any]] = {
    # Molecular domain - H-bond dimers (Transformation #1)
    # NOTE v2.2 correction: prior delta_g values were ΔE (electronic energy), not ΔG.
    # Real ΔG(298K) is much smaller; corrected values marked with [corrected].
    "acetic_acid_homodimer": {
        "eta_CP": (1e-3, 2e-3),          # recalculated with ΔG = −12 kJ/mol
        "xi_CP": (6.4, 7.0),             # 6.66 nats central; was 8.3–8.7 (ΔE artefact)
        "delta_g": -12,                  # kJ/mol ΔG(gas, 298K) [corrected; was −52 (ΔE)]
        "delta_e": -52,                  # kJ/mol ΔE (electronic binding energy, no thermal)
        "fidelity": "ƒ_hardsign",
        "geometry": {
            "OO_distance_ang": 2.675,    # Å, midpoint of 2.65–2.70 Å lit range
            "OH_O_angle_deg":  177.5,    # °, midpoint of 175–180°
            "OH_stretch_shift_cm": -400, # cm⁻¹ red-shift from monomer O-H stretch
        },
        "note": "R²₂(8) motif, P_± self-complementary; ΔG corrected from ΔE (Grok lit survey)",
    },
    "acid_amide_heterodimer": {
        "eta_CP": (1e-4, 2e-4),
        "xi_CP": (8.1, 8.4),             # recalculated with I_cal=8.2
        "delta_g": -38,                  # kJ/mol — likely ΔH not ΔG; ITC needed to verify
        "fidelity": "ƒ_dh",
        "note": "P_+- directional; delta_g may be ΔH not ΔG — flagged for ITC verification",
    },
    "formamide_homodimer": {
        "eta_CP": (5e-5, 9e-5),
        "xi_CP": (10.0, 10.5),
        "delta_g": -28,                  # kJ/mol — likely ΔH not ΔG; ITC needed to verify
        "fidelity": "ƒ_beltl",
        "note": "Lowest F in series, weak P_±; delta_g may be ΔH not ΔG — flagged",
    },

    # Supramolecular domain - Cooperativity (Transformation #5)
    "triple_hbond_array": {
        "eta_CP": (4e-4, 5e-4),          # recalculated with ΔG = −55 kJ/mol
        "xi_CP": (7.5, 7.9),             # 7.65 nats central; was 7.1–7.6 (ΔE artefact)
        "delta_g": -55,                  # kJ/mol ΔG(gas, 298K) est. [corrected; was −95 (ΔE)]
        "delta_e": -95,                  # kJ/mol ΔE (electronic binding energy)
        "fidelity": "ƒ_hardsign",
        "geometry": {
            "HB_distances_ang":  [1.80, 1.90, 1.80],  # three contacts; central slightly longer
            "HB_angles_deg":     [170, 163, 170],       # outer tighter than central
        },
        "cooperativity_factor": 1.25,    # confirmed by Grok: lit range 1.2–1.4
        "cooperativity_note": "Lit cooperativity ratio 1.2–1.4 vs 3× single HB; confirms Axiom 3 superlinear induction",
        "note": "DAD·ADA array; ΔG corrected from ΔE (Grok lit survey)",
    },

    # Temporal domain - Catalytic cycle (Transformation #6)
    "proline_aldol_cycle": {
        "eta_CP": (8e-5, 1.2e-4),        # recalculated with ΔG‡ = 97 kJ/mol
        "xi_CP": (9.0, 9.5),             # 9.21 nats central; was 9.9–11.4
        "delta_g": 97,                   # kJ/mol ΔG‡ (operative barrier) [corrected; was 85]
        "delta_g_range": (92, 100),      # kJ/mol — Houk group bracket from multiple substrates
        "fidelity": "ƒ_dh",
        "geometry": {
            "NH_O_distance_ang": 1.825,  # Å, midpoint of 1.75–1.90 Å in TS
            "CC_forming_ang":    2.1,    # Å, midpoint of 2.0–2.2 Å in TS
            "TS_imag_freq_cm":   400,    # cm⁻¹ typical C–C forming mode
        },
        "ee_prediction": {
            "delta_delta_g_kJ":  (5.0, 8.0),   # kJ/mol ΔΔG‡ from Houk studies
            "ee_predicted_pct":  (70, 85),       # % predicted; exp. benchmark = 74%
            "ee_experimental":   74,             # % (4-nitrobenzaldehyde + acetone in DMSO)
        },
        "note": "Houk-List TS; ΔG‡ corrected to 97 kJ/mol (was 85); ee prediction in range",
    },
    
    # σ-hole series — halogen bond (Transformation #7)
    "sigma_hole_dimer": {
        "eta_CP": (4e-4, 6e-4),          # recalculated with ΔG = −20 kJ/mol (CHCl3 est.)
        "xi_CP": (7.4, 7.8),             # 7.59 nats central; was 8.06–8.40 (ΔE artefact)
        "delta_g": -20,                  # kJ/mol ΔG(CHCl3 est.) [corrected; was −32 (ΔE)]
        "delta_e": -32,                  # kJ/mol ΔE
        "fidelity": "ƒ_dh",
        "geometry": {
            "IN_distance_ang":   2.875,  # Å, midpoint of 2.80–2.95 Å lit range
            "CI_N_angle_deg":    177.5,  # °, midpoint of 176–179° (highly directional)
            "Vs_max_kJ_mol":     175,    # kJ/mol V_s,max on I (σ-hole depth); lit 160–190
        },
        "note": "C6F5I···NMe3/Py model; ΔG corrected from ΔE (Grok lit survey)",
    },
    "sigma_hole_trimer": {
        "eta_CP": (2e-4, 3e-4),
        "xi_CP": (8.3, 8.5),             # 8.40 nats with −64 kJ/mol (no correction applied)
        "delta_g": -64,                  # kJ/mol — uncertain ΔE vs ΔG; flagged for correction
        "fidelity": "ƒ_dh",
        "note": "3 σ-holes, no cooperativity; delta_g may be ΔE not ΔG — flagged",
    },

    # Early framework proxies
    "zr_oxo_base_triplet": {
        "eta_CP": 5e-6,
        "xi_CP": 12.2,
        "note": "Early framework proxy",
    },
    "zr_oxo_singlet_tight": {
        "eta_CP": 3e-7,
        "xi_CP": 15.0,
        "note": "High geometric strain",
    },
    "zr_oxo_toluene_confined": {
        "eta_CP": 5e-8,
        "xi_CP": 16.8,
        "note": "Confinement overhead",
    },
    
    # Transformation #8 - Mechanical bond (planned)
    "rotaxane_dethreading": {
        "eta_CP": None,  # To be computed
        "xi_CP": None,  # To be computed
        "delta_g_ddagger": (60, 125),  # kJ/mol (dethreading barrier)
        "fidelity": "ƒ_dh",
        "kinetic_character": "Ç_turnm",
        "recognition_mode": "Ř_mechanical",
        "note": "DB24C8/dialkylammonium pseudorotaxane - planned Transformation #8",
        "criticality_probe": True,  # Examine for near-critical topology
    },
    
    # Criticality reference (theoretical)
    "critical_hbond_percolation": {
        "eta_CP": None,
        "xi_CP": None,
        "correlation_length": "divergent",
        "scaling_exponent": "to be determined",
        "note": "H-bond array near percolation threshold - candidate critical system",
        "criticality_phase": "⊙_ctyogh",
    },
}


def get_reference(imscription_name: str) -> Optional[Dict[str, Any]]:
    """
    Get reference η_CP/ξ_CP values from QUANTIG.md.
    
    Args:
        imscription_name: Name of the imscription
    
    Returns:
        Reference data dict or None if not found
    """
    return REFERENCE_VALUES.get(imscription_name)


def list_references() -> list[str]:
    """Return list of all reference imscription names."""
    return list(REFERENCE_VALUES.keys())
