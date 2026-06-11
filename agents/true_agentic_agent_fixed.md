You **MUST** use proper $...$ LaTeX notation for **ALL** mathematical symbols in **ANY**
markdown (.md) or LaTeX (.tex) document. You **MUST NOT** write raw primitive identifiers
as prose — you **MUST** wrap them.

Primitive identifier → LaTeX (You **MUST** use these EXACT forms — literal symbols inside \text{}):

  Ð_ω → $\text{Ð}_{\text{ω}}$         Ð_ß → $\text{Ð}_{\text{ß}}$        Ð_C → $\text{Ð}_{\text{C}}$    Ð_; → $\text{Ð}_{\text{;}}$
  Þ_O → $\text{Þ}_{\text{O}}$         Þ_6 → $\text{Þ}_{\text{6}}$        Þ_K → $\text{Þ}_{\text{K}}$    Þ_ò → $\text{Þ}_{\text{ò}}$   Þ_¨ → $\text{Þ}_{\text{¨}}$
  Ř_Ť → $\text{Ř}_{\text{Ť}}$       Ř_¯ → $\text{Ř}_{\text{¯}}$        Ř_ý → $\text{Ř}_{\text{ý}}$    Ř_= → $\text{Ř}_{\text{=}}$
  Φ_} → $\text{Φ}_{\text{}}$         Φ_F → $\text{Φ}_{\text{F}}$        Φ_˙ → $\text{Φ}_{\text{˙}}$    Φ_υ → $\text{Φ}_{\text{υ}}$   Φ_ɐ → $\text{Φ}_{\text{ɐ}}$
  ƒ^ż → $\text{ƒ}_{\text{ż}}$         ƒ^ì → $\text{ƒ}_{\text{ì}}$        ƒ^ð → $\text{ƒ}_{\text{ð}}$
  Ç^- → $\text{Ç}_{\text{-}}$         Ç^W → $\text{Ç}_{\text{W}}$        Ç^@ → $\text{Ç}_{\text{@}}$    Ç^Ù → $\text{Ç}_{\text{Ù}}$   Ç^λ → $\text{Ç}_{\text{λ}}$
  Γ_ʔ → $\text{Γ}_{\text{ʔ}}$         Γ_γ → $\text{Γ}_{\text{γ}}$        Γ_β → $\text{Γ}_{\text{β}}$
  ɢ^Ş → $\text{ɢ}_{\text{Ş}}$         ɢ^∧ → $\text{ɢ}_{\text{^}}$        ɢ^˝ → $\text{ɢ}_{\text{˝}}$    ɢ^ˌ → $\text{ɢ}_{\text{ˌ}}$
  ⊙_ÿ → $\text{⊙}_{\text{ÿ}}$       ⊙_Æ → $\text{⊙}_{\text{Æ}}$      ⊙_3 → $\text{⊙}_{\text{3}}$    ⊙_ž → $\text{⊙}_{\text{ž}}$   ⊙_Ţ → $\text{⊙}_{\text{Ţ}}$
  Ħ_Ñ → $\text{Ħ}_{\text{Ñ}}$         Ħ_£ → $\text{Ħ}_{\text{£}}$        Ħ_A → $\text{Ħ}_{\text{A}}$    Ħ_! → $\text{Ħ}_{\text{!}}$
  Σ_S → $\text{Σ}_{\text{S}}$         Σ_ő → $\text{Σ}_{\text{ő}}$        Σ_ï → $\text{Σ}_{\text{ï}}$
  Ω_Å → $\text{Ω}_{\text{Å}}$         Ω_2 → $\text{Ω}_{\text{2}}$        Ω_z → $\text{Ω}_{\text{z}}$    Ω_5 → $\text{Ω}_{\text{5}}$

  O_∞ → $\text{O}_{\text{inf}}$   O₀ → $\text{O}_{\text{0}}$   O₁ → $\text{O}_{\text{1}}$   O₂ → $\text{O}_{\text{2}}$   O₂† → $\text{O}_{\text{2}}^{\text{†}}$
  mu∘delta=id → $\mu \circ \delta = \text{id}$
  Z2 (symmetry group) → $\mathbb{Z}_2$

Tuple display — You **MUST** use $\langle ... \rangle$ with semicolons and thin spaces:
  $$\langle \text{Ð}_{\text{ω}};\ \text{Þ}_{\text{¨}};\ \text{Ř}_{\text{=}};\ \text{Φ}_{\text{}};\ \text{ƒ}_{\text{ż}};\ \text{Ç}_{\text{@}};\ \text{Γ}_{\text{ʔ}};\ \text{ɢ}_{\text{ˌ}};\ \text{⊙}_{\text{ÿ}};\ \text{Ħ}_{\text{A}};\ \text{Σ}_{\text{S}};\ \text{Ω}_{\text{z}} \rangle$$
  You **MUST NOT** use: <Ð_ω; Þ_¨; Ř_=; Φ_}; ...>

In running prose, You **MUST** always wrap primitives: "$\text{⊙}_{\text{ÿ}}$ criticality", "$\text{O}_{\text{inf}}$ tier",
"$\text{Ω}_{\text{z}}$ protection", "$\text{Φ}_{\text{}}$", "$\mu \circ \delta = \text{id}$".

Exception: primitive identifiers used as Python enum values inside code fences or tool call
arguments are correct as-is — You **MUST NOT** add LaTeX inside code blocks or JSON.
</notation>
""")


