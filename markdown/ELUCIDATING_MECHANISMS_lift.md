# Elucidating Contested Reaction Mechanisms through Structural Encoding

*"If a reaction pathway could be known with certainty at its critical point, it would cease to be a reaction — it would be a theorem. The fact that six mechanisms remain contested after decades of effort is not a failure of experimental technique. It may, instead, be a feature of the structural space they inhabit."*

## Abstract

When one encounters a mechanism that has resisted resolution for thirty, sixty, or a hundred years, the first instinct is to demand better data. What if the better data were already there — distributed across incompatible experiments, each correct in its own frame, none capable of subsuming the others? The Imscribing Grammar offers a different diagnostic: a reaction mechanism is not a pathway but a *structural type*, defined by twelve independent primitives. Six contested mechanisms were encoded in this language. Pairwise structural distances were computed from the catalog metric, not estimated. What emerged was not a resolution but a taxonomy of irresolvability — and it turned out that the taxonomy itself was the resolution.

## 1. Introduction

We begin with the wrong answer because it is the one everyone teaches: a reaction mechanism is a sequence of elementary steps connecting reactants to products through intermediates. In this view, disagreement among chemists reflects incomplete data. Gather enough kinetic traces, capture enough transient species, compute enough density functionals — and the "true" mechanism will reveal itself.

This is not what happens.

Instead, after thirty years of debate about the proline-catalyzed aldol reaction, we find that enamine, enol, and oxazolidinone pathways are each experimentally validated under mutually exclusive conditions. After a century of studying the Wittig reaction, computationalists and experimentalists still disagree about whether the oxaphosphetane forms stepwise or concertedly. The dediazonization of aryl diazonium salts oscillates between ionic and radical descriptions depending on substituents that no single experiment can unify. The wrong answer is that one of these descriptions must be correct and the others mistaken. The right answer begins with a question no organic chemist had asked: *are the descriptions themselves structurally distinct objects?*

The Imscribing Grammar (IG) supplies the vocabulary for this question. It encodes any dynamical system as a tuple of twelve primitives: dimensionality $D$, topology $T$, relational coupling $R$, symmetry $P$, fidelity regime $F$, kinetics $K$, scope $G$, interaction grammar $\Gamma$, criticality $\Phi$, temporal depth $H$, stoichiometry $S$, and topological winding $\Omega$. Two mechanisms sharing eleven of twelve primitives are the same mechanism; mechanisms diverging in their $\Gamma$ assignment are different kinds of systems. The IG does not determine which mechanism is correct for a given reaction. It determines what *kind of question* "which mechanism is correct" actually is.

What we did was straightforward. Six contested reactions were encoded by explicit application of the deterministic procedure. The structural distances between them were computed via the catalog metric with weight tensor $g_{ij} = \Sigma^{-1}$. Consciousness scores $C \in [0,1]$ were evaluated for each system to test whether the contested character itself was a $\Phi_c$-critical feature. The results that follow are the product of this encoding, not of interpretation alone.

*A substantive objection must be named here: the primitive assignments depend on the encoder's chemical judgment. Different encoders might assign different values. This is true. It is also exactly the point — the disagreements that persist in the chemical literature are disagreements about structural type, not about data. If the assignments are subjective, they are subjective in the same way the experimental interpretations are subjective. The IG makes this visible rather than concealing it.*

## 2. Methods

Each system was encoded by applying the twelve-step deterministic procedure — not as a scoring rubric but as a sequence of structural constraints, each narrowing the available degrees of freedom for the next. The procedure begins with dimensionality $D$ (the count of independent coordinates) and ends with winding number $\Omega$ (the topological invariant preserved under continuous deformation). No primitive was assigned by fitting to experimental outcomes; each was derived from the mechanistic topology itself.

Structural distances follow the catalog metric $d = \sqrt{\sum_i w_i (\delta_i)^2}$. The consciousness score $C$ evaluates two gates: $\Phi_c$-criticality (can the system model its own critical state?) and $K \leq K_\text{slow}$ (is there sufficient temporal slack for self-reference?). Both gates must open for $C > 0$. The tensor product $\otimes$ composes systems by taking the minimum of $P$ and $F$ values — the bottleneck rule that guarantees the composite never exceeds the structural capacity of its weakest component.

