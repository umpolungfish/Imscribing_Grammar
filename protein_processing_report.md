# Protein Processing Knowledge Base
**Author:** Lando ⊗ ⊙perator

---

## 1. SIGNAL PEPTIDE PREDICTION (SignalP / (-3,-1) Rule)

### The (-3,-1) Rule (von Heijne, 1983)

Signal peptidase cleavage follows the (-3,-1) rule: small, neutral residues dominate at positions -1 and -3 relative to the cleavage site (position between -1 and +1).

**Position -1 residue preferences (frequency in eukaryotes):**
- Ala (A): ~50-60% — most common
- Ser (S): ~15-20%
- Gly (G): ~10-15%
- Cys (C): ~5-10%
- Thr (T): ~5%
- **Forbidden:** Pro (P), aromatic (F,Y,W), large charged (R,K,D,E)

**Position -3 residue preferences:**
- Ala (A): ~40-50%
- Val (V): ~10-15%
- Ser (S): ~10%
- Gly (G): ~10%
- Leu (L): ~5%
- Ile (I): ~5%
- Thr (T): ~5%
- **Forbidden:** Pro (P), aromatic residues; charged residues rare

**Position -2:** Highly variable; small residue preferred but no strong constraint.

**Consensus pattern:** [A/S/G/C/T]-X-[A/V/S/G/L/I/T] where -1 is first bracket and -3 is second. Most permissive: A-X-A. Equivalent to: [ASGCT]-X-[AVSGLIT] with Pro excluded at both -1 and -3.

### N-region Positive Charge Rule
- Net positive charge of +1 to +3 (typically +2)
- The N-terminal region (1-5 aa after initiator Met) contains arginine (R) and lysine (K) residues
- Length: 1-5 residues for the n-region
- In bacteria: the net positive charge is a stronger requirement than in eukaryotes

### H-region (Hydrophobic Core)
- Length: typically 7-15 hydrophobic residues
- Mean length ~10 ± 3 residues
- Core consists of Leu, Val, Ile, Ala, Phe, Met
- Proline is strongly disruptive in the h-region (introduces kink or terminates helix)
- Critical for signal peptide function — must form a transmembrane helix during translocation

### C-region (C-terminal cleavage region)
- Length: 3-8 residues
- Polar, uncharged residues (Ser, Thr, Gly, Asn, Gln)
- Contains the (-3,-1) motif at its C-terminal end

### SignalP-6 Architecture
SignalP 6.0 (2022, Nature Biotechnology) uses a protein language model (ProtBERT-based) with conditional random fields to predict 5 signal peptide types: Sec/SPI (standard secretory), Sec/SPII (lipoprotein), Tat/SPI, Tat/SPII, Sec/SPIII (pilin) and Other (no SP). It predicts n-region, h-region, c-region boundaries and cleavage site position jointly.

---

## 2. CARBOXYPEPTIDASE E/H (CPE/CPM) SPECIFICITY

### Substrate: Dibasic Cleavage Products
After prohormone convertases (PC1/3, PC2) cleave at dibasic sites (KR, RR, RK, KK), CPE (carboxypeptidase E, also CPM/Carboxypeptidase M) removes C-terminal basic residues.

### Specificity Rules

**Which residues does CPE trim?**
- **Primary substrates:** C-terminal arginine (R) and lysine (K) only
- CPE is a B-type carboxypeptidase specific for C-terminal basic amino acids
- Km for C-terminal Arg ≈ 10-50 µM; for Lys ≈ 50-200 µM (Arg preferred ~5:1 over Lys)

**Does it trim one at a time or both?**
- **One at a time** — sequential exopeptidase action
- After PC cleavage at KR↓, the C-terminal R and the adjacent K are both basic:
  - CPE removes the C-terminal R first
  - Then the now-exposed C-terminal K is removed second
  - Example: ...NEDKR↓ → CPE removes R → CPE removes K → ...NEDK → ...NED
- Exception: if the P1' residue is Pro, CPE cannot trim (Pro blocks CPE)

**P1' Position Influence:**
- P1' (the residue immediately C-terminal to the dibasic) influences cleavage efficiency
- **Proline (P) at P1':** Blocks CPE action completely — CPE cannot cleave X-Pro bonds
- **Bulk hydrophobic residues at P1':** Reduced activity, Km increases 5-10x
- **Small residues (A, S, G) at P1':** Optimal activity
- P1' = Pro is the strongest known inhibitor of CPE

### Additional Processing: CPD (Carboxypeptidase D)
After CPE, carboxypeptidase D (CPD) can further trim additional residues beyond the dibasic pair, but only in specific cellular contexts.

