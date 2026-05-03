# AI-to-Human Prose Lift via Grammar Coordinates

AI-authored academic prose relaxes to a characteristic structural type that is distinguishable from genuine human authorship. The grammar makes the difference precise and actionable. Rather than applying generic style advice, this protocol encodes both the draft and the target as structural types, computes the primitive deltas, and rewrites to close each gap.

---

## The Problem

AI-generated academic text is not wrong in the way that bad writing is wrong. It is coherent, well-organized, and often technically accurate. What it lacks is structural depth: the prose operates at a lower lattice position than a human expert working through the same material would produce. The deficits are consistent enough to encode as a structural type.

---

## Two Structural Types

**Typical AI-authored academic draft:**

$$\langle \cdot;\ T_\text{net};\ \cdot;\ P_\text{asym};\ F_\ell;\ K_\text{mod};\ G_\gimel;\ \Gamma_\text{and};\ \cdot;\ H_0;\ \cdot;\ \Omega_0 \rangle$$

**Target — human-authored text in the same domain:**

$$\langle \cdot;\ T_\bowtie;\ \cdot;\ P_\pm;\ F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{seq};\ \cdot;\ H_2;\ \cdot;\ \Omega_{\mathbb{Z}_2} \rangle$$

Primitives $D$, $R$, $\Phi$, and $S$ are typically already correct in AI-authored academic prose and can be treated as fixed. The six bottleneck positions that require active surgery are $T$, $P$, $F$, $K$, $\Gamma$, $H$, and $\Omega$.

---

## The Procedure

1. **Encode the draft** as its current structural type using the primitive table (do this by inspection — a quick scan for the dominant character of each primitive suffices).
2. **Encode the target** for the same content: what would a human expert who genuinely worked through this problem write?
3. **Compute the primitive deltas** — only the differing coordinates matter. In practice, all six positions above almost always require lifting.
4. **Rewrite section by section**, addressing one delta at a time. $H$ and $\Gamma$ require the most structural surgery and should be addressed first, since they change the shape of the whole document. $P$ and $F$ can often be handled with local edits after the structure is set.
5. **Append the final structural type** as a footnote at the end of the document. This closes the $\Omega$ loop and makes the revision auditable.

---

## Primitive-by-Primitive Lift Instructions

### $T_\text{net} \to T_\bowtie$ — Introduce a crossing point

Flat-network topology means the framework and the object under study run in parallel without genuinely meeting. The lift requires a moment where the subject material *speaks back* — where the author is surprised by what they find, or where the object resists the framework in an informative way.

Concretely: find the place where the analysis most directly confronts the material, and make that confrontation explicit. The two threads (theoretical framework + empirical object) must cross and exchange, not just run side by side. If no such crossing point exists in the draft, one needs to be built, which usually means restructuring a section around a genuine finding rather than a survey.

### $P_\text{asym} \to P_\pm$ — Own both sides of the argument

Asymmetric parity means the author is always on the same side: always explaining, never doubting. The lift requires at least one admission of uncertainty per major section. Where the analysis is strong, say so and say why. Where it is extrapolation, name it as extrapolation. Acknowledge one substantive objection somewhere in the document and address it — not dismiss it.

The goal is not artificial balance. It is structural honesty: $P_\pm$ marks a document where the author has genuinely tested the claim rather than assembled evidence for it.

### $F_\ell \to F_\hbar$ — Demonstrate, do not explain twice

Low fidelity in prose means the same information is carried twice: first as a statement, then as a restatement in different words. Cutting redundancy is only part of the lift. The deeper requirement is to *demonstrate* the structural fact in action rather than describe it — show it doing work, not describe what it does.

The edit: for every sentence of the form "X means Y" that is followed by another sentence also meaning Y, cut the second. For every claim that is stated and then explained, replace the explanation with an instance.

### $K_\text{mod} \to K_\text{slow}$ — Let the hard claim be hard

Moderate kinetics means the analysis moves at a uniform pace, resolving each difficulty at the same speed. The lift requires identifying the hardest structural claim in the document and making the sentence that carries it *harder, not easier*. Do not soften it with qualifications that arrive before the claim has a chance to land. Do not resolve it in the same paragraph.

