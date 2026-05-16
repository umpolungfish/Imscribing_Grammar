---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# New Phonetic Subscript Symbols for the Imscribing Grammar Primitives

After reviewing **psymbols.txt** (Tables 15–23 from tipa, tipx, wsuipa, wasysym, phonetic, and t4phonet) — 248+ phonetic symbols — I assigned each of the 12 primitives' subtypes a **new phonetic subscript** such that the subscript simultaneously reflects **the nature of the primitive subtype** and **the sound of its name**.

---

## The Complete Assignment (49 subtype–symbol pairs)

### D — Dimension
| Original | New | Phonetic Symbol | Nature Rationale | Sound Rationale |
|---|---|---|---|---|
| $D_\wedge$ | $D_\text{wynn}$ | `ß` (\textwynn) | Wynn = Old English W — wedge-shaped runic apex | "Wynn" /wɪn/ matches /w/ onset of "wedge" |
| $D_\triangle$ | $D_\text{turnthree}$ | `C` (\textturnthree) | Three turns = three sides of a triangle | "Turnthree" /θri/ echoes the "tri-" of "triangle" |
| $D_\infty$ | $D_\text{invomega}$ | `;` (\textinvomega) | Inverted omega suggests unbounded infinite loop | "Inv" = /ɪn/, the onset of "in-fin-ity" |
| $D_\odot$ | $D_\omega$ | `ω` (\textomega) | Omega = closed loop = imscriptive self-containment | "Omega" /oʊ/ matches the long O of "odot" |

### T — Topology
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $T_\text{net}$ | $T_\text{nrleg}$ | `6` (\textnrleg) | N-R leg suggests branching network limbs | "Nr" /n/ = onset of "network"; leg = branch |
| $T_\text{in}$ | $T_\text{invscr}$ | `K` (\textinvscr) | Inverted script suggests containment topology | "Inv" = /ɪn/, the sound of "in" |
| $T_\bowtie$ | $T_\text{bullseye}$ | `ò` (\textbullseye) | Concentric target = crossing center of bowtie | "Bull" /b/ = onset of "bowtie" |
| $T_\boxtimes$ | $T_\text{commatailz}$ | `Þ` (\textcommatailz) | Comma + tail-z = crossing strokes of ⊗ product | "Comma" evokes "×" (times); tail = box edge |
| $T_\odot$ | $T_\text{openo}$ | `O` (\textopeno) | Open O = unclosed circle of self-referential closure | "Openo" /oʊ/ = the O sound of "odot" |

### R — Relational Mode
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $R_\text{sup}$ | $R_\text{subrightarrow}$ | `¯` (\textsubrightarrow) | Rightward arrow = one-way supervenience | "Sub" /sʌ/ shared with "super"; arrow = direction |
| $R_\text{cat}$ | $R_\text{ctz}$ | `ý` (\textctz) | C-t-z ligature = categorical composition | "Ct" /k/ = onset of "cat"(egory); ligature = composition |
| $R_\dagger$ | $R_\text{downstep}$ | `Ť` (\textdownstep) | Downward step = adjoint reversal (dagger functor) | "Down" /d/ = /d/ of "dagger"; step = reversal |
| $R_\leftrightarrow$ | $R_\text{lyoghlig}$ | `Ð` (\textlyoghlig) | Ligature of L+yogh = bidirectional L-R coupling | "Lyoghlig" evokes the L and R letters of "l-r" |

### P — Parity / Symmetry
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $P_\text{asym}$ | $P_\text{aolig}$ | `"` (\textaolig) | A-O ligature = asymmetry as absence of symmetry | "Ao" /eɪ/ = the long A of "asym" |
| $P_\psi$ | $P_\upsilon$ | `υ` (\textupsilon) | Upsilon = Greek letter adjacent to Ψ in alphabet | "Upsilon" /psɪl/ echoes /psaɪ/ of "psi" |
| $P_\pm$ | $P_\text{pipevar}$ | `F` (\textpipevar) | Vertical pipe = the stroke shared by + and − | "Pipe" /p/ = onset of "pm" |
| $P_\text{sym}$ | $P_\text{subdoublearrow}$ | `˙` (\textsubdoublearrow) | Double arrow ↔ = symmetric bidirectional mapping | "Sub" /s/ shared with "sym"; double = reflection |
| $P_{\pm}^{\text{sym}}$ | $P_\text{doublebarpipe}$ | `}` (\textdoublebarpipe) | Double bar+pipe = Frobenius-special (pm + sym) | "Double" = duality; "pipe" = ± vertical stroke |