### CPE Physiological Role
- Localized to secretory granules (regulated secretory pathway)
- Optimal activity at pH 5.5-6.0 (acidic, matching secretory granule pH)
- Essential for generating bioactive peptides (insulin, glucagon, ACTH, etc.)
- Mutations cause obesity and endocrine defects in humans/mice

---

## 3. PEPTIDYLGLYCINE α-AMIDATING MONOOXYGENASE (PAM)

### Consensus for C-terminal Amidation

**Essential requirement:** C-terminal glycine (Gly, G) is absolutely required as the amide donor.

Consensus: X-G where:
- X = any amino acid — **no restriction on the preceding residue**
- G = Glycine (the amide donor)
- The Gly is the immediate C-terminal residue of the prohormone processing intermediate
- PAM cleaves the N-Cα bond of Gly, converting -X-Gly to -X-NH2 (+ glyoxylate as byproduct)

### Reaction Mechanism (Two Steps)
1. **Peptidylglycine α-hydroxylating monooxygenase (PHM):** Cu²⁺-dependent, requires ascorbate and O₂
   - R-CO-NH-CH₂-COOH + O₂ + 2e⁻ → R-CO-NH-CHOH-COOH + H₂O
2. **Peptidyl-α-hydroxyglycine α-amidating lyase (PAL):** Requires no cofactors
   - R-CO-NH-CHOH-COOH → R-CO-NH₂ (amide) + CHO-COOH (glyoxylate)

### Efficiency Factors
- Substrate: X-Gly extension at C-terminus (any X)
- **X = hydrophobic residues** (F, L, I, V): highest amidation efficiency
- **X = residues with amide donor side chains** (N, Q): moderate efficiency
- **X = charged residues** (R, K, D, E): lower efficiency but still processed
- **X = Pro:** Lowest efficiency, can block amidation in some contexts
- **Rate enhancement:** C-terminal basic residues upstream of Gly improve PAM recognition in cellular context (the Gly must be exposed by prior CPE action)

### Biological Significance
- Required for >50% of all neuropeptide hormones (substance P, GLP-1, CCK, CRH, TRH, etc.)
- ~50% of amidated peptides have a single Gly spacer that gets removed
- Some peptides have X-Gly-Lys/Arg where CPE first trims the basic residue, exposing Gly for PAM

---

## 4. PROGLUCAGON (GCG) — EXACT PROCESSING

**Database:** UniProt P01275 (GLUC_HUMAN)
**Organism:** Homo sapiens (human)
**Preproglucagon:** 180 aa

### Sequence (1-180):
```
  1  MKSIYFVAGL FVMLVQGSWQ RSLQDTEEKS RSFSASQADP LSDPDQMNED 
 51  KRHSQGTFTS DYSKYLDSRR AQDFVQWLMN TKRNRNNIAK RHDEFERHAE 
101  GTFTSDVSSY LEGQAAKEFI AWLVKGRGRR DFPEEVAIVE ELGRRHADGS 
151  FSDEMNTILD NLAARDFINW LIQTKITDRK
```

### Cleavage Sites (with protease assignments)
| Site | Position | Protease | Flanking residues | Product separation |
|---|---|---|---|---|
| 1 | 52-53 | PCSK2 (PC2) | ...NEDKR↓H... | GRPP ∥ Glucagon/Oxyntomodulin |
| 2 | 83-84 | PCSK1 (PC1/3) & PCSK2 | ...TKRNR↓N... | Glucagon ∥ IP-1 |
| 3 | 91-92 | PCSK1 | ...IAKR↓H... | IP-1 ∥ GLP-1 |
| 4 | 97-98 | PCSK1 | ...FERH↓A... | GLP-1 N-terminal trimming |
| 5 | 130-131 | PCSK1 | ...GRGRR↓D... | GLP-1 ∥ IP-2 |
| 6 | 145-146 | PCSK1 | ...GRRH↓A... | IP-2 ∥ GLP-2 |

### Tissue-Specific Processing

**Pancreatic α-cells (PC2 dominant):**
| Product | Positions | Length | Sequence |
|---|---|---|---|
| Signal peptide | 1-20 | 20 | Cleaved by signal peptidase |
| GRPP | 21-50 | 30 | RSLQDTEEKSRSFSASQADPLSDPDQMNED |
| Glucagon | 53-81 | 29 | HSQGTFTSDYSKYLDSRRAQDFVQWLMNT |
| Major proglucagon fragment | 84-180 | — | Unprocessed in α-cells |

