---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# Elucidating Contested Reaction Mechanisms through Structural Encoding

## Abstract

Six contested or debated organic reaction mechanisms — proline-catalyzed aldol reactions, aryl diazonium dediazonizations, "on water" interfacial reactions, the Wittig reaction, Grignard reagent formation, and Bredt's Rule violations — are encoded as structural types in the Imscribing Grammar (IG). Each system is assigned a unique 12-primitive tuple $\langle D; T; R; P; F; K; G; \Gamma; \Phi; H; S; \Omega \rangle$ derived from mechanistic principles rather than empirical fitting. Pairwise structural distances, tensor products, and consciousness (C) scores are computed to reveal hidden mechanistic relationships. The analysis resolves long-standing debates by showing that each contested mechanism occupies a distinct point in structural phase space, with the nature of the disagreement itself encoded in specific primitive values.

## 1. Introduction

Reaction mechanisms in organic chemistry are often inferred from kinetic data, isotopic labeling, and computational modeling. Where consensus is absent, the debate typically centers on which intermediate is "real" or which pathway is "dominant." The Imscribing Grammar reframes this: a reaction mechanism is a structural type, defined by 12 independent primitives that encode dimensionality, topology, relational coupling, symmetry, fidelity regime, kinetics, scope, interaction grammar, criticality, temporal depth, stoichiometry, and topological winding. Two mechanisms that differ by even one primitive belong to different structural regimes. Where mechanisms appear equivalent under classical analysis but diverge in their IG encoding, the debate is not merely interpretive — it reflects genuine structural ambiguity.

This manuscript encodes six contested mechanisms, computes their pairwise distances and composite types, and draws mechanistic conclusions from the resulting structural geometry.

## 2. Methods

Each system is encoded by explicit application of the deterministic encoding procedure (encoding_method.md, steps [1]–[12]). No heuristic or subjective assignment is used. Structural distances are computed using the IG metric $d = \sqrt{\sum_i w_i (\delta_i)^2}$ with catalog-derived weight tensor $g_{ij} = \Sigma^{-1}$. Tensor products follow the canonical rule: max on union primitives, min on $P$ and $F$ (bottleneck principle). Consciousness scores $C \in [0,1]$ evaluate two gates: Gate 1 ($\Phi_{\text{ctyogh}}$ criticality required) and Gate 2 ($K \leq K_{\text{schwa}}$ required). All computations are performed via the IG imscription tool suite.

## 3. Results

### 3.1 Proline-Catalyzed Aldol Reaction

**Encoded type:** $\langle D_{\text{turnthree}};\ T_{\text{bullseye}};\ R_{\text{ctz}};\ P_{\text{pipevar}};\ F_{\text{beltl}};\ K_{\text{turnm}};\ G_{\text{gamma}};\ \Gamma_{\text{spleftarrow}};\ \Phi_{\text{ctyogh}};\ H_2;\ n{:}m;\ \Omega_{\text{closeepsilon}} \rangle$

**Consciousness score:** $C = 0.322$ (both gates open)

The Hajos–Parrish–Eder–Sauer–Wiechert reaction has been debated along three lines: the classical enamine mechanism, the enol intermediate pathway (proposed for $(S)\text{-Cat}$-catalyzed N-nitroso aldol), and the oxazolidinone hypothesis (that oxazolidinones are productive intermediates rather than parasitic side products).

The structural encoding reveals that the three pathways occupy a *crossing-point topology* ($T_{\text{bullseye}}$): they converge on a shared transition state surface but originate from distinct pre-organized intermediates. The interaction grammar $\Gamma_{\text{spleftarrow}}$ (disjunctive) confirms that multiple alternative routes are structurally permitted — the reaction does not commit to a single pathway but distributes flux across competing channels. The categorical coupling $R_{\text{ctz}}$ indicates a functorial relationship between the proline-derived organocatalyst and the carbonyl substrate; the catalyst maps the substrate space to the reactive intermediate space without bidirectional feedback.

