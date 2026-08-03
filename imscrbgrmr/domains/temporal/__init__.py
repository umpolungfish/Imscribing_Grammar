"""
Temporal Domain — Imscription agents for oscillatory reactions and catalytic cycles.

This module implements agents for analyzing temporal imscriptions
in the context of dynamic chemical systems.
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional

from imscrbgrmr.models import (
    Imscription,
    Dimensionality,
    Topology,
    RecognitionMode,
    Polarity,
    Fidelity,
    Granularity,
    InteractionGrammar,
    KineticCharacter,  # NEW
)

__all__ = ["TemporalImscriptionAgent"]


class TemporalImscriptionAgent:
    """
    Agent for analyzing temporal imscriptions in oscillatory chemical systems.
    
    Temporal imscriptions operate with D_infinity (1D temporal periodicity)
    and typically involve R_downstep (dynamic/catalytic) recognition modes.
    
    Capabilities:
    - Reaction cycle mapping (stationary points, transition states)
    - Fidelity-per-cycle computation (k_cat / (k_cat + k_side))
    - Barrier profile analysis
    - BZ oscillation pattern detection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def analyze_reaction_cycle(
        self,
        cycle_name: str,
        catalyst: str,
    ) -> Dict[str, Any]:
        """
        Map a catalytic cycle's stationary points.
        
        Args:
            cycle_name: Name of the cycle (e.g., "proline_aldol")
            catalyst: Catalyst identifier (e.g., "L-proline")
        
        Returns:
            Cycle analysis with stationary points and barriers
        """
        # Known catalytic cycles from QUANTIG.md
        known_cycles = {
            "proline_aldol": {
                "num_stationary_points": 4,
                "points": [
                    "free_proline + aldehyde",
                    "carbinolamine intermediate",
                    "enamine intermediate",
                    "C-C bond-forming TS (rate-determining)",
                ],
                "barrier_kJ_mol": 85-100,  # M06-2X/6-31+G(d,p) CPCM(DMSO)
                "fidelity_per_cycle": 0.999-0.9999,
            },
            "bz_reaction": {
                "num_stationary_points": 12,  # FKN mechanism
                "oscillation_period": "variable",
                "mechanism": "Field-Körös-Noyes",
            },
        }
        
        cycle_data = known_cycles.get(cycle_name, {
            "num_stationary_points": "unknown",
            "barrier_kJ_mol": "unknown",
        })
        
        return {
            "cycle_name": cycle_name,
            "catalyst": catalyst,
            **cycle_data,
            "dimensionality": "𐑼",
            "recognition_mode": "Ř_downstep",
        }
    
    def compute_fidelity_per_cycle(
        self,
        k_cat: float,
        k_side: float,
    ) -> Dict[str, Any]:
        """
        Compute fidelity per cycle for a catalytic process.
        
        F_cycle = k_cat / (k_cat + k_side)
        
        Based on Transformation #6 from QUANTIG.md:
        - Proline aldol: F_cycle ≈ 0.999-0.9999 (F_dh)
        
        Args:
            k_cat: Catalytic rate constant (s^-1)
            k_side: Side reaction rate constant (s^-1)
        
        Returns:
            Fidelity analysis with numeric and enum values
        """
        if k_cat + k_side <= 0:
            return {"error": "Invalid rate constants"}
        
        f_cycle = k_cat / (k_cat + k_side)
        
        # Map to Fidelity enum
        if f_cycle >= 0.95:
            fidelity_enum = Fidelity.peep
        elif f_cycle >= 0.60:
            fidelity_enum = Fidelity.they
        else:
            fidelity_enum = Fidelity.age
        
        # Compute ξ_CP for temporal imscription
        # Using typical barrier height for estimation
        delta_g_approx = 85  # kJ/mol (proline aldol reference)
        from imscrbgrmr.thermodynamics import compute_xi_CP

        # Create a minimal imscription for calculation
        temporal_imscription = Imscription(
            name="temporal_cycle",
            dimensionality=Dimensionality.array,
            topology=Topology.mime,
            recognition_mode=RecognitionMode.ear,
            polarity=Polarity.church,
            fidelity=fidelity_enum,
            kinetic_character=KineticCharacter.loll,
            granularity=Granularity.bib,
            interaction_grammar=InteractionGrammar.measure,
        )

        xi_cp = compute_xi_CP(temporal_imscription, delta_g_approx)

        return {
            "k_cat": k_cat,
            "k_side": k_side,
            "f_cycle": f_cycle,
            "fidelity_enum": fidelity_enum.value,
            "xi_CP_nats": xi_cp,
            "interpretation": (
                f"High fidelity temporal imscription (F ≈ {f_cycle:.4f})"
                if f_cycle >= 0.99
                else f"Medium fidelity temporal imscription (F ≈ {f_cycle:.3f})"
            ),
        }

    def get_barrier_profile(
        self,
        cycle_name: str,
    ) -> Dict[str, Any]:
        """
        Get barrier profile for a catalytic cycle.
        
        Args:
            cycle_name: Name of the cycle
        
        Returns:
            Barrier heights for each step
        """
        # Literature benchmark barriers
        barrier_profiles = {
            "proline_aldol": {
                "step_1_enamine_formation": 60-80,  # kJ/mol
                "step_2_cc_bond_formation": 85-100,  # Rate-determining
                "step_3_hydrolysis": 40-60,
                "overall_barrier": 85-100,
                "method": "M06-2X/6-31+G(d,p) CPCM(DMSO)",
            },
        }
        
        return barrier_profiles.get(cycle_name, {
            "error": f"Unknown cycle: {cycle_name}",
        })
    
    def detect_bz_oscillations(
        self,
        time_series: List[float],
        sampling_interval: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Detect Belousov-Zhabotinsky-type oscillations in time series data.
        
        Args:
            time_series: Concentration or absorbance measurements
            sampling_interval: Time between samples (seconds)
        
        Returns:
            Oscillation analysis with period and amplitude
        """
        if len(time_series) < 10:
            return {"error": "Insufficient data points"}
        
        # Simple peak detection
        peaks = []
        troughs = []
        
        for i in range(1, len(time_series) - 1):
            if time_series[i] > time_series[i-1] and time_series[i] > time_series[i+1]:
                peaks.append(i)
            elif time_series[i] < time_series[i-1] and time_series[i] < time_series[i+1]:
                troughs.append(i)
        
        if len(peaks) < 2:
            return {
                "is_oscillatory": False,
                "note": "No clear oscillations detected",
            }
        
        # Compute period
        periods = [
            (peaks[i+1] - peaks[i]) * sampling_interval
            for i in range(len(peaks) - 1)
        ]
        avg_period = sum(periods) / len(periods)
        
        # Compute amplitude
        amplitudes = [
            time_series[p] - time_series[t]
            for p, t in zip(peaks, troughs)
            if p > t
        ]
        avg_amplitude = sum(amplitudes) / len(amplitudes) if amplitudes else 0
        
        return {
            "is_oscillatory": True,
            "num_cycles": len(peaks),
            "period_seconds": avg_period,
            "amplitude": avg_amplitude,
            "imscription_type": "𐑼_temporal",
        }
    
    def to_imscription(
        self,
        cycle_name: str,
        fidelity: Fidelity = Fidelity.they,
    ) -> Imscription:
        """
        Create a temporal imscription from a catalytic cycle.
        
        Args:
            cycle_name: Name of the cycle
            fidelity: Fidelity level (default: MEDIUM)
        
        Returns:
            Imscription object
        """
        from imscrbgrmr.models import CriticalityPhase
        
        return Imscription(
            name=cycle_name,
            dimensionality=Dimensionality.array,
            topology=Topology.mime,
            recognition_mode=RecognitionMode.ear,
            polarity=Polarity.church,
            fidelity=fidelity,
            kinetic_character=KineticCharacter.loll,
            granularity=Granularity.bib,
            interaction_grammar=InteractionGrammar.measure,
            criticality_phase=CriticalityPhase.woe,
            description=f"Temporal imscription: {cycle_name} cycle",
            metadata={"cycle_type": "catalytic"},
        )