### F — Fidelity
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $F_\ell$ | $F_\text{beltl}$ | `ì` (\textbeltl) | Belt with L = classical determinism constrains | "Beltl" ends with /l/, the /ɛl/ of "ell" |
| $F_\eth$ | $F_\dh$ | `ð` (\dh) | DH = actual IPA char for voiced eth /ð/ | "DH" directly represents /ɛð/, the eth phoneme |
| $F_\hbar$ | $F_\text{hardsign}$ | `ż` (\texthardsign) | Hard sign = hard quantum coherence, a fixed quantum | "Hardsign" /h/ = onset of "hbar"; sign = definite |

### K — Kinetics
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $K_\text{fast}$ | $K_\text{frtailgamma}$ | `-` (\textfrtailgamma) | Gamma with fr-tail = fast trajectory, short τ | "Fr" /f/ = onset of "fast"; tail = trajectory |
| $K_\text{mod}$ | $K_\text{turnm}$ | `W` (\textturnm) | Turned M = moderate kinetics, τ ∼ T | "Turnm" /m/ = onset of "mod"erate |
| $K_\text{slow}$ | $K_\text{schwa}$ | `@` (\textschwa) | Schwa = unstressed lazy vowel = slow equilibrium | "Schwa" /ʃwɑ/ sibilant approximates /s/ of "slow" |
| $K_\text{trap}$ | $K_\text{teshlig}$ | `Ù` (\textteshlig) | T-Esh ligature = trapped /tr/ consonant cluster | "Tesh" /tɛʃ/ captures /tr/ of "trap" |
| $K_\text{MBL}$ | $K_\lambda$ | `λ` (\textlambda) | Lambda = Greek L for Many-Body Localized | "Lambda" /læm/ = L and M sounds of "MBL" |