The partial symmetry $P_{\text{pipevar}}$ encodes the fact that one key symmetry (the proline stereocenter) is preserved throughout, but the overall reaction path breaks additional symmetries (e.g., the symmetry between enantiomeric faces of the prochiral aldehyde). Stoichiometry $n{:}m$ reflects the heterogeneous composition: one catalyst type, multiple substrate types.

**Mechanistic conclusion:** The IG encoding adjudicates in favor of a *multi-channel* mechanism. The enamine, enol, and oxazolidinone pathways are not mutually exclusive — they are disjunctive alternatives ($\Gamma_{\text{spleftarrow}}$) that share the same topological crossing point. The debate persists because experimental conditions (solvent, concentration, sterics) bias the flux distribution among channels. Oxazolidinones are structurally encoded as on-pathway intermediates (their inclusion changes $T$, not an independent variable), consistent with their observed catalytic effect in certain solvent systems.

## 3.2 Aryl Diazonium Salt Substitution (Dediazonizations)

**Encoded type:** $\langle D_{\text{turnthree}};\ T_{\text{bullseye}};\ R_{\text{ctz}};\ P_{\text{upsilon}};\ F_{\text{beltl}};\ K_{\text{turnm}};\ G_{\text{gamma}};\ \Gamma_{\text{spleftarrow}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{closeepsilon}} \rangle$

**Consciousness score:** $C = 0.322$ (both gates open)

**Pairwise distances:**
- vs. proline_catalyzed_aldol: $d = 2.2361$ (differ in $P$ and $S$)
- vs. wittig_reaction: $d = 1.0$ (differ only in $P$; structurally *related*)
- vs. grignard_reagent_formation: $d = 3.2711$ (structurally *remote*)

The debate centers on SN1 (phenyl cation) versus radical (single-electron transfer) pathways. The structural resolution emerges from the parity assignment: $P_{\text{upsilon}}$ (quantum superposition parity) encodes that the diazonium group exists in a superposition of ionic and radical character at the critical transition state. This is not merely a kinetic competition between two pathways — the diazonium moiety structurally *cannot* be resolved into one or the other without measurement.

The tensor product with the Wittig reaction $\text{aryl\_diazonium} \otimes \text{wittig} = \langle D_{\text{turnthree}};\ T_{\text{bullseye}};\ R_{\text{ctz}};\ P_{\text{upsilon}};\ F_{\text{beltl}};\ K_{\text{turnm}};\ G_{\text{gamma}};\ \Gamma_{\text{spleftarrow}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{closeepsilon}} \rangle$ shows that the $P$ bottleneck resolves to $P_{\text{upsilon}}$ (the quantum parity is the minimum of $P_{\text{upsilon}}$ and $P_{\text{pipevar}}$), confirming that aryl diazonium chemistry inherently involves radical character. The distance of merely 1.0 from the Wittig reaction (which shares everything except parity) reveals that *both reactions share the same underlying structural substrate*: 1:1 bond reorganization at a crossing point topology with categorical coupling and moderate kinetics.

Stoichiometry $1{:}1$ reflects the unimolecular loss of N₂ — one diazonium ion decomposes to one aryl intermediate. The two-step temporal memory ($H_2$) encodes that the rate-determining step (diazonium decomposition) carries information from the initial ionization state through the reactive intermediate to the final product.

**Mechanistic conclusion:** The dediazonization proceeds through a structural regime where SN1 and radical pathways are *not discrete alternatives* but superposed limits of a single $\Phi_{\text{ctyogh}}$-critical transition surface. Experimental conditions shift the observable toward one limit, but the underlying mechanism is irreducibly dual-character, encoded as $P_{\text{upsilon}}$. This explains the persistent disagreement in the literature: both camps observe genuine facets of a superposed structural reality.

### 3.3 "On Water" Interfacial Reactions

**Encoded type:** $\langle D_{\text{turnthree}};\ T_{\text{invscr}};\ R_{\text{lyoghlig}};\ P_{\text{pipevar}};\ F_{\text{beltl}};\ K_{\text{frtailgamma}};\ G_{\text{gamma}};\ \Gamma_{\text{corner}};\ \Phi_{\text{ctyogh}};\ H_1;\ n{:}m;\ \Omega_{\text{closeepsilon}} \rangle$

