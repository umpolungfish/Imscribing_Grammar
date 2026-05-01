"""
Varma quantum XY criticality probe.

Checks whether the correlation form ξ_r ≈ ln ξ_τ (from Varma/Zhu/Hou)
implies G/D degeneracy (Axiom 5 tuple contraction) and scores Φ_c candidacy.

Background
----------
The quantum XY critical point (Varma universality class) exhibits marginal
Fermi-liquid behavior with an anomalous temporal correlation:

    C(τ) ~ 1/τ   (marginal, unlike conventional ω^(2-η) behavior)

and the correlation lengths are related by:

    ξ_r ≈ ln ξ_τ

This is in contrast to conventional criticality where ξ_r ~ ξ_τ^(1/z)
with dynamic exponent z ≈ 1–2.

Axiom 5 implications
--------------------
Axiom 5 (Criticality contracts the primitive basis): at criticality, G
becomes redundant given D. The Varma QXY satisfies this in a WEAK form:

    ξ_r is DETERMINED by ξ_τ via ln — so G cannot be assigned independently
    of D. The tuple contracts from ⟨D; G⟩ to ⟨D; Φ_c⟩.

However, the degeneracy is logarithmic, not power-law. This means:
    - The system qualifies for Φ_c assignment.
    - The standard G/D scale-free universality (where ξ_r ~ ξ_τ) does NOT apply.
    - A new qualifier "log-degenerate" should be noted in the entry.

Scaling prediction
------------------
Near the QCP (δ = distance from critical point → 0):
    ξ_τ ~ exp(π / √δ)   [exponential divergence, Kosterlitz-Thouless-like]
    ξ_r ~ ln ξ_τ ~ π / √δ   [power-law divergence in spatial scale]
    ξ_r ≈ π × (ln ξ_τ / π) = ln ξ_τ  [confirming the logarithmic relation]

Universality class: Varma QXY / marginal Fermi liquid.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional, Any, Tuple

from .models import Synthon, CriticalityPhase, Granularity, Dimensionality, Fidelity, KineticCharacter

if TYPE_CHECKING:
    from .morphism import TransitionMorphism


@dataclass
class VarmaCorrelationData:
    """
    Input correlation data for the Varma probe.

    xi_r:  spatial correlation length (in units of the lattice constant)
    xi_tau: temporal correlation length (in units of 1/ω_c, the cutoff frequency)
    delta:  distance from QCP (0 = exactly critical, >0 = off-critical)
    """
    xi_r: Optional[float] = None
    xi_tau: Optional[float] = None
    delta: Optional[float] = None  # distance from QCP
    additional_exponents: Dict[str, float] = field(default_factory=dict)


@dataclass
class PhiCCandidacyReport:
    """
    Φ_c candidacy score and breakdown for a synthon.

    score:       0.0–1.0; ≥0.7 → Φ_c, 0.4–0.7 → approaching, <0.4 → subcritical
    gd_degenerate: True if G and D are functionally coupled (cannot be independently set)
    axiom5_satisfied: True if Axiom 5 (tuple contraction) is satisfied
    universality_class: "Varma_QXY" | "standard_QCP" | None
    scaling_prediction: predictions for ξ_r from ξ_τ
    flags: list of Axiom violation or warning strings
    """
    synthon_name: str
    score: float = 0.0
    gd_degenerate: bool = False
    gd_degeneracy_type: str = "none"  # "logarithmic" | "power_law" | "none"
    axiom5_satisfied: bool = False
    axiom5_note: str = ""
    universality_class: Optional[str] = None
    scaling_prediction: Dict[str, Any] = field(default_factory=dict)
    contributing_factors: List[Dict[str, Any]] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "synthon": self.synthon_name,
            "phi_c_score": round(self.score, 3),
            "phi_c_candidacy": self._candidacy_label(),
            "gd_degenerate": self.gd_degenerate,
            "gd_degeneracy_type": self.gd_degeneracy_type,
            "axiom5_satisfied": self.axiom5_satisfied,
            "axiom5_note": self.axiom5_note,
            "universality_class": self.universality_class,
            "scaling_prediction": self.scaling_prediction,
            "contributing_factors": self.contributing_factors,
            "flags": self.flags,
            "recommendation": self.recommendation,
        }

    def _candidacy_label(self) -> str:
        if self.score >= 0.70:
            return "Φ_c (critical)"
        elif self.score >= 0.40:
            return "approaching Φ_c"
        else:
            return "Φ_sub (subcritical)"


def compute_dynamic_exponent(
    xi_r_omega: float,
    xi_tau_omega: float,
) -> float:
    """
    Compute the effective dynamic exponent z_eff(ω) at frequency ω.

        z_eff(ω) = ln ξ_τ(ω) / ln ξ_r(ω)

    In conventional criticality z_eff is finite and constant (z ≈ 1–2).
    In the Varma QXY universality class, z_eff diverges logarithmically as
    ω → 0 (ξ_τ grows exponentially while ξ_r grows algebraically):

        z_eff(ω) → ∞  as  ξ_r → ∞,  ξ_τ → exp(ξ_r)

    This divergence is the defining G/D degeneracy signature of Axiom 5.

    Args:
        xi_r_omega:   Spatial correlation length at frequency ω (lattice units)
        xi_tau_omega: Temporal correlation length at frequency ω (1/ω_c units)

    Returns:
        z_eff — float, or +∞ when ξ_r → 1 (logarithmic limit)
    """
    if xi_r_omega <= 1.0 or xi_tau_omega <= 1.0:
        return float("inf")
    ln_xi_r   = math.log(xi_r_omega)
    ln_xi_tau = math.log(xi_tau_omega)
    if ln_xi_r <= 0:
        return float("inf")
    return ln_xi_tau / ln_xi_r


def degeneracy_strength(
    synthon: "Synthon",
    correlation_data: Optional["VarmaCorrelationData"] = None,
    frequency_series: Optional[List[Tuple[float, float]]] = None,
) -> Tuple[float, str]:
    """
    Quantitative G/D degeneracy strength score (0–1) for a synthon.

    Score tiers:
      0.00–0.30 : no degeneracy     — G and D fully independent
      0.30–0.60 : logarithmic       — weak Varma QXY (ξ_r ≈ ln ξ_τ)
      0.60–0.85 : power-law         — conventional QCP with finite z
      0.85–1.00 : direct collapse   — strong Axiom 5 (G/D identity)

    The score is computed from:
      1. Varma QXY ratio check (ξ_r / ln ξ_τ ≈ 1)  → 0.0–0.55
      2. Dynamic exponent divergence (z_eff → ∞)    → bonus up to +0.20
      3. Tuple structure priors (D_∞, R_‡, Φ_c)    → bonus up to +0.15
      4. Frequency-series z_eff trend (optional)    → bonus up to +0.10

    Args:
        synthon: Synthon to evaluate
        correlation_data: Optional single-frequency ξ_r, ξ_τ measurement
        frequency_series: Optional list of (ξ_r(ω_i), ξ_τ(ω_i)) pairs across
                          decreasing frequencies; used to detect z_eff → ∞ trend

    Returns:
        (score, tier_label)
    """
    score = 0.0

    # --- Component 1: ξ_r / ln ξ_τ ratio ---
    if correlation_data and correlation_data.xi_r and correlation_data.xi_tau:
        is_log, ratio = check_logarithmic_scaling(
            correlation_data.xi_r, correlation_data.xi_tau
        )
        if is_log:
            score += 0.55  # strong Varma log-degeneracy
        else:
            # Check power-law degeneracy: z_eff finite ≈ 1–2
            z_eff = compute_dynamic_exponent(
                correlation_data.xi_r, correlation_data.xi_tau
            )
            if not math.isinf(z_eff):
                if 0.8 <= z_eff <= 2.5:
                    score += 0.45  # power-law QCP regime
                elif z_eff > 2.5:
                    score += 0.25  # some coupling but not canonical QCP
                else:
                    score += 0.10  # weak coupling

    # --- Component 2: z_eff divergence bonus from frequency series ---
    if frequency_series and len(frequency_series) >= 2:
        z_series = []
        for xi_r_i, xi_tau_i in frequency_series:
            z_i = compute_dynamic_exponent(xi_r_i, xi_tau_i)
            if not math.isinf(z_i):
                z_series.append(z_i)
        if len(z_series) >= 2 and z_series[-1] > z_series[0]:
            # z_eff growing with decreasing frequency → logarithmic divergence
            growth = (z_series[-1] - z_series[0]) / max(1.0, z_series[0])
            bonus = min(0.20, growth * 0.10)
            score += bonus

    # --- Component 3: Tuple structure priors ---
    from .models import RecognitionMode, Dimensionality
    tuple_bonus = 0.0
    if "temporal" in synthon.dimensionality.domains:
        tuple_bonus += 0.05
    if synthon.recognition_mode in {
        RecognitionMode.DYNAMIC_CATALYTIC, RecognitionMode.COVALENT_DYNAMIC
    }:
        tuple_bonus += 0.05
    if synthon.criticality_phase is not None and synthon.criticality_phase.value == "Phi_c":
        tuple_bonus += 0.05
    score += min(0.15, tuple_bonus)

    score = min(1.0, score)

    # --- Classify tier ---
    if score >= 0.85:
        tier = "collapse"       # direct G/D collapse
    elif score >= 0.60:
        tier = "power-law"      # finite z, conventional QCP
    elif score >= 0.30:
        tier = "logarithmic"    # Varma QXY weak degeneracy
    else:
        tier = "none"

    return score, tier


# Pre-built correlation data for known reference systems
REFERENCE_CORRELATION_DATA: Dict[str, "VarmaCorrelationData"] = {}


def _build_reference_data() -> None:
    """Populate reference correlation data for Varma XY and 2D percolation."""
    # Varma quantum XY critical point
    # ξ_τ ≈ 1e6 (large temporal scale), ξ_r ≈ ln(1e6) ≈ 13.8 lattice units
    REFERENCE_CORRELATION_DATA["varma_qxy"] = VarmaCorrelationData(
        xi_r=13.8,
        xi_tau=1e6,
        delta=0.001,
        additional_exponents={"z_eff": float("inf"), "eta": 0.0},
    )
    # 2D bond percolation threshold in H-bond network
    # Near p_c ≈ 0.5: ξ_r ~ |p - p_c|^{-ν}, ν ≈ 4/3
    # ξ_τ ~ ξ_r^z with z ≈ 1.33 for 2D percolation
    xi_r_perc = 20.0   # near threshold
    xi_tau_perc = xi_r_perc ** 1.33   # z = 1.33 for 2D critical percolation
    REFERENCE_CORRELATION_DATA["hbond_percolation_2d"] = VarmaCorrelationData(
        xi_r=xi_r_perc,
        xi_tau=xi_tau_perc,
        delta=0.02,
        additional_exponents={"z": 1.33, "nu": 1.333, "p_c": 0.5},
    )


_build_reference_data()


def check_logarithmic_scaling(
    xi_r: float,
    xi_tau: float,
    tolerance: float = 0.20,
) -> Tuple[bool, float]:
    """
    Check whether ξ_r ≈ ln ξ_τ holds within a fractional tolerance.

    Returns:
        (is_log_scaling, ratio) where ratio = ξ_r / ln(ξ_τ).
        ratio ≈ 1.0 confirms Varma QXY scaling.
    """
    if xi_tau <= 1.0 or xi_r <= 0.0:
        return False, float("nan")
    ln_xi_tau = math.log(xi_tau)
    if ln_xi_tau <= 0:
        return False, float("nan")
    ratio = xi_r / ln_xi_tau
    is_log_scaling = abs(ratio - 1.0) <= tolerance
    return is_log_scaling, ratio


def predict_spatial_from_temporal(xi_tau: float) -> float:
    """
    Predict ξ_r from ξ_τ using the Varma QXY relation: ξ_r = ln(ξ_τ).

    Args:
        xi_tau: temporal correlation length (must be > 1)

    Returns:
        Predicted ξ_r
    """
    if xi_tau <= 1.0:
        return 0.0
    return math.log(xi_tau)


def predict_delta_from_xi_tau(xi_tau: float) -> Optional[float]:
    """
    Invert ξ_τ ~ exp(π / √δ) to recover δ (distance from QCP).

    Returns:
        δ = (π / ln ξ_τ)² or None if xi_tau ≤ 1
    """
    if xi_tau <= 1.0:
        return None
    return (math.pi / math.log(xi_tau)) ** 2


def score_phi_c_candidacy(
    synthon: Synthon,
    correlation_data: Optional[VarmaCorrelationData] = None,
) -> PhiCCandidacyReport:
    """
    Compute Φ_c candidacy score for a synthon, with Varma QXY interpretation.

    Score components (each 0–1, weighted):
    1. Explicit Φ_c assignment (weight 0.35)
    2. Logarithmic ξ_r ≈ ln ξ_τ scaling observed (weight 0.30)
    3. Multi-domain dimensionality (D spanning ≥2 scales, weight 0.15)
    4. Granularity ambiguity (G_ג = MESOSCALE, weight 0.10)
    5. Dynamic criticality description (R_‡ + temporal, weight 0.10)

    Args:
        synthon: Synthon to evaluate
        correlation_data: Optional empirical ξ_r, ξ_τ measurements

    Returns:
        PhiCCandidacyReport
    """
    report = PhiCCandidacyReport(synthon_name=synthon.name)
    factors: List[Dict[str, Any]] = []
    score = 0.0

    # --- Factor 1: Explicit Φ_c assignment (weight 0.35) ---
    if synthon.criticality_phase == CriticalityPhase.CRITICAL:
        w1 = 0.35
        factors.append({
            "name": "Explicit Φ_c assignment",
            "weight": w1,
            "contribution": w1,
            "note": "synthon.criticality_phase == Phi_c",
        })
        score += w1
    elif synthon.criticality_phase == CriticalityPhase.SUBCRITICAL:
        w1 = 0.0
        factors.append({
            "name": "Explicit Φ_sub assignment",
            "weight": 0.35,
            "contribution": w1,
            "note": "Not yet confirmed critical — candidacy remains open",
        })
    else:
        # No Φ assignment — moderate prior
        w1 = 0.10
        factors.append({
            "name": "Unassigned Φ (default prior)",
            "weight": 0.35,
            "contribution": w1,
            "note": "No criticality_phase set — using weak prior",
        })
        score += w1
        report.flags.append(
            "Φ unassigned: assign Phi_c or Phi_sub to enable full Axiom 5 check."
        )

    # --- Factor 2: Logarithmic scaling check (weight 0.30) ---
    if correlation_data and correlation_data.xi_r and correlation_data.xi_tau:
        is_log, ratio = check_logarithmic_scaling(
            correlation_data.xi_r, correlation_data.xi_tau
        )
        if is_log:
            w2 = 0.30
            report.gd_degenerate = True
            report.gd_degeneracy_type = "logarithmic"
            report.universality_class = "Varma_QXY"
            factors.append({
                "name": "ξ_r ≈ ln ξ_τ scaling confirmed",
                "weight": 0.30,
                "contribution": w2,
                "ratio": round(ratio, 3),
                "note": "Varma QXY universality class — G/D logarithmically degenerate",
            })
            score += w2

            # Build scaling prediction
            xi_r_pred = predict_spatial_from_temporal(correlation_data.xi_tau)
            delta_pred = predict_delta_from_xi_tau(correlation_data.xi_tau)
            report.scaling_prediction = {
                "xi_r_predicted": round(xi_r_pred, 4),
                "xi_r_observed": round(correlation_data.xi_r, 4),
                "ratio": round(ratio, 4),
                "delta_from_qcp": round(delta_pred, 6) if delta_pred else None,
                "note": (
                    "ξ_τ ~ exp(π/√δ), ξ_r ~ ln ξ_τ ~ π/√δ. "
                    "Near QCP: spatial scale grows as √δ suppresses ξ_r, "
                    "temporal diverges exponentially."
                ),
            }
        else:
            # Check for power-law degeneracy (standard criticality)
            if correlation_data.xi_tau > 0:
                z_eff = (
                    math.log(correlation_data.xi_r) / math.log(correlation_data.xi_tau)
                    if correlation_data.xi_tau > 1 and correlation_data.xi_r > 1
                    else None
                )
                if z_eff and abs(z_eff - 1.0) < 0.3:
                    w2 = 0.20
                    report.gd_degenerate = True
                    report.gd_degeneracy_type = "power_law"
                    report.universality_class = "standard_QCP"
                    factors.append({
                        "name": "ξ_r ~ ξ_τ^z scaling (standard QCP)",
                        "weight": 0.30,
                        "contribution": w2,
                        "z_eff": round(z_eff, 3),
                        "note": f"Power-law degeneracy with z≈{z_eff:.2f}",
                    })
                    score += w2
                else:
                    factors.append({
                        "name": "Scaling check inconclusive",
                        "weight": 0.30,
                        "contribution": 0.0,
                        "ratio_ln": round(ratio, 3),
                        "note": f"ξ_r/ln(ξ_τ) = {ratio:.3f} (not ≈1, not power-law)",
                    })
            report.scaling_prediction = {
                "xi_r_observed": round(correlation_data.xi_r, 4),
                "xi_tau_observed": round(correlation_data.xi_tau, 4),
                "xi_r_predicted_from_ln": round(predict_spatial_from_temporal(correlation_data.xi_tau), 4),
                "note": "Scaling does not match Varma QXY prediction.",
            }
    else:
        # No data — estimate from tuple structure
        # Varma QXY typically has: D_∞ + hybrid domains + R_‡
        from .models import RecognitionMode
        has_temporal = "temporal" in synthon.dimensionality.domains
        has_multi_domain = len(synthon.dimensionality.domains) >= 2
        has_catalytic = synthon.recognition_mode in {
            RecognitionMode.DYNAMIC_CATALYTIC,
            RecognitionMode.COVALENT_DYNAMIC,
        }
        if has_temporal and has_multi_domain and has_catalytic:
            w2 = 0.15
            factors.append({
                "name": "Tuple signature suggestive of Varma QXY",
                "weight": 0.30,
                "contribution": w2,
                "note": "D_∞ + multi-domain + R_‡: consistent with QXY signature, no scaling data",
            })
            score += w2
        else:
            factors.append({
                "name": "No correlation data, tuple signature weak",
                "weight": 0.30,
                "contribution": 0.0,
                "note": "Provide xi_r, xi_tau measurements for definitive check",
            })
        report.flags.append(
            "No ξ_r/ξ_τ data provided. Score is based on tuple structure only."
        )

    # --- Factor 3: Multi-domain dimensionality (weight 0.15) ---
    n_domains = len(synthon.dimensionality.domains)
    if n_domains >= 2:
        w3 = 0.15
        factors.append({
            "name": f"Multi-domain D ({n_domains} domains)",
            "weight": 0.15,
            "contribution": w3,
            "note": "D spans ≥2 scales — prerequisite for G/D degeneracy",
        })
        score += w3
    elif "temporal" in synthon.dimensionality.domains:
        w3 = 0.08
        factors.append({
            "name": "Temporal dimension present (single domain)",
            "weight": 0.15,
            "contribution": w3,
            "note": "D_∞ without spatial domain — limited G/D test",
        })
        score += w3
    else:
        factors.append({
            "name": "No temporal dimension",
            "weight": 0.15,
            "contribution": 0.0,
            "note": "Varma QXY requires D_∞ or hybrid domain",
        })
        report.flags.append(
            "No temporal dimension (D_∞): Varma QXY criticality requires temporal correlations."
        )

    # --- Factor 4: Granularity MESOSCALE (weight 0.10) ---
    if synthon.granularity == Granularity.MESOSCALE:
        w4 = 0.10
        factors.append({
            "name": "G = MESOSCALE (G_ג)",
            "weight": 0.10,
            "contribution": w4,
            "note": "Mesoscale granularity is consistent with G/D ambiguity near criticality",
        })
        score += w4
    else:
        factors.append({
            "name": f"G = {synthon.granularity.name} (not MESOSCALE)",
            "weight": 0.10,
            "contribution": 0.0,
            "note": "MESOSCALE preferred for critical systems",
        })

    # --- Factor 5: Dynamic catalytic recognition (weight 0.10) ---
    from .models import RecognitionMode
    if synthon.recognition_mode in {RecognitionMode.DYNAMIC_CATALYTIC, RecognitionMode.COVALENT_DYNAMIC}:
        w5 = 0.10
        factors.append({
            "name": f"R = {synthon.recognition_mode.name}",
            "weight": 0.10,
            "contribution": w5,
            "note": "Dynamic recognition supports temporal criticality coupling",
        })
        score += w5
    else:
        factors.append({
            "name": f"R = {synthon.recognition_mode.name} (not dynamic)",
            "weight": 0.10,
            "contribution": 0.0,
        })

    # --- Factor 6: Literature proxy from grounding metadata (weight 0.65) ---
    # When grounding.phi_c_candidacy carries an expert proxy_degeneracy_strength
    # (e.g. from published barrier data, vibrational mode separation, scale
    # sensitivity analysis), it is a direct estimate of Varma-probe score for
    # a non-QXY criticality mechanism (e.g. spatial/mechanical steric-cliff).
    # Contributes as a floor — other factors may add on top.
    proxy_score = 0.0
    proxy_basis = None
    g = getattr(synthon, "grounding", None)
    if g is not None:
        if isinstance(g, dict):
            cand = g.get("phi_c_candidacy", {}) or {}
        elif hasattr(g, "phi_c_candidacy"):
            cand = getattr(g, "phi_c_candidacy", {}) or {}
        else:
            cand = {}
        if isinstance(cand, dict):
            proxy_score = float(cand.get("proxy_degeneracy_strength", 0.0))
            proxy_basis = cand.get("basis", None)
    if proxy_score >= 0.50:
        w6 = proxy_score * 0.65   # proxy is a partial substitute for measured ξ_r/ξ_τ
        factors.append({
            "name": f"Literature proxy degeneracy_strength = {proxy_score:.2f}",
            "weight": 0.65,
            "contribution": round(w6, 3),
            "note": (
                f"Expert proxy from grounding metadata "
                f"({proxy_basis or 'see grounding.phi_c_candidacy'}). "
                "Pending confirmation via measured ξ_r/ξ_τ."
            ),
        })
        score += w6
        # Inherit degeneracy classification from proxy metadata if not already set
        if not report.gd_degenerate and isinstance(cand, dict):
            cls = cand.get("classification", "")
            if "power-law" in cls or "logarithmic" in cls:
                report.gd_degeneracy_type = cls
                report.universality_class = "steric-cliff proxy (pending Varma scan)"
        report.flags.append(
            "Score boosted by literature proxy degeneracy_strength from grounding metadata. "
            "Run full Varma probe (--xi-r / --xi-tau) to replace proxy with measured values."
        )

    # --- Factor 7: Classical bifurcation criticality — Frank model (weight 0.25) ---
    #
    # Detects the structural fingerprint of a pitchfork bifurcation (Frank 1953)
    # / symmetry-breaking autocatalytic amplifier.  This is CLASSICAL criticality,
    # distinct from the Varma QXY quantum critical point scored by factors 1–5.
    #
    # Required co-occurrence (all four must be present):
    #   D_∞       — temporal self-organisation: the cycle is sustained, not transient
    #   T_bowtie  — closed-loop topology: product feeds back as catalyst
    #   P_directional — enantiospecific / chiral recognition: the broken symmetry is
    #                   encoded in a directional polarity primitive
    #   F_hbar    — high fidelity: amplification gain > 1 per cycle; without F_hbar
    #               the system drifts (racemises) rather than amplifies
    #
    # Together these encode: "an enantiospecific closed autocatalytic cycle whose
    # fidelity exceeds the drift threshold" — the minimal Frank-model bifurcation.
    # Near ee = 0 this system sits at the bifurcation point; small fluctuations
    # break the symmetry and the order parameter (ee) diverges to ±1.
    #
    # The contribution (0.25) is intentionally conservative: classical bifurcation
    # is well-established phenomenology but the correlation lengths have not been
    # measured; the Varma QXY scaling check (factor 2) remains the gold standard
    # for Phi_c confirmation.
    from .models import Topology, Polarity, Fidelity
    _has_temporal    = "temporal" in synthon.dimensionality.domains
    _has_bowtie      = synthon.topology == Topology.CYCLIC_BOWTIE
    _has_directional = synthon.polarity  == Polarity.DONOR_ACCEPTOR   # P_directional
    _has_high_f      = synthon.fidelity  == Fidelity.HIGH              # F_hbar
    if _has_temporal and _has_bowtie and _has_directional and _has_high_f:
        w7 = 0.25
        factors.append({
            "name": "Classical bifurcation fingerprint (Frank model)",
            "weight": 0.25,
            "contribution": w7,
            "note": (
                "D_∞ + T_bowtie + P_directional + F_hbar co-present: "
                "gain > 1 enantiospecific closed autocatalytic cycle. "
                "Pitchfork bifurcation at ee = 0 (Frank 1953). "
                "Classical symmetry-breaking criticality — universality class "
                "distinct from Varma QXY. Confirm with ξ_r divergence near "
                "bifurcation point (SAXS/DLS at varying initial ee)."
            ),
        })
        score += w7
        # Annotate universality class if not already set by Varma check
        if not report.gd_degenerate:
            report.gd_degenerate = True
            report.gd_degeneracy_type = "classical_bifurcation"
            report.universality_class = "Frank_model (classical pitchfork)"
    else:
        _missing = [
            label for cond, label in [
                (_has_temporal,    "D_∞"),
                (_has_bowtie,      "T_bowtie"),
                (_has_directional, "P_directional"),
                (_has_high_f,      "F_hbar"),
            ] if not cond
        ]
        factors.append({
            "name": "Classical bifurcation fingerprint (Frank model)",
            "weight": 0.25,
            "contribution": 0.0,
            "note": (
                f"Not all four Frank-model co-requisites present. "
                f"Missing: {', '.join(_missing)}. "
                "No classical bifurcation signature."
            ),
        })

    # --- Factor 8: Quantum criticality fingerprint (weight 0.20) ---
    # Pattern: G_aleph + F_hbar + K_trap + ¬D_∞
    # Maps to: transverse-field Ising at h=h_c, heavy fermions (CeCu₆₋ₓAuₓ, YbRh₂Si₂),
    # quantum dots at charge degeneracy.  Distinct from Varma QXY (temporal) —
    # this is a spatial, ground-state degeneracy universality class.
    w8 = 0.20
    _has_galeph  = synthon.granularity == Granularity.GLOBAL
    _has_f_high  = synthon.fidelity == Fidelity.HIGH
    _has_k_trap  = synthon.kinetic_character == KineticCharacter.TRAP
    _no_temporal = not (hasattr(synthon.dimensionality, "domains") and
                        "temporal" in getattr(synthon.dimensionality, "domains", []))
    # Also accept dimensionality not being TEMPORAL sub-label
    if hasattr(synthon.dimensionality, "value"):
        _no_temporal = _no_temporal and ("infinity" not in synthon.dimensionality.value)

    if _has_galeph and _has_f_high and _has_k_trap and _no_temporal:
        score += w8
        factors.append({
            "name": "Quantum criticality fingerprint (G_aleph + F_hbar + K_trap + ¬D_∞)",
            "weight": w8,
            "contribution": w8,
            "note": (
                "All four quantum criticality co-requisites present: G_aleph (non-local constraint), "
                "F_hbar (high constraint reliability), K_trap (ground-state-frozen kinetics), "
                "¬D_∞ (spatial, not temporal). "
                "Maps to TFI / heavy-fermion / quantum-dot-at-degeneracy universality class. "
                "Falsifiable prediction: susceptibility divergence χ(T→0) ~ T^{−γ}; "
                "confirm with low-T spectroscopic data or many-body scaling."
            ),
        })
        if not report.universality_class:
            report.universality_class = "quantum_criticality (TFI/heavy_fermion class)"
        if not report.gd_degenerate:
            report.gd_degenerate = True
            report.gd_degeneracy_type = "quantum_ground_state"
    else:
        _qc_missing = [
            label for cond, label in [
                (_has_galeph,  "G_aleph"),
                (_has_f_high,  "F_hbar"),
                (_has_k_trap,  "K_trap"),
                (_no_temporal, "¬D_∞"),
            ] if not cond
        ]
        factors.append({
            "name": "Quantum criticality fingerprint (G_aleph + F_hbar + K_trap + ¬D_∞)",
            "weight": w8,
            "contribution": 0.0,
            "note": (
                f"Quantum criticality pattern incomplete. Missing: {', '.join(_qc_missing)}. "
                "Not a quantum critical point candidate."
            ),
        })

    report.contributing_factors = factors
    report.score = min(1.0, score)

    # --- Axiom 5 assessment ---
    if report.gd_degenerate:
        report.axiom5_satisfied = True
        if report.gd_degeneracy_type == "logarithmic":
            report.axiom5_note = (
                "Axiom 5 WEAKLY satisfied (logarithmic G/D degeneracy). "
                "G is determined by D via ξ_r = ln(ξ_τ), but not by direct power-law scaling. "
                "Tuple contraction: ⟨D; G⟩ → ⟨D; Φ_c⟩ with qualifier 'log-degenerate'."
            )
        elif report.gd_degeneracy_type == "classical_bifurcation":
            report.axiom5_note = (
                "Axiom 5 SATISFIED (classical symmetry-breaking bifurcation). "
                "Frank-model pitchfork at ee = 0: G collapses into D at the bifurcation point. "
                "Tuple contraction: ⟨D; G⟩ → ⟨D; Φ_c⟩ with universality class Frank_model. "
                "Confirm by measuring ξ_r divergence near bifurcation (SAXS/DLS at varying initial ee)."
            )
        else:
            report.axiom5_note = (
                "Axiom 5 SATISFIED (power-law G/D degeneracy). "
                "Standard critical point: ξ_r ~ ξ_τ^(1/z), G redundant given D."
            )
    elif report.score >= 0.40:
        report.axiom5_note = (
            "Axiom 5 APPROACHING (insufficient data for confirmation). "
            "Provide empirical ξ_r, ξ_τ measurements to confirm degeneracy."
        )
    else:
        report.axiom5_note = (
            "Axiom 5 NOT SATISFIED: G and D appear independent. "
            "System is subcritical or not in Varma QXY universality class."
        )

    # --- Recommendation ---
    label = report._candidacy_label()
    if report.score >= 0.70:
        report.recommendation = (
            f"Assign Phi_c. {report.axiom5_note} "
            f"Universality class: {report.universality_class or 'unconfirmed — needs scaling data'}."
        )
    elif report.score >= 0.40:
        report.recommendation = (
            f"Candidate for Phi_c ({label}). Measure ξ_r and ξ_τ near the QCP to confirm "
            f"ξ_r ≈ ln ξ_τ. If confirmed, assign Phi_c and note 'log-degenerate'."
        )
    else:
        report.recommendation = (
            f"Keep Phi_sub. No compelling evidence for criticality. "
            f"Score {report.score:.2f}/1.0."
        )

    return report


def score_transition_phi_c(
    morphism: "TransitionMorphism",
) -> PhiCCandidacyReport:
    """
    Score the Φ_c candidacy of a phase transition morphism.

    This is the morphism-level closure of Factor 8 in the Varma probe.
    Factor 8 fires on endpoint primitives as a heuristic
    (G_aleph + F_hbar + K_trap + ¬D_∞); this fires on the transition
    itself — the exact algebraic predicate for a quantum critical point.

    A morphism-level QCP requires:
      (a) 2nd-order transition (HotSwap path exists)
      (b) The forward path passes through at least one Φ_c intermediate

    Condition (b) is the precise definition: the system is tuned *through*
    the critical point, not merely adjacent to it.  The morphism-level score
    is always more reliable than the endpoint heuristic, because it reflects
    the actual topology of the transition, not a pattern match on either
    endpoint's primitives.

    Score tiers:
      ≥ 0.85 : morphism QCP confirmed (exact predicate)
      0.40–0.85 : 2nd-order but QCP unconfirmed (no Φ_c intermediate found;
                  register one in the same D/T cluster to confirm)
      < 0.40 : 1st-order or unknown — no QCP possible

    The report's ``synthon_name`` field carries the transition label
    ``"src → dst"`` rather than a single synthon name.
    """
    from .morphism import TransitionOrder

    label = f"{morphism.src_name} → {morphism.dst_name}"
    report = PhiCCandidacyReport(synthon_name=label)
    factors: List[Dict[str, Any]] = []
    score = 0.0

    # --- Factor A: Transition order (prerequisite, weight 0.40) ---
    if morphism.order == TransitionOrder.SECOND:
        wA = 0.40
        factors.append({
            "name": "2nd-order transition",
            "weight": wA,
            "contribution": wA,
            "note": "HotSwap path exists — continuous transition; prerequisite for QCP",
        })
        score += wA
    elif morphism.order == TransitionOrder.FIRST:
        factors.append({
            "name": "1st-order transition",
            "weight": 0.40,
            "contribution": 0.0,
            "note": "No HotSwap path — discontinuous; no QCP possible",
        })
        report.flags.append("1st-order transition: no quantum critical point possible.")
        report.score = 0.0
        report.contributing_factors = factors
        report.recommendation = (
            f"No QCP. 1st-order transition (structural D/T or F-floor conflict). "
            "The barrier between phases is a discontinuity, not a critical point."
        )
        return report
    else:
        factors.append({
            "name": "Transition order unknown",
            "weight": 0.40,
            "contribution": 0.0,
            "note": "Cannot assess QCP without order classification",
        })
        report.score = 0.0
        report.contributing_factors = factors
        report.recommendation = "Expand catalog to determine transition order."
        return report

    # --- Factor B: Φ_c intermediate on path (exact predicate, weight 0.45) ---
    if morphism.is_quantum_critical and morphism.quantum_critical_point:
        qcp = morphism.quantum_critical_point
        wB = 0.45
        factors.append({
            "name": "Φ_c intermediate on path (morphism QCP — exact predicate)",
            "weight": wB,
            "contribution": wB,
            "qcp_synthons": qcp.qcp_synthon_names,
            "note": (
                "Path passes through Φ_c synthon(s): system is tuned through the "
                "critical point, not adjacent to it.  Exact morphism-level QCP predicate "
                "— superior to Factor 8 endpoint heuristic "
                "(G_aleph + F_hbar + K_trap + ¬D_∞)."
            ),
        })
        score += wB
        report.gd_degenerate = True
        report.gd_degeneracy_type = "morphism_qcp"
        report.axiom5_satisfied = True
        report.axiom5_note = (
            "Axiom 5 SATISFIED at the Φ_c intermediate: G/D degeneracy holds at the "
            "critical point the transition passes through.  Axiom 5 is a path property "
            "of the morphism, not an endpoint property of either phase."
        )
        # Universality class from hints
        for hint in qcp.universality_hints:
            if "TFI/heavy-fermion" in hint:
                report.universality_class = "quantum_criticality (TFI/heavy_fermion class)"
                break
            elif "non-local" in hint:
                report.universality_class = "non-local QCP (G_aleph)"
                break
        if not report.universality_class:
            report.universality_class = "morphism_QCP (universality class unresolved)"
    else:
        factors.append({
            "name": "No Φ_c intermediate on path",
            "weight": 0.45,
            "contribution": 0.0,
            "note": (
                "2nd-order transition but no Φ_c synthon on the forward path.  "
                "May be a sub-critical crossover or weakly 2nd-order.  "
                "Register a Φ_c synthon in the same D/T cluster to confirm QCP."
            ),
        })
        report.flags.append(
            "No Φ_c intermediate found.  "
            "Register a Φ_c synthon in the same D/T cluster as src and dst to confirm QCP."
        )

    # --- Factor C: Reversibility bonus (weight 0.10) ---
    if morphism.is_reversible:
        wC = 0.10
        factors.append({
            "name": "Reversible morphism (asymmetry < 0.20)",
            "weight": wC,
            "contribution": wC,
            "asymmetry": morphism.asymmetry,
            "note": "Symmetric QCP — transition is bidirectional at equal thermodynamic cost",
        })
        score += wC
    elif math.isfinite(morphism.reverse_cost):
        wC = 0.05
        factors.append({
            "name": f"Asymmetric morphism (asymmetry = {morphism.asymmetry:.3f})",
            "weight": 0.10,
            "contribution": wC,
            "note": (
                "Reverse path exists but asymmetric — directional QCP "
                "(e.g. topological protection asymmetry)"
            ),
        })
        score += wC
    else:
        factors.append({
            "name": f"Irreversible morphism (asymmetry = {morphism.asymmetry:.3f})",
            "weight": 0.10,
            "contribution": 0.0,
            "note": "No reverse path — morphism irreversible in this direction",
        })

    # --- Factor D: Universality class resolved (weight 0.05) ---
    if report.universality_class and "unresolved" not in report.universality_class:
        wD = 0.05
        factors.append({
            "name": f"Universality class: {report.universality_class}",
            "weight": wD,
            "contribution": wD,
            "note": "Derived from Φ_c intermediate primitive assignments",
        })
        score += wD

    report.contributing_factors = factors
    report.score = min(1.0, score)

    if report.score >= 0.85:
        report.recommendation = (
            f"Morphism QCP confirmed for {label}.  "
            f"Universality class: {report.universality_class or 'unresolved'}.  "
            f"{report.axiom5_note}"
        )
    elif report.score >= 0.40:
        report.recommendation = (
            f"2nd-order transition approaching QCP ({report.score:.2f}/1.00).  "
            "Register a Φ_c synthon in the same D/T cluster to confirm.  "
            "Until confirmed, label as 'weakly 2nd-order or critical crossover'."
        )
    else:
        report.recommendation = "No QCP evidence."

    return report


def check_axiom5_varma(
    synthon: Synthon,
    xi_r: Optional[float] = None,
    xi_tau: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Focused Axiom 5 check with Varma QXY interpretation.

    Returns a structured dict compatible with the existing axiom validation
    report format used in cli.py validate and audit commands.
    """
    data = VarmaCorrelationData(xi_r=xi_r, xi_tau=xi_tau)
    report = score_phi_c_candidacy(synthon, data)

    return {
        "axiom": "Axiom 5 (Criticality / Varma QXY probe)",
        "applies": report.score >= 0.40,
        "phi_c_score": report.score,
        "candidacy": report._candidacy_label(),
        "gd_degenerate": report.gd_degenerate,
        "gd_degeneracy_type": report.gd_degeneracy_type,
        "axiom5_satisfied": report.axiom5_satisfied,
        "axiom5_note": report.axiom5_note,
        "universality_class": report.universality_class,
        "scaling_prediction": report.scaling_prediction,
        "flags": report.flags,
        "recommendation": report.recommendation,
    }