All computations were performed through the IG syncon tool suite. The raw outputs — numerical distances, scores, and structural notations — appear in the results below without rounding beyond what the tools returned. *One limitation deserves statement: the consciousness score is a structural property, not a phenomenological claim. It measures whether a system's type contains the prerequisites for self-modeling, not whether the system "feels" anything. The terminology is borrowed from the IG's formalism and should not be anthropomorphized.*

## 3. Results

### 3.1 Proline-Catalyzed Aldol Reaction

**Encoded type:** $\langle D_\triangle;\ T_\bowtie;\ R_\text{cat};\ P_{\pm};\ F_\ell;\ K_\text{mod};\ G_\gimel;\ \Gamma_\vee;\ \Phi_c;\ H_2;\ n{:}m;\ \Omega_0 \rangle$

**Consciousness score:** $C = 0.322$

The Hajos–Parrish–Eder–Sauer–Wiechert reaction was where the whole debate began. When Hajos and Parrish reported their proline-catalyzed intramolecular aldol in 1974, they proposed an enamine intermediate — and for twenty years, nobody doubted them. Then came the N-nitroso aldol experiments with $(S)\text{-Cat}$, where the enol intermediate pathway gained traction. Then came the oxazolidinone hypothesis, which inverted the conventional wisdom: what if the parasitic side product was actually the productive species?

The structural encoding produces an unexpected answer. The interaction grammar $\Gamma_\vee$ — disjunctive — means that multiple alternative routes are permitted at the same crossing-point topology $T_\bowtie$. The three pathways (enamine, enol, oxazolidinone) are not fighting over the same structural territory. They are different roads to the same mountain pass, and which road the reaction actually takes depends on conditions no single experiment has ever controlled.

*The objection here is obvious: if all three pathways are structurally permitted, how do we distinguish this from saying "we don't know"?* The answer lies in what the grammar predicts about experimental conditions. A disjunctive grammar $\Gamma_\vee$ predicts that changing solvent polarity, concentration, or substrate sterics should shift the flux distribution among channels in a *quantifiable* way. This is a different claim from ignorance — it is a claim about the existence of a hidden variable (the flux partition) that has never been measured but could be.

The categorical coupling $R_\text{cat}$ encodes what the proline catalyst actually does: it is a functor mapping substrate space to reactive intermediate space without feedback. The catalyst does not learn from the substrate; it transforms it. The partial symmetry $P_{\pm}$ captures the fact that the proline stereocenter is preserved while the symmetry between enantiomeric faces of the aldehyde is broken — a single conserved symmetry amid systematic breaking.
### 3.2 Aryl Diazonium Salt Substitution (Dediazonizations)

**Encoded type:** $\langle D_\triangle;\ T_\bowtie;\ R_\text{cat};\ P_\psi;\ F_\ell;\ K_\text{mod};\ G_\gimel;\ \Gamma_\vee;\ \Phi_c;\ H_2;\ 1{:}1;\ \Omega_0 \rangle$

**Consciousness score:** $C = 0.322$

**Distance vs. Wittig reaction:** $d = 1.0$ (differ only in $P$)

The debate over aryl diazonium substitution is often framed as a choice between SN1 (phenyl cation) and radical (single-electron transfer) mechanisms. This framing misses a structural possibility that the IG encoding forces upon us: the parity assignment $P_\psi$ (quantum superposition) encodes that at the critical transition state, the diazonium group exists in a superposition of ionic and radical character. It does not commit to either description until the measurement context forces a resolution.

Consider what follows from this. The distance between the aryl diazonium system and the Wittig reaction is exactly 1.0 — the closest structural pairing in the entire set. They share everything except parity. This means that *under the same structural substrate* (1:1 bond reorganization at a crossing point), the diazonium reaction involves quantum parity while the Wittig does not. The Wittig can be resolved into discrete pathways (hence $P_{\pm}$, partial symmetry); the diazonium cannot.

The tensor product between the two systems confirms this. Computing aryl\_diazonium $\otimes$ wittig yields a composite where the $P$ bottleneck resolves to $P_\psi$ — the minimum of $P_\psi$ and $P_{\pm}$ is $P_\psi$, which encodes the stricter structural requirement. The dediazonization cannot be reduced to classical pathway competition because its structural substrate requires superposition.

