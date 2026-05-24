#!/usr/bin/env python3
"""
ASSIGN NEW PHONETIC SYMBOLS TO IMSCRIBING GRAMMAR PRIMITIVES

Task: replace existing subscripts (e.g., D_omega, T_commatailz) with new 
phonetic symbols from psymbols.txt, such that the subscript reflects 
BOTH the nature of the primitive subtype AND the sound of its name.

Approach: For each primitive subtype, I select a phonetic symbol whose
LATEX NAME phonetically resembles the subtype name, AND whose visual 
appearance or typographic shape evokes the nature of that primitive.

Strategy by category:

1. DIRECT PHONETIC MATCHES: Where the symbol name clearly sounds like 
   the subtype name.
   - beth → \textbeta (β) — "beta" sounds nearly identical to "beth"
   - wedge → \textwynn (ß) — wynn = old English w, wedge starts with W
   - seq → \textsecstress (­) — "sec" sounds like "seq"
   - sub → \textsubrightarrow (¯) — starts with "sub"
   - EP → \textepsilon (ε) — "epsilon" starts with "ep"
   - psi → \textpsi... no \textpsi in list. But \textphi (φ) or \textupsilon (υ)

2. PHONETIC INITIAL SOUND: Subtype name starts with same sound as symbol name.
   - infty → \textinvscripta (!) — "inv" sounds like "in" from "infty"
   - in → \textinvscripta (!) — "in"
   - network → \textnrleg (6) — starts with "n"
   - super → \textsubrightarrow (¯) — "sup" and "sub" share initial
   - cat → \textctz (ý) — "ct" (c+t ligature) starts with /k/
   - fast → \textfrtailgamma (-) — starts with "f"
   - slow → \text... hmm, none start with "slo". Let's try \textschwa (@)?
   - mod → ??? No direct match
   - S_doublebaresh → \textopeno? No. Let's think differently.

3. VISUAL/SEMANTIC CONNECTION: Symbol shape evokes the nature.
   - triangle → \textturnthree (C) — three turns = three sides!
   - bowtie → \textbullseye (ò) — target shape, crossing point
   - odot → \textopeno (O) — open O like a dot/point
   - dot/odot → \textomega (ω) — omega is like a circle
   - lr (left-right) → \textlyoghlig (Ð) — ligature joining two shapes
   - dagger → \textdzlig (z) — d-z ligature suggests dagger shape? 
     Or \textdownstep (Ť) — downward stroke

4. SOUNDS OF LETTERS (for number/letter codes)
   - For H_0: zero → \textopeno (O) — zero = circle
   - For H_1: one → \textwynn (ß) — wynn sounds like "one"? No.
   - For H_2: two → \textcrtwo (2) or \textturntwo (A) — literally "two"
   - For H_invscripta: infty → \textinvscripta (!) — "in" sound
   - For Omega_closeepsilon: zero → \textopeno (O)
   - For Omega_crtwo: Z2 → \textctz (ý) for Z sound, or \textcrtwo (2) for 2
   - For Omega_dzlig: Z → \textctz (ý) — "ctz" has Z sound at end
   - For Omega_turna: NA → \textnrleg (6) — "nr" starts with N sound

5. COMPLEX COMPOSITES
   - c_complex: complex → \text... "com" → \textcommatailz (Þ)?
     Or just \textctz (ý) for the c sound + some modifier
   - pm: plus-minus → \textpm doesn't exist. \textprimstress (")? No.
     \textpipevar (F)? No. Maybe \textturna (5)? No.
   - pm_sym: Frobenius-special needs a special symbol. 
     \textdoublebarpipe (})? \textdoublepipe ({)?
   - asym: asymmetric → \textaolig (")? 
   - sym: symmetric → \text... \textsubrightarrow (¯)?
   
6. HEBREW LETTERS
   - aleph → The phonetic symbol for /ʔ/ or /a/... 
     \textaolig (") has "a" sound. Or \textrevapostrophe (\)?
     Actually \textschwa (@) — schwa is the closest to the Hebrew aleph sound

7. ELL / ETH / HBAR
   - ell → \textbeltl (ì) — beltl ends with "l" and has "l" in name
     Or \textltailm (M)? No. \texttoneletterstem (£)? No.
     \textesh (S) — "esh" ends with "sh" not "ell"
   - eth → \texttheta (θ) — theta ends with "ta" but starts with "th" like eth
     \texteth doesn't exist but \texttheta has the th sound!
   - hbar → \texthvlig (ß) — hv ligature, hbar = h + bar

8. MBL (Many-Body Localization)
   - MBL → \textlambda (λ) — lambda has the L sound
     Or \textltailm (M) for M, \textbullseye (ò) for B?

9. TRAP (frozen ordered)
   - trap → \textretractingvar (˚) — retract suggests being stuck

10. GIMEL
    - gimel → \textgrgamma (,) — "gr" starts like "gi" (g sound)
      Or \textgamma (γ) — gamma has the hard G sound like gimel

11. ALEPH
    - aleph → \textaolig (") — "ao" starts with A sound
      Or \textinvscripta (!) — no
      Or \textopeno (O) — no

12. AND / OR / BROAD
    - and → \textaolig (") — "a" sound
    - or → \textopeno (O) — "o" sound  
    - broad → \textbullseye (ò) — "b" sound, also round like broadcast

13. ELL → \textbeltl (ì) — "beltl" has the L sound and belt suggests binding
    Actually \textellg... doesn't exist. But \textbeltl has "l" ending.
    Or \textscj (ĺ)? No. \textschwa (@)? No.
    \textepsilon (ε)? No.
    
14. ETH → \texttheta (θ) — th sound, eth is the voiced th
    Actually \textdh (ð) exists! From the wasysym table:
    ð \dh — thorn-like with stroke, used for eth sound in IPA!
    But wait, the symbol is \dh not \textdh. Let me check...
    
    From the wasysym table: ð \dh — this IS the IPA symbol for the voiced 
    dental fricative (eth sound)! But it uses \dh not \text... prefix.

    Similarly, þ \thorn — this IS the thorn character.

    Also, from wasysym: Ð \DH and Þ \Thorn

    But these use \dh and \thorn without the \text prefix, so they might
    not be in my parser. Let me check.

Actually, looking more carefully at the tables, the symbols are organized by
package. Let me look at the non-\text entries too.

OK, I think I've gathered enough information. Let me now make the assignments.
"""
print("Analysis complete. Switching to assignment phase.")