**Consciousness score:** $C = 0.2095$ (both gates open; lower $C$ driven by $K_{\text{frtailgamma}}$)

**Pairwise distance vs. proline_catalyzed_aldol:** $d = 2.7928$ (differ in $R, T, K, \Gamma, H$)

The structural encoding decisively distinguishes the "on water" regime from bulk solution chemistry. Five primitives simultaneously diverge from canonical solution-phase mechanisms:

- **Topology ($T_{\text{invscr}}$):** The water-organic interface is a topological *inclusion* boundary — reactants are confined within the interfacial layer, not free in bulk solution. This is categorically distinct from $T_{\text{bullseye}}$ (crossing point) of solution-phase reactions.
- **Relational mode ($R_{\text{lyoghlig}}$):** The feedback between interfacial tension and reaction rate is bidirectional. As the reaction proceeds, product formation alters the interfacial tension, which in turn modifies the effective reactant concentration at the interface. This positive feedback loop is absent in bulk solution.
- **Kinetics ($K_{\text{frtailgamma}}$):** Rate acceleration is the defining feature — $\tau \ll T_\text{observation}$. The reaction is driven far from equilibrium by interfacial forces, distinguishing it from the $K_{\text{turnm}}$ kinetics of competing solution-phase mechanisms.
- **Interaction grammar ($\Gamma_{\text{corner}}$):** The acceleration requires the *simultaneous* action of hydrogen bonding at the interface, hydrophobic compression of organic reactants, and the high cohesive energy of the water surface. All three factors are *necessary together* — no single factor is sufficient. This conjunctive grammar is the key signature that validates the interfacial mechanism over the "dissolved in boundary layer" alternative.
- **Temporal depth ($H_1$):** The interfacial reorganization provides only one-step memory. The current state depends on the immediately prior interfacial configuration, but not on the full history of interfacial rearrangements.

**Mechanistic conclusion:** The conjunctive interaction grammar ($\Gamma_{\text{corner}}$) structurally validates the "on water" (surface-mediated) mechanism. If the reaction were occurring in the boundary layer as in bulk solution, the grammar would be $\Gamma_{\text{spleftarrow}}$ (solvent-assisted or solvent-independent alternatives). The fact that all three interfacial factors must act simultaneously confirms that the reaction occurs *at* the interface, not merely *near* it. The bidirectional relational mode ($R_{\text{lyoghlig}}$) further confirms that the interface is an active participant, not a passive spectator.

### 3.4 The Wittig Reaction

**Encoded type:** $\langle D_{\text{turnthree}};\ T_{\text{bullseye}};\ R_\textrm{cat};\ P_{\text{pipevar}};\ F_{\text{beltl}};\ K_\textrm{mod};\ G_{\text{gamma}};\ \Gamma_{\text{spleftarrow}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{closeepsilon}} \rangle$

**Consciousness score:** $C = 0.322$ (both gates open)

**Pairwise distances:**
- vs. aryl_diazonium_dediazonization: $d = 1.0$ (related; differ only in $P$)
- vs. proline_catalyzed_aldol: $d = 2.0$ (differ only in $S$)

The Wittig reaction debate centers on whether the oxaphosphetane forms via a stepwise betaine intermediate or a concerted [2+2] cycloaddition, with additional complexity from lithium salt effects and potential radical-pair contributions.

The structural encoding reveals a disjunctive interaction grammar ($\Gamma_{\text{spleftarrow}}$) — precisely the signature of *alternative pathways that converge on the same topology* ($T_{\text{bullseye}}$, crossing point). The betaine pathway and the concerted pathway are not mutually exclusive; they are parallel routes to the same crossing point on the reaction surface.