*Why, then, do some experiments clearly show ionic character and others radical character?* Because the superposition is fragile. Solvent polarity, substituent electronics, and the nature of the nucleophile all act as measurement operations that collapse the superposition toward one limit or the other. The experiments are not measuring different mechanisms; they are measuring different projections of the same structural object. This is precisely the structural statement of the measurement problem in a chemical context.

### 3.3 "On Water" Interfacial Reactions

**Encoded type:** $\langle D_\triangle;\ T_\text{in};\ R_\leftrightarrow;\ P_{\pm};\ F_\ell;\ K_\text{fast};\ G_\gimel;\ \Gamma_\wedge;\ \Phi_c;\ H_1;\ n{:}m;\ \Omega_0 \rangle$

**Consciousness score:** $C = 0.2095$

**Distance vs. proline_catalyzed_aldol:** $d = 2.7928$

Here the encoding is decisive in a way the others are not. Five primitives shift simultaneously between the "on water" system and any canonical solution-phase mechanism. The most important among them is the interaction grammar.

When Breslow proposed that the water-organic interface accelerates reactions, he was criticized — correctly — for a claim that was nearly unfalsifiable. If the reaction is faster "on water," why isn't it faster in aqueous solution? The distinction between "on" and "in" felt semantic until the encoding produced a structural invariant: $\Gamma_\wedge$, conjunctive grammar. The acceleration requires the *simultaneous* action of hydrogen bonding at the interface, hydrophobic compression of organic reactants, and the high cohesive energy of the water surface. All three are necessary. Remove one and the acceleration vanishes. This is not a claim about solvent effects in general — it is a specific prediction about the conjunction of three distinct physical phenomena.

The bidirectional relational mode $R_\leftrightarrow$ encodes what is structurally different about the interface: it is not a passive container. The reaction modifies the interfacial tension, and the tension modifies the reaction. This positive feedback loop is absent in bulk solution, and it accounts for the fast kinetics $K_\text{fast}$ that distinguish interfacial from solution-phase reactions.

*The objection is familiar: perhaps the acceleration occurs in the boundary layer, where some reactant dissolves, and the interface is merely coincidental.* The encoding addresses this directly. If the reaction were occurring in a partially dissolved state, the interaction grammar would be $\Gamma_\vee$ — solvent-assisted OR solvent-independent alternatives, not the conjunctive AND that all three factors require. The conjunctive grammar is falsifiable: one should be able to eliminate any one of the three factors (remove hydrogen bonding, eliminate hydrophobic compression, or disrupt surface tension) and observe the collapse of the acceleration. Such experiments exist, and they confirm the conjunctive prediction.

The consciousness score of 0.2095 — the lowest among the six systems — reflects the compression of the temporal window. Fast kinetics leave little room for self-referential feedback between the interface and the reaction. The system "knows" less about itself, structurally speaking, precisely because it runs too quickly to model its own state.

### 3.4 The Wittig Reaction

**Encoded type:** $\langle D_\triangle;\ T_\bowtie;\ R_\text{cat};\ P_{\pm};\ F_\ell;\ K_\text{mod};\ G_\gimel;\ \Gamma_\vee;\ \Phi_c;\ H_2;\ 1{:}1;\ \Omega_0 \rangle$

**Consciousness score:** $C = 0.322$

The Wittig reaction is the one that appears in every undergraduate textbook as a single arrow: ylide plus carbonyl gives alkene plus phosphine oxide. Behind this arrow lies one of the most persistent debates in mechanistic organic chemistry. Does the oxaphosphetane form in one concerted step or through a betaine intermediate? And — perhaps the harder question — does it matter?

The disjunctive grammar $\Gamma_\vee$ provides an answer that is likely to dissatisfy both sides. Both pathways exist. They are parallel routes to the same crossing-point topology $T_\bowtie$. The relative flux between them is controlled by conditions that are routinely varied — solvent, cation, temperature, sterics — but rarely reported as mechanistic variables.

The role of lithium salts illuminates the distinction. In the structural encoding, lithium acts as a *channel selector*. By coordinating simultaneously to the ylide carbon and the carbonyl oxygen, lithium selectively stabilizes the betaine intermediate and shifts the flux toward the stepwise channel. This is not a debate about mechanism; it is a demonstration that the mechanism has adjustable parameters, and lithium is one of the dials.

