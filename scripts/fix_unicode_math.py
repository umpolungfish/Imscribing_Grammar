#!/usr/bin/env python3
"""
fix_unicode_math.py
Scans a .tex file and replaces Unicode mathematical italic/bold characters
and bare Greek letters that appear OUTSIDE LaTeX math mode with proper
$...$ LaTeX equivalents.

Handles:
  - Math italic capitals U+1D434-U+1D44D  (𝐴-𝑍) → $A$-$Z$
  - Math italic smalls   U+1D44E-U+1D467  (𝑎-𝑧) → $a$-$z$
  - Math bold capitals   U+1D400-U+1D419  (𝐀-𝐙) → $\mathbf{A}$-...
  - Math bold smalls     U+1D41A-U+1D433  (𝐚-𝐳) → $\mathbf{a}$-...
  - Bare Greek uppercase in text → $\Name$
  - Unicode operators (×⊗⊕→⊆∈…) in text → $\cmd$
  - Digit(s) immediately following a converted char become a subscript
"""

import re, sys, unicodedata
from pathlib import Path

# ── character maps ────────────────────────────────────────────────────────────

MATH_ITALIC_UPPER = {chr(0x1D434 + i): chr(ord('A') + i) for i in range(26)}
MATH_ITALIC_LOWER = {chr(0x1D44E + i): chr(ord('a') + i) for i in range(25)}  # h gap
MATH_ITALIC_LOWER['ℎ'] = 'h'  # Planck h

MATH_BOLD_UPPER = {chr(0x1D400 + i): ('\\mathbf{' + chr(ord('A') + i) + '}') for i in range(26)}
MATH_BOLD_LOWER = {chr(0x1D41A + i): ('\\mathbf{' + chr(ord('a') + i) + '}') for i in range(26)}

# Math bold italic
MATH_BOLD_ITALIC_UPPER = {chr(0x1D468 + i): ('\\boldsymbol{' + chr(ord('A') + i) + '}') for i in range(26)}
MATH_BOLD_ITALIC_LOWER = {chr(0x1D482 + i): ('\\boldsymbol{' + chr(ord('a') + i) + '}') for i in range(26)}

MATH_CHAR_MAP = {
    **MATH_ITALIC_UPPER, **MATH_ITALIC_LOWER,
    **MATH_BOLD_UPPER,   **MATH_BOLD_LOWER,
    **MATH_BOLD_ITALIC_UPPER, **MATH_BOLD_ITALIC_LOWER,
}

# Greek uppercase that appear as IG primitives in text mode
GREEK_MAP = {
    'Γ': r'\Gamma',  'Δ': r'\Delta',  'Θ': r'\Theta',  'Λ': r'\Lambda',
    'Ξ': r'\Xi',     'Π': r'\Pi',     'Σ': r'\Sigma',  'Υ': r'\Upsilon',
    'Φ': r'\Phi',    'Χ': r'\Chi',    'Ψ': r'\Psi',    'Ω': r'\Omega',
}

# Unicode operators to LaTeX
OP_MAP = {
    '×': r'\times',  '⊗': r'\otimes', '⊕': r'\oplus',  '⊙': r'\odot',
    '→': r'\to',     '←': r'\leftarrow', '↔': r'\leftrightarrow',
    '⇒': r'\Rightarrow', '⇔': r'\Leftrightarrow',
    '≤': r'\leq',    '≥': r'\geq',    '≠': r'\neq',    '≡': r'\equiv',
    '≈': r'\approx', '∝': r'\propto', '∼': r'\sim',
    '∈': r'\in',     '∉': r'\notin',  '⊆': r'\subseteq', '⊂': r'\subset',
    '⊇': r'\supseteq', '⊃': r'\supset',
    '∪': r'\cup',    '∩': r'\cap',    '∅': r'\emptyset',
    '∀': r'\forall', '∃': r'\exists', '¬': r'\neg',
    '∧': r'\wedge',  '∨': r'\vee',
    '⌊': r'\lfloor', '⌋': r'\rfloor', '⌈': r'\lceil', '⌉': r'\rceil',
    '∞': r'\infty',  '∂': r'\partial', '∇': r'\nabla',
    '√': r'\sqrt{}', '∫': r'\int',    '∑': r'\sum',    '∏': r'\prod',
    '⟨': r'\langle', '⟩': r'\rangle',
}

ALL_TRIGGER = set(MATH_CHAR_MAP) | set(GREEK_MAP) | set(OP_MAP)

# ── math-mode tracker ─────────────────────────────────────────────────────────