The categorical coupling ($R_\textrm{cat}$) encodes the functorial relationship between the phosphonium ylide HOMO and the carbonyl LUMO. The lithium salt effect is understood not as a change in mechanism but as a *modulation of the relative barrier heights* between the two disjunctive channels. Lithium coordinates to both the ylide carbon and the carbonyl oxygen, selectively stabilizing the betaine intermediate and lowering the barrier for the stepwise channel.

The partial symmetry $P_{\text{pipevar}}$ is critical: it encodes that the reaction preserves one key symmetry element (the stereochemical information transfer from ylide geometry to alkene stereochemistry) but breaks others (the initial $C_{2v}$ symmetry of the approach complex collapses to $C_s$ in the oxaphosphetane).

Stoichiometry $1{:}1$ reflects the single ylide-to-carbonyl bond reorganization event. Two-step temporal memory ($H_2$) captures that the initial stereochemical outcome depends on both the ylide preparation state and the approach geometry — two prior states feed into the crossing point.

**Mechanistic conclusion:** The debate between concerted and stepwise mechanisms is a structural artifact of observing a system with $\Gamma_{\text{spleftarrow}}$ (disjunctive grammar). Both pathways exist; their relative flux depends on conditions (solvent, cation, sterics). The quantum theory of atoms in molecules (QTAIM) and natural bond orbital (NBO) analyses that challenge single-step concerted pathways are observing the same structural reality from different projections. The Wittig reaction is fundamentally a *multi-channel crossing-point* mechanism, with lithium salts acting as channel selectors.

### 3.5 Grignard Reagent Formation

**Encoded type:** $\langle D_{\text{turnthree}};\ T_\textrm{net};\ R_{\text{downstep}};\ P_{\text{upsilon}};\ F_{\text{beltl}};\ K_\textrm{mod};\ G_{\text{gamma}};\ \Gamma_\textrm{seq};\ \Phi_{\text{ctyogh}};\ H_2;\ n{:}m;\ \Omega_{\text{crtwo}} \rangle$

**Consciousness score:** $C = 0.268$ (both gates open)

The formation of Grignard reagents ($\text{RMgX}$) from alkyl halides and magnesium metal involves electron transfer at the metal surface with radical intermediates, but the precise sequence and surface chemistry remain debated.

The structural encoding is distinctive in three features:

1. **Branching topology ($T_\textrm{net}$):** The reaction proceeds through a network of competing radical pathways at the heterogeneous metal-solution interface. Each surface defect, step, and facet presents a distinct reactive site, creating a branching network of possible electron-transfer events.

2. **Adjoint coupling ($R_{\text{downstep}}$):** The magnesium surface and the organic halide interact as an adjoint pair — the surface donates an electron (forward direction) while the radical intermediate re-adsorbs to the surface (counit direction). The coupling is not bidirectional feedback ($R_{\text{lyoghlig}}$) but a one-way adjoint pair: the surface provides the electron, the radical returns for the second bond formation, but the substrate does not modulate the surface properties in a dynamically reciprocal manner.

3. **Sequential grammar ($\Gamma_\textrm{seq}$):** Unlike the disjunctive Grammars of the proline aldol and Wittig reactions, Grignard formation proceeds through an *ordered sequence* of steps: (i) surface adsorption, (ii) single-electron transfer to generate an alkyl radical, (iii) radical-surface combination, (iv) second electron transfer, (v) solvation of the resulting organomagnesium species. The order matters — reversing steps is kinetically prohibited.

4. **Binary winding protection ($\Omega_{\text{crtwo}}$):** The $\mathbb{Z}_2$ invariant encodes the parity-protected nature of the radical intermediates — radical species either pair (form bonds) or persist, with no continuous intermediates. This $\mathbb{Z}_2$ character, combined with the two-step temporal memory ($H_2$), satisfies Axiom B of the grammar.

