#!/usr/bin/env python3
"""
fix_ig_glyphs.py
Replace wrong primitive letter representations in .tex files with the
standardized IG primitive glyphs, rendered through \igprimfont (FreeSerif).

Subscript text names → correct glyph:
  Ð  wynn turnthree invomega omega
  Þ  nrleg invscr bullseye commatailz openo
  Ř  subrightarrow ctz downstep lyoghlig
  Φ  aolig upsilon pipevar subdoublearrow doublebarpipe
  ƒ  beltl dh eth hardsign
  Ç  frtailgamma turnm schwa teshlig lambda
  Γ  beta gamma revapostrophe
  ɢ  corner spleftarrow secstress doublevertline
  ⊙  softsign ctyogh closerevepsilon revepsilon upstep
  Ħ  closeomega toneletterstem turntwo invscripta
  Σ  doublebaresh ctn ltailm
  Ω  closeepsilon crtwo dzlig turna
"""

import re
import sys
from pathlib import Path

SUB_TO_GLYPH = {
    'wynn': 'Ð', 'turnthree': 'Ð', 'invomega': 'Ð', 'omega': 'Ð',
    'nrleg': 'Þ', 'invscr': 'Þ', 'bullseye': 'Þ', 'commatailz': 'Þ', 'openo': 'Þ',
    'subrightarrow': 'Ř', 'ctz': 'Ř', 'downstep': 'Ř', 'lyoghlig': 'Ř',
    'aolig': 'Φ', 'upsilon': 'Φ', 'pipevar': 'Φ', 'subdoublearrow': 'Φ', 'doublebarpipe': 'Φ',
    'beltl': 'ƒ', 'dh': 'ƒ', 'eth': 'ƒ', 'hardsign': 'ƒ',
    'frtailgamma': 'Ç', 'turnm': 'Ç', 'schwa': 'Ç', 'teshlig': 'Ç', 'lambda': 'Ç',
    'beta': 'Γ', 'gamma': 'Γ', 'revapostrophe': 'Γ',
    'corner': 'ɢ', 'spleftarrow': 'ɢ', 'secstress': 'ɢ', 'doublevertline': 'ɢ', 'seq': 'ɢ',
    'softsign': '⊙', 'ctyogh': '⊙', 'closerevepsilon': '⊙', 'revepsilon': '⊙', 'upstep': '⊙',
    'closeomega': 'Ħ', 'toneletterstem': 'Ħ', 'turntwo': 'Ħ', 'invscripta': 'Ħ',
    'doublebaresh': 'Σ', 'ctn': 'Σ', 'ltailm': 'Σ',
    'closeepsilon': 'Ω', 'crtwo': 'Ω', 'dzlig': 'Ω', 'turna': 'Ω',
}

def ig(glyph, sub=''):
    if sub:
        return f'\\text{{{{\\igprimfont {glyph}}}}}{sub}'
    return f'\\text{{{{\\igprimfont {glyph}}}}}'