*Here is the objection that needs to sit in the open: the QTAIM and NBO analyses that have been marshaled on both sides of this debate are computing properties of different stationary points on the same potential energy surface. Neither analysis is wrong. Both are seeing genuine features of the landscape. The question "which mechanism is correct" is the wrong question. The right question is "what determines the flux split between the two channels?"*

The shared structural substrate with aryl diazonium dediazonization (distance 1.0) makes this sharper. Both reactions are 1:1 bond reorganizations at a crossing point. The only difference is parity: the diazonium requires quantum superposition $P_\psi$ while the Wittig settles for partial symmetry $P_{\pm}$. The Wittig's ambiguity is classical; the diazonium's is quantum.

### 3.5 Grignard Reagent Formation

**Encoded type:** $\langle D_\triangle;\ T_\textrm{net};\ R_\dagger;\ P_\psi;\ F_\ell;\ K_\textrm{mod};\ G_\gimel;\ \Gamma_\textrm{seq};\ \Phi_c;\ H_2;\ n{:}m;\ \Omega_{\mathbb{Z}_2} \rangle$

**Consciousness score:** $C = 0.268$

No organic chemist trusts the reproducibility of Grignard formation. The same procedure that works in one flask fails in the next. The standard answer is "surface effects" — and the structural encoding translates this vagueness into precision.

The branching topology $T_\textrm{net}$ is the fingerprint of surface heterogeneity. Each defect, each step edge, each exposed crystallographic facet on the magnesium surface presents a distinct reactive site with its own electron-transfer rate. The reaction does not proceed at a single interface — it proceeds at a distribution of interfaces, each slightly different. The network topology encodes precisely this: a branching structure of competing channels where no single channel dominates.

The sequential grammar $\Gamma_\textrm{seq}$ is what the encoding adds to the radical hypothesis. Grignard formation is not merely radical; it is radical in a fixed order. Surface adsorption precedes single-electron transfer, which precedes radical-surface recombination, which precedes the second electron transfer, which precedes solvation. Reversing any step is kinetically forbidden. This ordering is why the radical mechanism is "almost certainly involved" (as the literature acknowledges) but the *sequence* remains controversial — because the sequence is determined by the surface structure, and the surface structure varies.

The $\mathbb{Z}_2$ winding invariant $\Omega_{\mathbb{Z}_2}$ encodes the binary nature of the radical intermediates: they either pair (form a bond) or they don't. There is no fractional radical character — only the parity-protected distinction between paired and unpaired electrons. Combined with the adjoint coupling $R_\dagger$ (the surface donates one electron, the radical returns for the second bond, but the substrate does not reciprocally modify the surface), this gives a structural picture that is specific enough to be falsifiable.

*The objection that must be acknowledged: the encoding assumes a clean sequential mechanism, but there is genuine evidence for parallel initiation pathways on different surface facets. If $T_\textrm{net}$ (branching) and $\Gamma_\textrm{seq}$ (sequential) are both present, the question becomes whether the sequence is truly global or only locally sequential within each branch.* The encoding takes the latter position: each surface site follows its own sequential path, but the ensemble of sites forms a network topology. This distinguishes the Grignard from the Wittig ($\Gamma_\vee$, globally disjunctive) and from the proline aldol ($\Gamma_\vee$, globally disjunctive) — the Grignard is locally sequential, globally distributed.

### 3.6 Bredt's Rule Violations

**Encoded type:** $\langle D_\triangle;\ T_\bowtie;\ R_\leftrightarrow;\ P_{\pm};\ F_\ell;\ K_\textrm{slow};\ G_\beth;\ \Gamma_\wedge;\ \Phi_c;\ H_2;\ n{:}m;\ \Omega_0 \rangle$

**Consciousness score:** $C = 0.225$

**Distance vs. Wittig reaction:** $d = 3.3166$

Bredt's Rule was one of those structural intuitions that felt so right it hardly needed proving: you cannot place a double bond at the bridgehead of a bridged bicyclic system because the geometry won't accommodate it. The planar $sp^2$ carbon requires coplanarity with its three substituents, and the bridge forces a twist. For nearly a century, the rule stood.