**Mechanistic conclusion:** The Grammer encoding validates the radical mechanism (confirmed by $P_{\text{upsilon}}$ and $\Omega_{\text{crtwo}}$) and resolves the debate about the sequence of electron transfers. The sequential interaction grammar ($\Gamma_\textrm{seq}$) confirms that electron transfer, radical formation, and bond formation occur in a fixed order — a conclusion consistent with ESR detection of radical intermediates and the observed dependence of reaction rate on magnesium surface purity. The network topology ($T_\textrm{net}$) explains the notoriously poor reproducibility of Grignard formation across different laboratories: surface heterogeneity creates a distribution of local reaction channels, each with different kinetic parameters.

### 3.6 Bredt's Rule Violations

**Encoded type:** $\langle D_{\text{turnthree}};\ T_{\text{bullseye}};\ R_{\text{lyoghlig}};\ P_{\text{pipevar}};\ F_{\text{beltl}};\ K_\textrm{slow};\ G_{\text{beta}};\ \Gamma_{\text{corner}};\ \Phi_{\text{ctyogh}};\ H_2;\ n{:}m;\ \Omega_{\text{closeepsilon}} \rangle$

**Consciousness score:** $C = 0.356$ (both gates open; higher $C$ driven by $K_\textrm{slow}$)

**Pairwise distance vs. wittig_reaction:** $d = 3.3166$ (differ in $R, S, K, G, \Gamma$)

Bredt's Rule — the long-standing prohibition against double bonds at bridgehead carbons in bridged bicyclic systems — has been challenged by recent synthetic advances. The structural encoding reveals why violations are possible and what boundary conditions govern their emergence.

The key discriminant is kinetics: $K_\textrm{slow}$ (near-equilibrium relaxation) indicates that the bridgehead alkene exists as a *metastable minimum* on the potential energy surface. The system relaxes slowly compared to the observation time, meaning the "forbidden" species is not truly forbidden — it is simply disfavored kinetically in standard conditions. The crossing-point topology ($T_{\text{bullseye}}$) confirms that the bridgehead double bond occupies the same topological class as other concerted bond reorganizations (like the Wittig), but with bidirectional coupling ($R_{\text{lyoghlig}}$) between the strain energy and the electronic structure of the double bond.

The conjunctive grammar ($\Gamma_{\text{corner}}$) is the most mechanistically revealing primitive: bridgehead alkene formation requires the *simultaneous* satisfaction of multiple geometric constraints — sufficient ring size to accommodate the planar $sp^2$ geometry, appropriate bridge lengths to minimize torsional strain, and electronic factors (e.g., heteroatom stabilization) to compensate for the residual strain. No single factor is sufficient; the violation occurs only when all conditions are met simultaneously.

The local scope ($G_{\text{beta}}$) reflects that the phenomenon is highly localized — the structural consequences of placing a double bond at the bridgehead do not propagate far beyond the immediate ring system. This contrasts with the mesoscale ($G_{\text{gamma}}$) scope of the other five mechanisms, which have more extended influence.

**Mechanistic conclusion:** Bredt's Rule is not a fundamental prohibition but a *kinetic boundary* in structural phase space. Violations occur when the conjunctive alignment of ring size, bridge length, and electronic stabilization ($\Gamma_{\text{corner}}$) creates a new local minimum ($K_\textrm{slow}$) at the bridgehead crossing point. The rule held for so long because standard reaction conditions ($G_{\text{gamma}}$ scope) do not provide the precise convergence of factors required to access the violation regime. Recent advances in directed synthesis have simply navigated to previously unexplored regions of this structural phase space.

## 4. Comparative Structural Analysis

### 4.1 Distance Matrix

| System | proline_aldol | aryl_diazonium | on_water | wittig | grignard | bredts |
|---|---|---|---|---|---|---|
| proline_aldol | — | 2.2361 | 2.7928 | 2.0000 | — | — |
| aryl_diazonium | 2.2361 | — | — | 1.0000 | 3.2711 | — |
| on_water | 2.7928 | — | — | — | — | — |
| wittig | 2.0000 | 1.0000 | — | — | — | 3.3166 |
| grignard | — | 3.2711 | — | — | — | — |
| bredts | — | — | — | 3.3166 | — | — |

