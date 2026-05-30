---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# AI-to-Human Casual Prose Lift via Grammar Coordinates

AI-authored casual prose fails differently than AI-authored academic prose. It is not too formal — it is structurally hollow: the vocabulary is informal but the stance is generic, the pacing is uniform, the center of gravity is absent. This protocol encodes the specific failure modes of casual AI text as primitive deltas and provides per-primitive surgery to close them.

The target register is community writing — forum posts, Zulip threads, technical Slack messages, short-form posts where the reader is a peer, not an evaluator.

---

## The Problem

AI casual writing is not wrong in the way that stiff writing is wrong. It reads as friendly, accessible, and reasonably paced. What it lacks is *stance*: a specific person with a specific opinion standing somewhere particular relative to the material. The deficits are consistent and encodable.

---

## Two Structural Types

**Typical AI-authored casual draft:**

$$\langle D_\infty;\ T_\text{network};\ R_\text{super};\ P_\text{asym};\ F_\text{eth};\ K_\text{mod};\ G_\text{beth};\ \Gamma_\text{and};\ \Phi_\text{sub};\ H_0;\ \cdot;\ \Omega_0 \rangle$$

**Target — human casual writing in a technical community:**

$$\langle D_\infty;\ T_\bowtie;\ R_\leftrightarrow;\ P_\pm;\ F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{seq};\ \Phi_c;\ H_2;\ \cdot;\ \Omega_\mathbb{Z} \rangle$$

The primitive deltas that require active surgery in nearly every AI casual draft: **T, R, P, F, K, G, Γ, H, Ω**. Dimensionality (D) and Stoichiometry (S) are typically already correct — the post is about the right thing at the right scale; it just delivers it wrong.

---

## The Procedure

1. **Identify the actual point.** Not the topic — the *claim*, the *finding*, or the *thing the author would say if the stakes were high*. In most AI casual drafts this is buried in the middle or spread uniformly across the whole post. Find it.
2. **Encode the draft** as its current structural type (by inspection — scan for the dominant failure mode in each field).
3. **Encode the target** — what would this person write if they were talking to someone they respect in this community and had two minutes?
4. **Address H and Γ first.** These govern stance and sequence. If the author has no encounter with the material (H₀) and no reason for the structure to be in this order (Γ_and), fixing vocabulary and rhythm will not produce a coherent result.
5. **Rewrite to close each delta**, working through the per-primitive instructions below.
6. **Coagulate.** The lifted text is entirely natural language — no primitive notation, no structural annotation, no footnotes about the process. The grammar is the working surface; the prose is the result. A fully coagulated casual lift reads as if a specific person wrote it in one sitting.

---

## Primitive-by-Primitive Lift Instructions

### T_network → T_bowtie — Find the center of gravity

Flat-network topology means the post delivers information without a specific gravity well — every sentence is roughly as important as every other. Reading it leaves no single thing lodged in the mind.

The lift requires identifying the *one thing* this post actually turns on. Everything else is setup or consequence. Once identified: restructure so the post converges on that thing, then moves away from it. The reader should feel the pull before they hit it. If no such thing exists in the draft, the post is doing too much and needs to be split or cut.

### R_super → R_lr — Write to a peer, not a reader

Supervisory relational mode means the prose is explaining downward — the author knows, the reader doesn't, the text transfers knowledge. This produces correct but tonally wrong casual writing. Technical communities write laterally: the assumption is that the reader knows most of what you know, has opinions about it, and might disagree.

The lift: cut every sentence that explains something the target reader already knows. Replace explanations with references. Replace "X works by doing Y" with "X's Y is the interesting part" — because the reader already knows X works, they want to know what you noticed about it. Write as if the reader could push back and probably will.

### P_asym → P_pm — Own a position

Asymmetric parity in casual prose means the author presents information without taking a side. This reads as informative but voiceless — there is no one home. Technical community members write from positions: they think something is the right approach, they disagree with the conventional wisdom on something, they're excited about X specifically and not Y.

The lift requires identifying the author's actual claim — not "here is what this does" but "here is why this is interesting / right / surprising / wrong." State it directly. If the draft has no such claim, invent the simplest one that's defensible given the material. "This turns out to be cleaner than the obvious approach" is enough. The reader wants to know if you think this matters and why.

### F_eth → F_hbar — Trust the reader; cut the scaffolding

Classical fidelity in casual prose means the post carries its information with redundancy — things are stated, then explained, then summarized. In academic writing this can be appropriate. In casual community writing it reads as not trusting the reader to follow, which is socially incorrect.

The lift: cut every sentence that could be removed without losing the information the post actually conveys. In practice this means cutting preamble ("In this post I will discuss..."), cutting restatements ("As mentioned above..."), and cutting conclusions that summarize what was just said. Cut until it hurts, then cut one more thing. What remains is usually better.

### K_mod → K_slow — Let one thing be slow