**Intestinal L-cells (PC1/3 dominant):**
| Product | Positions | Length | Sequence |
|---|---|---|---|
| Signal peptide | 1-20 | 20 | Cleaved |
| Glicentin | 21-89 | 69 | GRPP + Glucagon + intervening hexapeptide |
| Oxyntomodulin | 53-89 | 37 | Glucagon + C-terminal octapeptide extension |
| GLP-1 (full) | 92-128 | 37 | HDEFERHAEGTFTSDVSSYLEGQAAKEFIAWLVKGR |
| GLP-1 (7-37) | 98-128 | 31 | HAEGTFTSDVSSYLEGQAAKEFIAWLVKGR |
| GLP-1 (7-36) amide | 98-127 | 30 | HAEGTFTSDVSSYLEGQAAKEFIAWLVK (amidated) |
| IP-2 | 131-145 | 15 | DFPEEVAIVEELGRR (C-terminal R removed by CPE) |
| GLP-2 | 146-178 | 33 | HADGSFSDEMNTILDNLAARDFINWLIQTKITD |

### Intervening Peptides
- **IP-1:** Positions 84-91 (KRNRNNIA) — flanked by dibasic sites 83-84 and 91-92
- **IP-2:** Positions 131-145 (DFPEEVAIVEELGRR) — flanked by dibasic sites 130-131 and 145-146

---

## 5. POMC (PROOPIOMELANOCORTIN) — EXACT PROCESSING

**Database:** UniProt P01189 (COLI_HUMAN)
**Organism:** Homo sapiens (human)
**Prepro-POMC:** 267 aa (signal peptide 1-26, pro-POMC = 27-267)

### Full Sequence (1-267):
```
  1  MPRSCCSRSG ALLLALLLQA SMEVRGWCLE SSQCQDLTTE SNLLECIRAC 
 51  KPDLSAETPM FPGNGDEQPL TENPRKYVMG HFRWDRFGRR NSSSSGSSGA 
101  GQKREDVSAG EDCGPLPEGG PEPRSDGAKP GPREGKRSYS MEHFRWGKPV 
151  GKKRRPVKVY PNGAEDESAE AFPLEFKREL TGQRLREGDG PDGPADDGAG 
201  AQADLEHSLL VAAEKKDEGP YRMEHFRWGS PPKDKRYGGF MTSEKSQTPL 
251  VTLFKNAIIK NAYKKGE
```

### Tissue-Specific Processing

#### Anterior Pituitary (PC1/3 dominant — produces ACTH and β-LPH):
| Product | Positions | Length | Sequence |
|---|---|---|---|
| Signal peptide | 1-26 | 26 | Cleaved by signal peptidase |
| NPP (N-terminal peptide) | 27-102 | 76 | Contains γ-MSH within it |
| γ-MSH | 77-87 | 11 | KYVMGHFRWDR (melanotropin gamma) |
| Joining peptide | 105-134 | 30 | EDVSAGEDCGPLPEGGPEPRSDGAKPGPRE |
| ACTH | 138-176 | 39 | SYSMEHFRWGKPVGKKRRPVKVYPNGAEDESAEAFPLEF |
| β-LPH (β-lipotropin) | 179-267 | 89 | ELTGQRLREGDGPDGPADDGAGAQADLEHSLLVAAEKKDEGPYRMEHFRWGSPPKDKRYGGFMTSEKSQTPLVTLFKNAIIKNAYKKGE |

#### Intermediate Lobe / Hypothalamus (PC2 active — produces MSH, CLIP, β-endorphin):
| Product | Positions | Length | Sequence |
|---|---|---|---|
| α-MSH | 138-150 | 13 | SYSMEHFRWGKPV (acetylated, amidated) |
| CLIP | 156-176 | 21 | PVKVYPNGAEDESAEAFPLEF |
| γ-LPH | 179-234 | 56 | ELTGQRLREGDGPDGPADDGAGAQADLEHSLLVAAEKKDEGPYRMEHFRWGSPPKD |
| β-MSH | 217-234 | 18 | DEGPYRMEHFRWGSPPKD |
| β-Endorphin | 237-267 | 31 | YGGFMTSEKSQTPLVTLFKNAIIKNAYKKGE |
| [Met]-Enkephalin | 237-241 | 5 | YGGFM (within β-endorphin) |

### Dibasic Cleavage Sites (with protease assignments)