def process(text):
    # ── 1. Subscript _{\text{NAME}} form ──────────────────────────────────────
    # Matches: LETTER_{\text{NAME}} or \COMMAND_{\text{NAME}}
    # The capturing group is the letter/command before the underscore.
    def sub_text_repl(m):
        name = m.group('name')
        if name not in SUB_TO_GLYPH:
            return m.group(0)
        glyph = SUB_TO_GLYPH[name]
        return ig(glyph, '_{{\\text{{{}}}}}'.format(name))

    # With braces: X_{\text{name}}
    text = re.sub(
        r'(?<![\\a-zA-Z])(?:D|T|R|P|F|K|G|H|S|\\Gamma|\\Phi|\\Omega)'
        r'_\{\\text\{(?P<name>[a-z]+)\}\}',
        sub_text_repl, text
    )

    # Without braces: X_\text{name}  (rare variant)
    text = re.sub(
        r'(?<![\\a-zA-Z])(?:D|T|R|P|F|K|G|H|S|\\Gamma|\\Phi|\\Omega)'
        r'_\\text\{(?P<name>[a-z]+)\}',
        sub_text_repl, text
    )

    # ── 2. H_N digit subscripts (temporal depth values H0..H9) ───────────────
    # Only bare H not preceded by a letter/backslash (avoids Hom, H_{..}, etc.)
    text = re.sub(
        r'(?<![\\a-zA-Z])H_([0-9])(?![a-zA-Z])',
        lambda m: ig('Ħ', f'_{m.group(1)}'),
        text
    )

    # ── 3. H_\infty ───────────────────────────────────────────────────────────
    _hinfty = ig('Ħ', '_\\infty')
    text = re.sub(
        r'(?<![\\a-zA-Z])H_\\infty(?![a-zA-Z])',
        lambda m: _hinfty,
        text
    )

    # ── 3b. Math-subscript variants (\Phi_\uparrow, \Phi_\times, \Gamma_{\to}) ─
    MATH_SUB = [
        (r'\\Phi_\\uparrow',           ig('⊙', '_\\uparrow')),
        (r'\\Phi_\\times',             ig('⊙', '_\\times')),
        (r'\\Phi_\\varnothing',        ig('⊙', '_\\varnothing')),
        (r'\\Phi_\\downarrow',         ig('⊙', '_\\downarrow')),
        (r'\\Gamma_\{\\to\}',          ig('ɢ', '_{\\to}')),
        (r'\\Gamma_\{\\gg\}',          ig('ɢ', '_{\\gg}')),
        (r'\\Gamma_\{\\rightarrow\}',  ig('ɢ', '_{\\rightarrow}')),
        (r'\\Omega_\\varnothing',      ig('Ω', '_\\varnothing')),
    ]
    for pat, repl in MATH_SUB:
        _repl = repl
        text = re.sub(r'(?<![\\a-zA-Z])' + pat, lambda m, r=_repl: r, text)

    # ── 3c. X_\text{name} without outer braces (e.g. F_\text{eth}) ───────────
    text = re.sub(
        r'(?<![\\a-zA-Z])(?:D|T|R|P|F|K|G|H|S|\\Gamma|\\Phi|\\Omega)'
        r'_\\text\{(?P<name>[a-z]+)\}',
        sub_text_repl, text
    )

    # ── 4. Standalone \Phi in math (without subscript) — always ⊙ in this doc ─
    _phi_repl = ig('⊙')
    text = re.sub(
        r'(?<![\\a-zA-Z])\\Phi(?![a-zA-Z_{])',
        lambda m: _phi_repl,
        text
    )

    # ── 5. Standalone \Gamma in math (without subscript) — always ɢ here ──────
    _gam_repl = ig('ɢ')
    text = re.sub(
        r'(?<![\\a-zA-Z])\\Gamma(?![a-zA-Z_{])',
        lambda m: _gam_repl,
        text
    )

    # ── 6. Standalone \Omega in math (without subscript) — Ω primitive ────────
    _om_repl = ig('Ω')
    text = re.sub(
        r'(?<![\\a-zA-Z])\\Omega(?![a-zA-Z_{])',
        lambda m: _om_repl,
        text
    )

    # ── 7. Family list patterns ── ($F,G,S$), ($D,R,\Gamma,H,\Omega$), etc. ──
    # These appear in the text as fixed patterns; handle as literal replacements.
    LITERAL = [
        # 3-family
        ('($F,G,S$)', f'(${ig("ƒ")},{ig("Γ")},{ig("Σ")}$)'),
        # 4-family
        ('($D,R,\\Gamma,H,\\Omega$)',
         f'(${ig("Ð")},{ig("Ř")},{ig("ɢ")},{ig("Ħ")},{ig("Ω")}$)'),
        # 5-family
        ('($T,P,\\Phi,K$)',
         f'(${ig("Þ")},{ig("Φ")},{ig("⊙")},{ig("Ç")}$)'),
        # tikz node standalone labels (X\\X_sub form already handled by #1/#2)
        # Table standalone headers
        ('$D$ & Dimensionality', f'${ig("Ð")}$ & Dimensionality'),
        ('$T$ & Topology',       f'${ig("Þ")}$ & Topology'),
        ('$R$ & Relational mode', f'${ig("Ř")}$ & Relational mode'),
        ('$P$ & Parity',         f'${ig("Φ")}$ & Parity'),
        ('$F$ & Fidelity',       f'${ig("ƒ")}$ & Fidelity'),
        ('$K$ & Kinetics',       f'${ig("Ç")}$ & Kinetics'),
        ('$G$ & Scope',          f'${ig("Γ")}$ & Scope'),
        ('$\\Gamma$ & Interaction grammar', f'${ig("ɢ")}$ & Interaction grammar'),
        ('$\\Phi$ & Criticality', f'${ig("⊙")}$ & Criticality'),
        ('$H$ & Temporal',       f'${ig("Ħ")}$ & Temporal'),
        ('$\\Sigma$ & Stoichiometry', f'${ig("Σ")}$ & Stoichiometry'),
        ('$\\Omega$ & Winding',  f'${ig("Ω")}$ & Winding'),
        # tikz node primitive-label pairs: {$X$\\$X_sub$}
        ('{$K$\\\\', f'${{{ig("Ç")}}}\\\\'),
        ('{$F$\\\\', f'${{{ig("ƒ")}}}\\\\'),
        ('{$R$\\\\', f'${{{ig("Ř")}}}\\\\'),
        ('{$T$\\\\', f'${{{ig("Þ")}}}\\\\'),
        ('{$D$\\\\', f'${{{ig("Ð")}}}\\\\'),
        ('{$\\Phi$\\\\', f'${{{ig("⊙")}}}\\\\'),
        ('{$\\Omega$\\\\', f'${{{ig("Ω")}}}\\\\'),
        ('{$\\Gamma$\\\\', f'${{{ig("ɢ")}}}\\\\'),
    ]
    for old, new in LITERAL:
        text = text.replace(old, new)

    return text