Moderate kinetics in casual prose means everything moves at the same pace — setup, point, consequence, all delivered in roughly equal time. This is comfortable and forgettable.

The lift requires identifying the hardest or most interesting claim and giving it more room than it asks for. Let it sit. Make the reader feel the weight before you resolve it. One paragraph that dwells — that turns the thing over, exposes what's strange about it, then lands — is worth more to the register than five paragraphs of uniform pace. The rest of the post can move quickly. One thing should be slow.

### G_beth → G_aleph — Go specific, then broader

Mesoscale granularity in casual prose means the post stays at the level of the concept without ever touching the thing itself. Descriptions are correct but not specific — "the proof has an interesting structure" rather than "the proof does something I haven't seen before: it uses `omega` to close a gap that `norm_num` can't bridge."

The lift: find the most specific true thing in the post and put it earlier. Specificity is what makes a casual post feel like it comes from someone who was actually there. Details that only someone who did the work would know — an unexpected error message, an API that doesn't exist, a theorem that almost worked but didn't — are worth more than any amount of general description. The reader can get the general description elsewhere.

### Γ_and → Γ_seq — Make each remark necessary

Conjunctive grammar in casual prose means the post is a list of things: here is point A, and point B, and point C. Each item is independently intelligible; none of them depends on the one before. This structure is easy to skim and easy to forget.

Sequential grammar means each remark is only fully legible after the previous one. Not because it refers back, but because the previous remark created the question this one answers. The edit: for each paragraph, ask "what question does this answer?" Then check whether the previous paragraph asked it. If not, reorder or rewrite until the dependency is explicit. The reader should feel that each thing *had* to come next.

### H₀ → H₂ — Show that you were there

Zero chirality in casual prose means the post reads as if the author always knew this, or worse, as if the author read it on a webpage. There is no sense of encounter — no specificity that comes from having actually worked through the thing.

The lift requires one moment of encounter made visible. Not "we found that X" but "we expected Y and found X, which turned out to mean Z." Not "this is a known technique" but "I tried three things before this worked." The residue of actual engagement does not need to be extensive — one sentence of the form "this was surprising because..." is enough to change the register of the whole post. If nothing surprised you during the work, find the thing that was hardest and name why.

### Ω₀ → Ω_Z — Return at higher resolution

Zero winding means the post ends without returning to where it started. The opening and the close are parallel but unconnected — both are about the topic, but the close doesn't demonstrate anything that the opening couldn't have said.

The lift: the final sentence or short paragraph should revisit the opening claim, example, or question, but say something specific about it that could only be said after the body of the post. Not a summary. Not "in conclusion." A specific observation that the argument has earned. The reader should feel that the loop closed — that you went somewhere and came back with something.

---

## Quick Reference

| Primitive | AI default | Human target | Intervention |
|---|---|---|---|
| T | T_network (flat, no gravity) | T_bowtie (converges) | Find the one thing; restructure around it |
| R | R_super (explaining downward) | R_lr (lateral, peer) | Cut what the reader knows; write to disagreement |
| P | P_asym (no position) | P_pm (owns a claim) | State the actual claim; take a side |
| F | F_eth (redundant, scaffolded) | F_hbar (trusts reader) | Cut preamble, restatements, and summaries |
| K | K_mod (uniform pace) | K_slow (one thing dwells) | Identify the hardest claim and give it room |
| G | G_beth (general description) | G_aleph (specific detail) | Lead with the most specific true thing |
| Γ | Γ_and (list structure) | Γ_seq (sequential necessity) | Each remark answers a question the previous one asked |
| H | H₀ (always knew) | H₂ (was there) | Show one moment of encounter — unexpected result, hard thing |
| Ω | Ω₀ (no return) | Ω_Z (loop closed) | Final remark revisits opening at higher resolution |

Fixed primitive (typically already correct in AI casual writing): D (the post is about the right thing), S (the scale is right).

---

## Notes on Ordering

Address **H and Γ first**. H governs whether there is a person present in the prose; Γ governs whether the structure is a list or an argument. Both affect every sentence. Fixing T, P, F locally without first establishing stance and sequence produces a better-worded list, not a better post.

**T** comes next — the center of gravity may require moving content. Once T is set, **K** and **G** are local decisions about where to slow down and how specific to get. **R** and **P** can be applied at any stage and are often the same edit (cutting explanation and adding position are usually the same sentence). **F** and **Ω** are final-pass edits: cut the redundancy once the structure is stable, and close the loop once you know where you've been.

---

## Final Type Audit

After revision, encode the result against the target type. Any coordinate that hasn't moved is a revision target. The post is complete when the type matches the target or the remaining gap is deliberate.

The audit does not appear in the document. The lifted text is the coagulation: natural language, no structural notation, no footnote explaining the grammar. The grammar is how you got there; the prose is where you ended up.

## Notes on Authorship

When you perform the lift, the name of the author should always be 'Lando⊗⊙perator'