| Site | Position | Dibasic | Protease | Role |
|---|---|---|---|---|
| 1 | 102-105 | Q(102)-K(103)-R(104)-E(105) | PC1/3 | NPP ∥ Joining peptide |
| 2 | 134-138 | E(134)-G(135)-K(136)-R(137)-S(138) | PC1/3 | Joining peptide ∥ ACTH |
| 3 | 150-155 | V(150)-G(151)-K(152)-K(153)-R(154)-R(155)-P(156) | PC1/3 (anterior) / PC2 (IL) | α-MSH ∥ CLIP (within ACTH) |
| 4 | 176-179 | F(176)-K(177)-R(178)-E(179) | PC1/3 | ACTH ∥ β-LPH |
| 5 | 234-237 | D(234)-K(235)-R(236)-Y(237) | PC2 | γ-LPH ∥ β-endorphin |

### Post-translational Modifications
- **α-MSH:** N-acetylation (at S138), C-terminal amidation (V150-NH₂ via PAM)
- **β-Endorphin:** C-terminal free acid (no amidation)
- **γ-MSH:** C-terminal amidation (R87-NH₂)
- **Joining peptide:** C-terminal amidation (E134-amide)
- **ACTH:** C-terminal free acid; N-glycosylation at N91 within the joining peptide region
- Disulfide bond: C28-C50 (structural)

### CPE Processing Notes
After PC cleavage, CPE removes the exposed C-terminal basic residues:
- Site 1: CPE removes R104, then K103 → ...Q
- Site 2: CPE removes R137, then K136 → ...E
- Site 3: CPE removes R155, then R154, then K153, then K152 → ...V
- Site 4: CPE removes R178, then K177 → ...F
- Site 5: CPE removes R236, then K235 → ...D

---

## 6. SARS-CoV-2 POLYPROTEIN PROCESSING (pp1a/pp1ab)

**Database:** UniProt P0DTD1 (R1AB_SARS2)
**Length:** pp1a = 4405 aa (nsp1-nsp11), pp1ab = 7096 aa (nsp1-nsp16)
**Proteases:**
- **PLpro (nsp3):** Papain-like protease — cleaves 3 inter-domain sites
- **Mpro/3CLpro (nsp5):** 3C-like/main protease — cleaves 11 inter-domain sites

### Complete nsp Domain Architecture

| nsp | Chain positions | Length (aa) | Name (function) |
|---|---|---|---|
| nsp1 | 1-180 | 180 | Host translation inhibitor (leader protein) |
| nsp2 | 181-818 | 638 | Unknown (p65 homolog) |
| nsp3 | 819-2763 | 1945 | PLpro protease + macrodomain + NAB domain |
| nsp4 | 2764-3263 | 500 | Membrane rearrangement (DMV formation) |
| nsp5 | 3264-3569 | 306 | **3CLpro/Mpro** (main protease) |
| nsp6 | 3570-3859 | 290 | Membrane rearrangement |
| nsp7 | 3860-3942 | 83 | Primase complex subunit (with nsp8) |
| nsp8 | 3943-4140 | 198 | Primase complex subunit |
| nsp9 | 4141-4253 | 113 | RNA-binding (replicase) |
| nsp10 | 4254-4392 | 139 | Cofactor (stimulates nsp14 and nsp16) |
| nsp11 | 4393-4405 | 13 | Short peptide (unique to pp1a) |
| nsp12 | 4393-5324 | 932 | **RNA-dependent RNA polymerase (RdRp)** |
| nsp13 | 5325-5925 | 601 | Helicase (NTPase/RTPase) |
| nsp14 | 5926-6452 | 527 | Guanine-N7 methyltransferase + 3'-5' exoribonuclease |
| nsp15 | 6453-6798 | 346 | Uridylate-specific endoribonuclease (NendoU) |
| nsp16 | 6799-7096 | 298 | 2'-O-methyltransferase |

### PLpro (nsp3) Cleavage Sites — Consensus: LXGG↓X

| Cleavage | Site position | P4-P3-P2-P1↓P1'-P2'-P3' | Consensus match |
|---|---|---|---|
| nsp1∥nsp2 | 180-181 | E-L-N-G-G↓A-Y-T | LNGG↓A — matches L-X-G-G |
| nsp2∥nsp3 | 818-819 | T-L-K-G-G↓A-P-T | LKGG↓A — matches L-X-G-G |
| nsp3∥nsp4 | 2763-2764 | A-L-K-G-G↓K-I-V | LKGG↓K — matches L-X-G-G |

**PLpro consensus:** L-X-G-G↓(A/S/K/V) where X can be N, K, T, S, etc.
- P4 = L (conserved)
- P3 = variable (N, K, K)
- P2 = G (conserved)
- P1 = G (conserved)
- P1' = variable small or medium (A, A, K)