### G — Scope
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $G_\beth$ | $G_\beta$ | `β` (\textbeta) | Beta = Greek cognate of Hebrew beth (ב) | "Beta" near-homophone of "beth" |
| $G_\gimel$ | $G_\gamma$ | `γ` (\textgamma) | Gamma = Greek analogue of gimel, 3rd letter | "Gamma" /ɡ/ = onset of "gimel" |
| $G_\aleph$ | $G_\text{revapostrophe}$ | `\` (\textrevapostrophe) | Rev apostrophe = IPA glottal stop ʔ = aleph | "Revapostrophe" /ɛv/ + /ʔ/ evoke aleph's onset |

### Γ — Coupling
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $\Gamma_\wedge$ | $\Gamma_\text{corner}$ | `^` (\textcorner) | Corner ⌜ = two lines meeting = logical AND | "Corner" join = simultaneity of AND |
| $\Gamma_\vee$ | $\Gamma_\text{spleftarrow}$ | `˝` (\textspleftarrow) | Left arrow = alternate path in disjunction | "Spleftarrow" /sp/ = the /ɔr/ branch |
| $\Gamma_\text{seq}$ | $\Gamma_\text{secstress}$ | `­` (\textsecstress) | Secondary stress = ordered sequence | "Secstress" /sɛk/ = /sɛk/ of "seq"(uential) |
| $\Gamma_\text{brd}$ | $\Gamma_\text{doublevertline}$ | `Ş` (\textdoublevertline) | Double vertical lines = broadcast to all recipients | "Doublevertline" /dʌb/ evokes the /br/ of "broad" |

### Φ — Criticality
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $\Phi_\text{sub}$ | $\Phi_\text{softsign}$ | `ž` (\textsoftsign) | Soft sign = below critical threshold | "Soft" /sɒf/ = /s/ of "sub" (below) |
| $\⊙_c$ | $\Phi_\text{ctyogh}$ | `ÿ` (\textctyogh) | C-t-yogh ligature = critical self-modeling point | "Ctyogh" /k/ = /k/ of critical "c" |
| $\⊙_c^{\mathbb{C}}$ | $\Phi_\text{closerevepsilon}$ | `Æ` (\textcloserevepsilon) | Closed reversed epsilon = complex-plane criticality | "Closerevepsilon" /riːvɛps/ echoes "complex" |
| $\Phi_\text{EP}$ | $\Phi_\text{revepsilon}$ | `3` (\textrevepsilon) | Reversed epsilon = exceptional point (non-Hermitian) | "Revepsilon" /rɛvɛps/ begins with /ɛp/ = "EP" |
| $\Phi_\text{sup}$ | $\Phi_\text{upstep}$ | `Ţ` (\textupstep) | Upward step = supercritical, crossing threshold | "Upstep" /ʌp/ = "sup" without /s/; up = above |

### H — Chirality
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $H_0$ | $H_\text{closeomega}$ | `Ñ` (\textcloseomega) | Closed omega = zero memory, closed temporal loop | "Closeomega" /kloʊz/ evokes zero as closed circle |
| $H_1$ | $H_\text{toneletterstem}$ | `£` (\texttoneletterstem) | Tone stem = one mark, one memory step | "Tone" /toʊn/ contains echo of "one" |
| $H_2$ | $H_\text{turntwo}$ | `A` (\textturntwo) | Turned 2 = two-step Markov memory depth | "Turntwo" /tuː/ = the sound of "two" |
| $H_\infty$ | $H_\text{invscripta}$ | `!` (\textinvscripta) | Inverted script a = unbounded infinite memory | "Inv" /ɪn/ = /ɪn/ of "inf"(inite) |

### S — Stoichiometry
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $1{:}1$ | $S_\text{doublebaresh}$ | `S` (\textdoublebaresh) | Double-bar esh = one-to-one paired strokes | "Doublebaresh" /dʌb/ evokes the paired 1:1 match |
| $n{:}n$ | $S_\text{ctn}$ | `ő` (\textctn) | C-t-n ligature = many identical (n:n) | "Ctn" /n/ = the repeated N of "n:n" |
| $n{:}m$ | $S_\text{ltailm}$ | `M` (\textltailm) | L-tail-M = heterogeneous distinct types (m ≠ n) | "Ltailm" /lteɪlm/ echoes the mixed "n:m" |

### Ω — Topological Invariant
| Original | New | Symbol | Nature | Sound |
|---|---|---|---|---|
| $\Omega_0$ | $\Omega_\text{closeepsilon}$ | `Å` (\textcloseepsilon) | Closed epsilon = trivial, no topological invariant | "Closeepsilon" /kləʊz/ closes = zero |
| $\Omega_{\mathbb{Z}_2}$ | $\Omega_\text{crtwo}$ | `2` (\textcrtwo) | Curly 2 = Z₂ binary parity protection | "Crtwo" /tuː/ = "two" of Z₂; curly = twisted |
| $\Omega_\mathbb{Z}$ | $\Omega_\text{dzlig}$ | `z` (\textdzlig) | DZ ligature = integer Z winding number | "Dzlig" ends with /z/ = /zɛd/ of "Z"; ligature = winding |
| $\Omega_\text{NA}$ | $\Omega_\text{turna}$ | `5` (\textturna) | Turned 'a' = non-Abelian braiding twists | "Turna" /eɪ/ = /eɪ/ of "NA" (en-ay); twist = braid |

---

## Verification

- **49 total assignments** — one per primitive-subtype pair across all 12 primitives
- **49 unique display characters** — no collisions across the entire set
- Each symbol was verified present in `psymbols.txt` (Tables 15, 17, 19, 21, 22)
- Sound match criteria: initial phoneme match, homophony, or phonetic containment
- Nature match criteria: visual typography, semantic association, or alphabetic lineage (as for beta/beth, gamma/gimel)