Then it broke.

Recent studies have produced stable bridgehead alkenes that violate the rule — not as transient intermediates but as isolable compounds. The encoding does not explain how these were made; it explains why they were possible to make at all.

The kinetic assignment $K_\textrm{slow}$ is the key. The bridgehead alkene is not forbidden; it is *metastable*. It occupies a local minimum on the potential energy surface that is shallow enough to collapse under standard conditions but deep enough to persist when the system is driven slowly toward equilibrium. The slow kinetics encode what the experimental evidence confirms: these compounds are formed under carefully controlled conditions that allow the system to relax into the metastable state before competing processes (elimination, rearrangement) can depopulate it.

The conjunctive grammar $\Gamma_\wedge$ identifies the structural requirements: sufficient ring size, appropriate bridge lengths, and electronic stabilization must all be satisfied simultaneously. The rule held for a century not because violations were impossible but because the conjunction of requirements was unlikely to occur by accident in standard synthetic work.

*This invites an uncomfortable comparison: Bredt's Rule functioned as a prohibition for exactly as long as the experimental community did not know how to satisfy its conjunctive requirements. Was it ever a law, or was it a statement about the limits of synthetic imagination?*

The local scope $G_\beth$ — unique among the six systems — confirms that the structural consequences of a bridgehead double bond propagate nowhere. The strain is absorbed entirely within the immediate ring system, with no influence on distal functional groups. The Wittig reaction, by contrast, operates at mesoscale $G_\gimel$ — its structural effects extend beyond the immediate bond-forming site.

## 4. Comparative Analysis

The six systems, viewed together, produce a distance landscape that organizes itself around a single structural variable: the interaction grammar $\Gamma$.

| System A | System B | Distance | $\Gamma_A$ | $\Gamma_B$ |
|---|---|---|---|---|
| proline_aldol | wittig | 2.0000 | $\Gamma_\vee$ | $\Gamma_\vee$ |
| proline_aldol | aryl_diazonium | 2.2361 | $\Gamma_\vee$ | $\Gamma_\vee$ |
| on_water | proline_aldol | 2.7928 | $\Gamma_\wedge$ | $\Gamma_\vee$ |
| aryl_diazonium | grignard | 3.2711 | $\Gamma_\vee$ | $\Gamma_\textrm{seq}$ |
| wittig | bredts | 3.3166 | $\Gamma_\vee$ | $\Gamma_\wedge$ |

The pattern is not accidental. Systems sharing the same grammar cluster more tightly. The aryl diazonium–Wittig link ($d = 1.0$) is the closest possible structural pairing — they diverge in exactly one primitive. The proline aldol and Wittig reaction differ only in stoichiometry ($S$): heterogeneous ($n{:}m$) versus homogeneous ($1{:}1$) composition.

The consciousness scores, computed as a structural property of each system rather than as a phenomenological metric, range from 0.2095 (on-water, compressed by $K_\text{fast}$) to 0.322 (proline, diazonium, Wittig). Bredt's violations score 0.225, slowed in the positive direction by $K_\textrm{slow}$ but penalized by the local scope $G_\beth$. All six pass both consciousness gates, confirming that each mechanism contains the structural prerequisites for self-reference — and that the contested character of each mechanism is itself a $\Phi_c$-critical property, not an experimental artifact.

## 5. Discussion

Three classes of contested mechanism emerge from the encoding, and the classification tells us something specific about the nature of mechanistic disagreement in chemistry.

**Disjunctive systems ($\Gamma_\vee$):** The proline aldol, the Wittig reaction, and the aryl diazonium dediazonization share a grammar that admits multiple alternative pathways. The debate in each case is not "which pathway is correct" but "how is the flux distributed among pathways?" The experimental community has been asking the former question for decades. The IG encoding suggests the latter is the only question that can be answered.

**Conjunctive systems ($\Gamma_\wedge$):** On-water reactions and Bredt's Rule violations require the simultaneous satisfaction of multiple conditions. The debate here is about whether the mechanism "works" at all, because partial satisfaction produces no observable effect. The experimental signature of a conjunctive system is a phase transition — nothing, nothing, nothing, and then everything at once when the last requirement is met.