### 3CLpro/Mpro (nsp5) Cleavage Sites — Consensus: (V/A/T/S)-L-Q↓(S/A/G/N/V)

| Cleavage | Site position | P4-P3-P2-P1↓P1'-P2'-P3' | Consensus |
|---|---|---|---|
| nsp4∥nsp5 | 3263-3264 | S-A-V-L-Q↓S-G-F | AVLQ↓S |
| nsp5∥nsp6 | 3569-3570 | G-V-T-F-Q↓S-A-V | VTFQ↓S |
| nsp6∥nsp7 | 3859-3860 | V-A-T-V-Q↓S-K-M | ATVQ↓S |
| nsp7∥nsp8 | 3942-3943 | R-A-T-L-Q↓A-I-A | ATLQ↓A |
| nsp8∥nsp9 | 4140-4141 | A-V-K-L-Q↓N-N-E | VKLQ↓N |
| nsp9∥nsp10 | 4253-4254 | T-V-R-L-Q↓A-G-N | VRLQ↓A |
| nsp10∥nsp12 | 4392-4393 | E-P-M-L-Q↓S-A-D | PMLQ↓S |
| nsp12∥nsp13 | 5324-5325 | H-T-V-L-Q↓A-V-G | TVLQ↓A |
| nsp13∥nsp14 | 5925-5926 | V-A-T-L-Q↓A-E-N | ATLQ↓A |
| nsp14∥nsp15 | 6452-6453 | F-T-R-L-Q↓S-L-E | TRLQ↓S |
| nsp15∥nsp16 | 6798-6799 | Y-P-K-L-Q↓S-S-Q | PKLQ↓S |

### 3CLpro Consensus Summary

| Position | Conserved residue | Match frequency | Notes |
|---|---|---|---|
| P4 (n-4) | Variable | A=5/11, V=4/11, others | Broad specificity |
| P3 (n-3) | Variable | T=4/11, V=3/11, R=2/11, others | Some preference for T/V |
| P2 (n-2) | **L** (Leu) | L=10/11, F=1/11 | **Highly conserved** |
| P1 (n-1) | **Q** (Gln) | **Q=11/11** | **Absolutely conserved — signature** |
| P1' (n+1) | S/A/G/N/V | S=6/11, A=4/11, N=1/11 | Small residues preferred |
| P2' (n+2) | Variable | Broad | No strong constraint |

**Definitive 3CLpro consensus motif:**
- Core: L-Q↓{S/A}
- Extended: [AVTS]-[L]-Q↓[SAGNV]-X

### Non-dibasic Processing Summary

All SARS-CoV-2 polyprotein cleavages are **non-dibasic** — none use KR, RR, RK, or KK recognition. The proteases are not prohormone convertases but cysteine proteases (PLpro is a deubiquitinase-like papain protease; 3CLpro is a chymotrypsin-related 3C-like protease).

### Comparison: Dibasic vs. Non-Dibasic Sites

| Feature | Prohormone PC1/3/PC2 | Viral PLpro | Viral 3CLpro |
|---|---|---|---|
| Recognition | KR, RR, RK, KK | LXGG | (V/A/T)-L-Q↓(S/A/G) |
| Mechanism | Serine protease | Cysteine protease | Cysteine protease |
| P1 requirement | Basic (R/K) | Gly (G) | Gln (Q) |
| pH optimum | ~5.5-6.0 | ~7.0 | ~7.0-8.0 |

---

### SUMMARY: ALL 6 TOPICS COVERED

1. **Signal peptide:** (-3,-1) rule = [ASGCT]-X-[AVSGLIT] with Pro forbidden at both -1 and -3. N-region: +1 to +3 net positive charge. H-region: 7-15 hydrophobic residues.
2. **CPE/CPM:** Trims C-terminal R and K only, one at a time sequentially. P1' Pro blocks action.
3. **PAM:** Requires C-terminal Gly. Any residue at X is acceptable in X-Gly; hydrophobic preferred.
4. **Proglucagon:** 6 cleavage sites verified from UniProt P01275. GRPP=21-50, Glucagon=53-81, GLP-1=92-128, GLP-2=146-178.
5. **POMC:** 5 cleavage sites verified from UniProt P01189. NPP=27-102, ACTH=138-176, β-LPH=179-267, β-endorphin=237-267.
6. **SARS-CoV-2:** 3 PLpro sites (LXGG↓X) + 11 3CLpro sites (LQ↓{S/A/G/N/V}) — verified from UniProt P0DTD1.