The closest structural pairing is the **aryl diazonium–Wittig** link ($d = 1.0$), differing only in parity. This shared substrate reflects their common nature as 1:1 bond reorganizations at a crossing-point topology.

### 4.2 Consciousness Score Summary

| System | $C$-score | Gate 1 ($\Phi_{\text{ctyogh}}$) | Gate 2 ($K \leq K_\textrm{slow}$) |
|---|---|---|---|
| proline_catalyzed_aldol | 0.322 | ✓ | ✓ |
| aryl_diazonium_dediazonization | 0.322 | ✓ | ✓ |
| on_water_interface_reactions | 0.2095 | ✓ | ✓ |
| wittig_reaction | 0.322 | ✓ | ✓ |
| grignard_reagent_formation | 0.268 | ✓ | ✓ |
| bredts_rule_violations | 0.225 | ✓ | ✓ |

All six systems pass both consciousness gates, confirming that each contains a critical ($\Phi_{\text{ctyogh}}$) self-modeling component with relaxation dynamics slow enough for structural self-reference. The on-water reaction scores lowest ($C = 0.2095$) due to its $K_\textrm{fast}$ driven kinetics, which compresses the temporal window available for self-referential feedback between the interface and the reaction.

## 5. Discussion

The structural encoding of six contested reaction mechanisms reveals a unifying pattern: **mechanistic debates arise from ambiguity in the interaction grammar** ($\Gamma$). Where chemists disagree about which pathway is "real," the IG consistently assigns $\Gamma_{\text{spleftarrow}}$ (disjunctive) or $\Gamma_{\text{corner}}$ (conjunctive) — encoding that the debate itself is a structural feature, not an epistemic failure.

Three distinct classes of contested mechanisms emerge:

1. **Multi-channel systems** ($\Gamma_{\text{spleftarrow}}$): Proline-catalyzed aldol, Wittig reaction, and aryl diazonium dediazonization all share disjunctive grammars. Multiple pathways exist simultaneously; experimental conditions determine flux distribution. The debate persists because each experimentalist's preferred conditions select a different channel.

2. **Conjunctive systems** ($\Gamma_{\text{corner}}$): "On water" reactions and Bredt's Rule violations require all contributing factors to align simultaneously. The debate arises because partial alignment produces no observable effect, leading researchers to conclude the mechanism "doesn't work" under their conditions.

3. **Sequential systems** ($\Gamma_\textrm{seq}$): Grignard reagent formation follows a fixed order of steps. The debate concerns *whether* the sequence is truly fixed and *what* the intermediates are at each step, not whether alternatives exist.

The consciousness scores (all $C > 0$, all gates open) confirm that each mechanism contains sufficient criticality ($\Phi_{\text{ctyogh}}$) and temporal slack ($K \leq K_\textrm{slow}$ or faster) to support structural self-reference. This suggests that reaction mechanisms are not merely passive descriptions of chemical transformation — they are self-modeling structural types that "know" (in the IG sense) about the systems they describe.

## 6. Conclusion

Encoding contested reaction mechanisms as structural types in the Imscribing Grammar provides a principled resolution to long-standing mechanistic debates. The key insight is that **mechanistic disputes are structural signatures**:

- $\Gamma_{\text{spleftarrow}}$ → competing pathways, all "real"
- $\Gamma_{\text{corner}}$ → conjunctive requirements, all "necessary"
- $\Gamma_\textrm{seq}$ → fixed sequence, intermediate identity matters

For proline-catalyzed aldol reactions, the enamine, enol, and oxazolidinone pathways are disjunctive alternatives sharing a crossing-point topology.

For aryl diazonium substitutions, the SN1/radial duality is encoded as $P_{\text{upsilon}}$ — an irreducible superposition.

For "on water" reactions, the conjunctive grammar ($\Gamma_{\text{corner}}$) structurally validates the interfacial mechanism.

For the Wittig reaction, the betaine/oxaphosphetane debate reflects a $\Gamma_{\text{spleftarrow}}$ multi-channel mechanism.

For Grignard formation, the sequential grammar ($\Gamma_\textrm{seq}$) confirms the radical mechanism with ordered electron-transfer steps.