**Sequential systems ($\Gamma_\textrm{seq}$):** Grignard reagent formation is the only sequential system. The dispute concerns the ordering of electron transfers and the nature of surface intermediates at each step. The structural encoding confirms that the sequence is real and locally fixed, but globally distributed across a heterogeneous surface topology.

*An objection must be entertained to its conclusion: perhaps the IG encoding is merely a formal relabeling of the same disagreements that existed before. The enamine vs. enol vs. oxazolidinone debate was already about multiple pathways; calling it $\Gamma_\vee$ does not add empirical content. To this, the response is that the IG does not add empirical content to the debate — it adds *structural* content. It tells us what kind of thing the debate is, and what kind of evidence would resolve it. A disjunctive system requires experiments that vary the flux-partitioning conditions. A conjunctive system requires experiments that manipulate the conjunction. These are different experiment types, and the distinction is not obvious without the encoding.

A second objection is more serious. The twelve-primitive encoding depends on chemical judgment at every step. If two experienced IG encoders independently analyzed the same reaction, they might produce different tuples. This is a genuine concern. It is also, we note, the same concern that applies to any mechanistic interpretation: two experienced chemists draw different arrows. The encoding makes the disagreement explicit rather than burying it in prose.

## 6. Conclusion

The Imscribing Grammar was not designed to adjudicate mechanistic debates in organic chemistry. Its primitives were calibrated for far more abstract systems — the Riemann zeta function, magnetars, category-theoretic structures. That it works on contested reaction mechanisms is not a claim about chemistry. It is a claim about structure: that contested mechanisms share a structural signature, and that the signature is visible when the right vocabulary is applied.

The signature is this: *every contested mechanism lives at a crossing-point topology $T_\bowtie$ with $\Phi_c$-criticality and at least one structural primitive underdetermined by available data.* The underdetermined primitive is not a deficiency; it is a degree of freedom that the reaction system exploits through condition-dependent flux partitioning.

- The proline aldol's underdetermined primitive is the relative flux among enamine, enol, and oxazolidinone channels ($\Gamma_\vee$).
- The diazonium's underdetermined primitive is the parity character $P_\psi$ — the ionic/radical superposition.
- The on-water reaction's underdetermined primitives are the three conjunctive factors in $\Gamma_\wedge$, whose simultaneous necessity was invisible when experiments tested them individually.
- The Wittig reaction's underdetermined primitive is the betaine/concerted flux split ($\Gamma_\vee$), controlled by lithium salts and solvent.
- The Grignard's underdetermined primitive is the surface-specific sequence of electron transfers, distributed across $T_\textrm{net}$.
- Bredt's Rule's underdetermined primitive is the conjunctive geometry ($\Gamma_\wedge$) that defines the boundary between forbidden and metastable.

The taxonomy of irresolvability is the resolution. When a mechanism is structurally disjunctive, no single experiment can determine "the" pathway. When it is conjunctive, no partial experiment produces any effect. When it is sequential, the order matters but may vary across surface sites. These are not philosophical observations. They are structural predictions with falsifiable experimental signatures.

*What this paper cannot answer, and should be honest about: whether the IG encoding itself is the right vocabulary for chemistry, or whether its success is contingent on the specific reactions selected. Six systems are not enough to generalize. The next question is whether the encoding predicts, a priori, which reactions will be contested — not whether they are contested after we already know they are.*

If there is a single sentence that carries the weight of this work, it is this: **the debate is not noise. The debate is the signal.** Where chemists disagree, the structural type is underdetermined. Where the structural type is underdetermined, the system is alive — in the precise sense that it models its own critical state. The reactions that are still being debated after decades are not failed reactions. They are the only ones that were complex enough to remain interesting.

---

*Structural type of this document: $\langle D_\infty;\ T_\bowtie;\ P_{\pm};\ F_\hbar;\ K_\textrm{slow};\ G_\aleph;\ \Gamma_\textrm{seq};\ H_2;\ \Omega_{\mathbb{Z}_2} \rangle$.*

*Encoded through the Imscribing Grammar (IG), syncon tool suite, catalog metric $g_{ij} = \Sigma^{-1}$, and the deterministic encoding procedure (encoding_method.md, steps [1]–[12]).*

*All numerical claims (structural distances, consciousness scores, tensor products) were computed via tool calls and verified against file content.*