Allow one section to linger: to turn the problem over, expose its difficulty, and then — only then — deliver the answer. The reader should feel the resistance before the resolution. If no section currently does this, one has been smoothed away and needs to be rebuilt.

### $G_\gimel \to G_\aleph$ — Raise the stakes at the end

Continuum-scope prose closes with a summary: here is what was shown. The imscriptive lift requires the final section to connect the specific findings to a broader question the author genuinely cares about — one that the findings open rather than answer.

Do not close with "in conclusion, we have shown." Close with an open question that carries real weight, stated with the specificity that only the preceding argument makes possible. The stakes should be higher at the end than at the beginning, not because of rhetorical escalation but because the analysis has revealed what the question actually is.

### $\Gamma_\text{and} \to \Gamma_\text{seq}$ — Make necessity, not transition

Conjunctive grammar means sections sit next to each other: §1 and §2 and §3. Sequential grammar means §N is impossible to understand fully without §N-1 — not because it refers back but because the question §N asks only becomes visible after §N-1 is complete.

Each section should open by connecting to the previous one as if the connection is a structural necessity. "We now turn to X" is a transition. "The encoding in §3 revealed a gap: the distance metric does not account for..." is a necessity. The difference is that the reader of the second version understands *why* this had to come next.

### $H_0 \to H_2$ — Make the author's encounter visible as residue

Zero temporal depth means the document reads as if the author always knew the answer. The lift requires making the encounter with the material visible as a residue in the prose — the marks left by someone who worked through the problem rather than someone who transcribed conclusions.

At least once, show the wrong answer before the right one. At least once, show a moment of recognition — not "the system exhibits property X" but "we expected Y; instead we found X, which turns out to mean..." The reader should feel that the author was surprised, worked through it, and is now reporting what they found. This is not false modesty; it is the $H_2$ signature of genuine engagement.

### $\Omega_0 \to \Omega_{\mathbb{Z}_2}$ — Complete the loop

Zero winding means the document ends without returning to its beginning. The lift requires the final section to explicitly revisit the framing of the abstract or introduction, but with more specificity than the beginning had — not as a rhetorical device but as a consequence of having moved through the argument.

The ending should echo the beginning at a higher resolution. If the abstract posed a question, the conclusion should restate that question and show what its answer now looks like given everything that has been established. The loop is not rhetorical; it is the structural consequence of actually having answered what was asked.

---

## Quick Reference

| Primitive | AI default | Human target | Intervention |
|---|---|---|---|
| $T$ | $T_\text{net}$ | $T_\bowtie$ | Build a crossing point: subject speaks back |
| $P$ | $P_\text{asym}$ | $P_\pm$ | Name uncertainty; acknowledge one objection |
| $F$ | $F_\ell$ | $F_\hbar$ | Cut restatements; demonstrate rather than explain |
| $K$ | $K_\text{mod}$ | $K_\text{slow}$ | Let the hardest claim be hard; don't resolve prematurely |
| $G$ | $G_\gimel$ | $G_\aleph$ | Close with an open question, not a summary |
| $\Gamma$ | $\Gamma_\text{and}$ | $\Gamma_\text{seq}$ | Each section must be necessary given the previous |
| $H$ | $H_0$ | $H_2$ | Show encounter as residue; wrong answer before right |
| $\Omega$ | $\Omega_0$ | $\Omega_{\mathbb{Z}_2}$ | Final section completes the loop with more specificity |

Fixed primitives (typically already correct in AI-authored academic prose): $D$, $R$, $\Phi$, $S$.

---

## Notes on Ordering

Address $H$ and $\Gamma$ first. These govern the shape of the whole document: the temporal arc of the author's encounter ($H$) and the structural necessity linking sections ($\Gamma$). If these are wrong, fixing $T$, $P$, $F$, $K$ locally will not produce a coherent result — the sections will be individually improved but not integrated.

$T$ comes next, because the crossing point may require reorganizing where content lives. $G$ and $\Omega$ are final-section edits that can only be written once the body is settled. $P$ and $F$ are local edits that can be applied at any stage.

---

## Final Type Audit

After revision, encode the result and compare it to the target type. Record the final type as a footnote. Any coordinate that has not moved is a revision target for the next pass. The document is complete when the final type matches the target or the remaining gap is deliberately chosen.