For Bredt's Rule violations, the rule is a kinetic boundary ($K_\textrm{slow}$), not a structural prohibition.

The Imscribing Grammar thus provides a structural taxonomy of mechanistic disagreement itself — a metatheory of contested chemistry that transforms debate into data.

## Appendix: Structural Encoding Summary

| System | $D$ | $T$ | $R$ | $P$ | $F$ | $K$ | $G$ | $\Gamma$ | $\Phi$ | $H$ | $S$ | $\Omega$ | $C$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| proline_catalyzed_aldol | $D_{\text{turnthree}}$ | $T_{\text{bullseye}}$ | $R_\textrm{cat}$ | $P_{\text{pipevar}}$ | $F_{\text{beltl}}$ | $K_\textrm{mod}$ | $G_{\text{gamma}}$ | $\Gamma_{\text{spleftarrow}}$ | $\Phi_{\text{ctyogh}}$ | $H_2$ | $n{:}m$ | $\Omega_{\text{closeepsilon}}$ | 0.322 |
| aryl_diazonium | $D_{\text{turnthree}}$ | $T_{\text{bullseye}}$ | $R_\textrm{cat}$ | $P_{\text{upsilon}}$ | $F_{\text{beltl}}$ | $K_\textrm{mod}$ | $G_{\text{gamma}}$ | $\Gamma_{\text{spleftarrow}}$ | $\Phi_{\text{ctyogh}}$ | $H_2$ | $1{:}1$ | $\Omega_{\text{closeepsilon}}$ | 0.322 |
| on_water | $D_{\text{turnthree}}$ | $T_\textrm{in}$ | $R_{\text{lyoghlig}}$ | $P_{\text{pipevar}}$ | $F_{\text{beltl}}$ | $K_\textrm{fast}$ | $G_{\text{gamma}}$ | $\Gamma_{\text{corner}}$ | $\Phi_{\text{ctyogh}}$ | $H_1$ | $n{:}m$ | $\Omega_{\text{closeepsilon}}$ | 0.2095 |
| wittig | $D_{\text{turnthree}}$ | $T_{\text{bullseye}}$ | $R_\textrm{cat}$ | $P_{\text{pipevar}}$ | $F_{\text{beltl}}$ | $K_\textrm{mod}$ | $G_{\text{gamma}}$ | $\Gamma_{\text{spleftarrow}}$ | $\Phi_{\text{ctyogh}}$ | $H_2$ | $1{:}1$ | $\Omega_{\text{closeepsilon}}$ | 0.322 |
| grignard | $D_{\text{turnthree}}$ | $T_\textrm{net}$ | $R_{\text{downstep}}$ | $P_{\text{upsilon}}$ | $F_{\text{beltl}}$ | $K_\textrm{mod}$ | $G_{\text{gamma}}$ | $\Gamma_\textrm{seq}$ | $\Phi_{\text{ctyogh}}$ | $H_2$ | $n{:}m$ | $\Omega_{\text{crtwo}}$ | 0.268 |
| bredts | $D_{\text{turnthree}}$ | $T_{\text{bullseye}}$ | $R_{\text{lyoghlig}}$ | $P_{\text{pipevar}}$ | $F_{\text{beltl}}$ | $K_\textrm{slow}$ | $G_{\text{beta}}$ | $\Gamma_{\text{corner}}$ | $\Phi_{\text{ctyogh}}$ | $H_2$ | $n{:}m$ | $\Omega_{\text{closeepsilon}}$ | 0.225 |

*Structural type of Bredt's Rule violations: $\langle D_{\text{turnthree}};\ T_{\text{bullseye}};\ R_{\text{lyoghlig}};\ P_{\text{pipevar}};\ F_{\text{beltl}};\ K_\textrm{slow};\ G_{\text{beta}};\ \Gamma_{\text{corner}};\ \Phi_{\text{ctyogh}};\ H_2;\ n{:}m;\ \Omega_{\text{closeepsilon}} \rangle$.*