def process_macros(text):
    """Update SO_BELOW.tex macro definitions."""
    MACRO_REPLACEMENTS = [
        (r'\newcommand{\Phic}{\Phi_{\text{ctyogh}}}',
         f'\\newcommand{{\\Phic}}{{{ig("⊙", "_{{\\text{{ctyogh}}}}")}}}'),
        (r'\newcommand{\Ppm}{P_{\text{pipevar}}}',
         f'\\newcommand{{\\Ppm}}{{{ig("Φ", "_{{\\text{{pipevar}}}}")}}}'),
        (r'\newcommand{\Ppms}{P_{\text{doublebarpipe}}}',
         f'\\newcommand{{\\Ppms}}{{{ig("Φ", "_{{\\text{{doublebarpipe}}}}")}}}'),
        (r'\newcommand{\OmegaZ}{\Omega_{\text{dzlig}}}',
         f'\\newcommand{{\\OmegaZ}}{{{ig("Ω", "_{{\\text{{dzlig}}}}")}}}'),
        (r'\newcommand{\OmegaZtwo}{\Omega_{\text{crtwo}}}',
         f'\\newcommand{{\\OmegaZtwo}}{{{ig("Ω", "_{{\\text{{crtwo}}}}")}}}'),
        (r'\newcommand{\GamSeq}{\Gamma_{\to}}',
         f'\\newcommand{{\\GamSeq}}{{{ig("ɢ", "_{{\\to}}")}}}'),
        (r'\newcommand{\GamBrd}{\Gamma_{\text{doublevertline}}}',
         f'\\newcommand{{\\GamBrd}}{{{ig("ɢ", "_{{\\text{{doublevertline}}}}")}}}'),
        (r'\newcommand{\Tbw}{T_{\mathord{\bowtie}}}',
         f'\\newcommand{{\\Tbw}}{{{ig("Þ", "_{{\\mathord{{\\bowtie}}}}")}}}'),
        (r'\newcommand{\Tin}{T_{\mathord{\subset}}}',
         f'\\newcommand{{\\Tin}}{{{ig("Þ", "_{{\\mathord{{\\subset}}}}")}}}'),
        (r'\newcommand{\Tbox}{T_{\mathord{\boxtimes}}}',
         f'\\newcommand{{\\Tbox}}{{{ig("Þ", "_{{\\mathord{{\\boxtimes}}}}")}}}'),
    ]
    for old, new in MACRO_REPLACEMENTS:
        text = text.replace(old, new)
    return text


if __name__ == '__main__':
    paths = sys.argv[1:] or []
    for path in paths:
        p = Path(path)
        original = p.read_text(encoding='utf-8')
        fixed = process(original)
        if 'SO_BELOW' in p.name or 'SB' in p.name:
            fixed = process_macros(fixed)
        if fixed != original:
            p.write_text(fixed, encoding='utf-8')
            n = sum(1 for a, b in zip(original, fixed) if a != b)
            print(f'Fixed {p.name}: ~{n} chars changed')
        else:
            print(f'Clean: {p.name}')