MATH_ENVS = {'equation', 'equation*', 'align', 'align*', 'gather', 'gather*',
             'multline', 'multline*', 'flalign', 'flalign*', 'eqnarray',
             'eqnarray*', 'math', 'displaymath'}

def process(text: str) -> str:
    out = []
    i = 0
    n = len(text)
    math_depth = 0   # >0 means we're inside math

    while i < n:
        c = text[i]

        # ── skip comments ────────────────────────────────────────────────────
        if c == '%':
            end = text.find('\n', i)
            if end == -1: end = n
            out.append(text[i:end])
            i = end
            continue

        # ── \begin{env} / \end{env} ──────────────────────────────────────────
        if text[i:i+7] == r'\begin{':
            j = text.find('}', i+7)
            if j != -1:
                env = text[i+7:j]
                if env in MATH_ENVS:
                    math_depth += 1
                out.append(text[i:j+1])
                i = j + 1
                continue
        if text[i:i+5] == r'\end{':
            j = text.find('}', i+5)
            if j != -1:
                env = text[i+5:j]
                if env in MATH_ENVS and math_depth > 0:
                    math_depth -= 1
                out.append(text[i:j+1])
                i = j + 1
                continue

        # ── \( \) \[ \] ──────────────────────────────────────────────────────
        if text[i:i+2] == r'\(':
            math_depth += 1; out.append(r'\('); i += 2; continue
        if text[i:i+2] == r'\)':
            if math_depth > 0: math_depth -= 1
            out.append(r'\)'); i += 2; continue
        if text[i:i+2] == r'\[':
            math_depth += 1; out.append(r'\['); i += 2; continue
        if text[i:i+2] == r'\]':
            if math_depth > 0: math_depth -= 1
            out.append(r'\]'); i += 2; continue

        # ── $ and $$ ─────────────────────────────────────────────────────────
        if c == '$':
            if text[i:i+2] == '$$':
                if math_depth == 0:
                    math_depth += 1
                    out.append('$$'); i += 2; continue
                else:
                    math_depth -= 1
                    out.append('$$'); i += 2; continue
            else:
                math_depth = 0 if math_depth > 0 else 1
                out.append('$'); i += 1; continue

        # ── inside math: pass through unchanged ──────────────────────────────
        if math_depth > 0:
            out.append(c); i += 1; continue

        # ── outside math: convert trigger chars ──────────────────────────────
        if c in ALL_TRIGGER:
            if c in OP_MAP:
                # standalone operator → $\cmd$
                out.append('$' + OP_MAP[c] + '$')
                i += 1
                continue

            # math italic / bold / Greek char — may have trailing digit subscript
            if c in MATH_CHAR_MAP:
                latex_char = MATH_CHAR_MAP[c]
            else:
                latex_char = GREEK_MAP[c]

            # consume digits immediately following as subscript
            j = i + 1
            while j < n and text[j].isdigit():
                j += 1
            digits = text[i+1:j]

            if digits:
                if len(digits) == 1:
                    out.append(f'${latex_char}_{digits}$')
                else:
                    out.append(f'${latex_char}_{{{digits}}}$')
            else:
                out.append(f'${latex_char}$')
            i = j
            continue

        out.append(c)
        i += 1

    return ''.join(out)


# ── post-pass: merge adjacent $...$ separated only by whitespace/punctuation ──

def merge_adjacent_math(text: str) -> str:
    """
    Merge $A$, $B$ → $A, B$ only when separated by ', ' or ' ' and
    both sides are simple math tokens (no nested braces beyond one level).
    Conservative: only merge when separator is ', ' or ' \times ' etc.
    """
    # Merge $X$ \times $Y$ → $X \times Y$ (operator already converted)
    # Actually operators were wrapped individually: $\times$ — unwrap when between math
    text = re.sub(
        r'\$([^$]+)\$ *\$\\(times|otimes|oplus|to|cdot|cup|cap)\$ *\$([^$]+)\$',
        lambda m: f'${m.group(1)} \\{m.group(2)} {m.group(3)}$',
        text
    )
    return text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fix_unicode_math.py FILE.tex [FILE2.tex ...]")
        sys.exit(1)

    for path in sys.argv[1:]:
        p = Path(path)
        original = p.read_text(encoding='utf-8')
        fixed = process(original)
        fixed = merge_adjacent_math(fixed)
        if fixed != original:
            p.write_text(fixed, encoding='utf-8')
            changed = sum(1 for a, b in zip(original, fixed) if a != b)
            print(f'Fixed: {path}  (~{changed} chars changed)')
        else:
            print(f'Clean: {path}')
