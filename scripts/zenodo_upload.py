#!/usr/bin/env python3
"""
zenodo_upload.py — Zenodo uploader for Imscribing Grammar publications.

Quick start:
  python3 zenodo_upload.py paper.pdf               # sandbox draft, prompts pre-filled
  python3 zenodo_upload.py -y paper.pdf            # sandbox, no prompts (auto everything)
  python3 zenodo_upload.py --live -y paper.pdf     # publish to zenodo.org, no prompts
  python3 zenodo_upload.py --list                  # see all your deposits
  python3 zenodo_upload.py --update 12345 new.pdf  # add file to existing deposit

Metadata is auto-extracted from the associated .md source file (same stem, searched
in the file's directory and ~/imscribing_grammar/**).  Falls back to PDF metadata,
then to interactive prompts for anything that couldn't be found.

Token setup (one-time):
  export ZENODO_SANDBOX_TOKEN=...   # from sandbox.zenodo.org/account/settings/applications
  export ZENODO_TOKEN=...           # from zenodo.org/account/settings/applications
  (both need scopes: deposit:write  deposit:actions)
"""

import datetime
import os
import re
import subprocess
import sys
import json
import argparse
import textwrap
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("requests not installed — run: uv pip install requests")


# ── Constants ────────────────────────────────────────────────────────────────

BASE = {
    "sandbox": "https://sandbox.zenodo.org/api",
    "live":    "https://zenodo.org/api",
}
SITE = {
    "sandbox": "https://sandbox.zenodo.org",
    "live":    "https://zenodo.org",
}

DEFAULT_CREATOR = {
    "name":        "Mills, Lando",
    "orcid":       "0000-0003-0003-0552",
    "affiliation": "Independent Researcher",
}

DEFAULT_CONTRIBUTOR_LARSON = {
    "name": "Larson, Harry T.",
    "type": "Other",
}

CRYSTALLINE_BRANCH = "crystalline/manuscripts3-2026-07-07"
CRYSTALLINE_TAG    = "crystalline-manuscripts3-v1"
P4RA_COMMIT        = "eea2c0c"
MOMONAD_COMMIT     = "16da4a9"

PROG_LANG_NAMES = {
    "lean":   "Lean",
    "rust":   "Rust",
    "python": "Python",
}

# Per-manuscript Zenodo profiles (repository box, method, languages, default links).
MANUSCRIPT_PROFILES: dict[str, dict] = {
    "sic_povm_stark_hilbert12_lifted": {
        "code_repository": "https://github.com/umpolungfish/p4rakernel",
        "programming_languages": ["lean"],
        "method": (
            "Lean 4 machine-checked formalization of SIC-POVM existence, "
            "Belnap multilattice structure, and the Stark--Zauner--Hilbert chain."
        ),
        "extra_related": [
            "https://github.com/umpolungfish/ig-docs",
            "https://github.com/umpolungfish/imscribing_grammar",
            "https://github.com/umpolungfish",
            "https://orcid.org/0000-0003-0003-0552",
            "https://landomills.com/",
            "https://imscribe.com/",
        ],
        "companions": ["witness_vessel", "chrysopoeia_2048"],
    },
    "witness_vessel_lifted": {
        "code_repository": "https://github.com/umpolungfish/p4rakernel",
        "programming_languages": ["lean", "rust"],
        "method": (
            "Lean 4 proof verification of witness-vessel lossless transport, "
            "paired with bare-metal Rust execution in mOMonadOS under QEMU."
        ),
        "extra_related": [
            "https://github.com/umpolungfish/momonad_os",
            "https://github.com/umpolungfish/ig-docs",
            "https://github.com/umpolungfish/imscribing_grammar",
            "https://github.com/umpolungfish",
            "https://orcid.org/0000-0003-0003-0552",
            "https://landomills.com/",
            "https://imscribe.com/",
        ],
        "companions": ["sic_povm_stark_hilbert12", "chrysopoeia_2048"],
    },
    "chrysopoeia_2048_lifted": {
        "code_repository": "https://github.com/umpolungfish/p4rakernel",
        "programming_languages": ["lean"],
        "method": (
            "Explicit algebraic construction program for the $d=2048$ SIC-POVM moduli; "
            "PARI/GP field computations with Lean 4 companion formalization."
        ),
        "extra_related": [
            "https://github.com/umpolungfish/ig-docs",
            "https://github.com/umpolungfish/imscribing_grammar",
            "https://github.com/umpolungfish",
            "https://orcid.org/0000-0003-0003-0552",
            "https://landomills.com/",
            "https://imscribe.com/",
        ],
        "companions": ["sic_povm_stark_hilbert12", "witness_vessel"],
    },
    "alt_sic_moduli_conductor": {
        "code_repository": "https://github.com/umpolungfish/p4rakernel",
        "programming_languages": ["lean", "rust"],
        "method": (
            "Ray class field computation in PARI/GP determines the conductor of the "
            "SIC-POVM moduli field; the tower is discharged in Lean 4 with no axioms, "
            "and the arithmetic at $d=2048$ runs in the mOMonadOS bare-metal kernel."
        ),
        "extra_related": [
            "https://github.com/umpolungfish/momonad_os",
            "https://github.com/umpolungfish/ig-docs",
            "https://github.com/umpolungfish/imscribing_grammar",
            "https://github.com/umpolungfish",
            "https://orcid.org/0000-0003-0003-0552",
            "https://landomills.com/",
            "https://imscribe.com/",
        ],
        "companions": ["sic_povm_stark_hilbert12", "witness_vessel", "chrysopoeia_2048"],
        "crystalline_branch": "crystalline/sic-moduli-conductor-2026-08-08",
        "crystalline_tag":    "crystalline-sic-moduli-conductor-v2",
        "p4ra_commit":        "40803b7",
        "momonad_commit":     "1b0823d",
    },
}

UPLOAD_TYPES = {
    "publication": "Publication  (preprint, article, report, thesis…)",
    "dataset":     "Dataset",
    "software":    "Software",
    "other":       "Other",
}

PUB_SUBTYPES = {
    "preprint":     "Preprint",
    "article":      "Journal article",
    "report":       "Technical report",
    "workingpaper": "Working paper",
    "other":        "Other",
}

ACCESS_RIGHTS = {
    "open":   "Open access",
    "closed": "Closed",
}

RELATION_TYPES = {
    "isVersionOf":           "Is new version of (prior DOI/URL)",
    "isPreviousVersionOf":   "Is previous version of (newer DOI/URL)",
    "isPartOf":              "Is part of a series/collection",
    "hasPart":               "Has part (companion file DOI/URL)",
    "isSupplementTo":        "Is supplement to another paper",
    "isSupplementedBy":      "Is supplemented by (code, data…)",
    "references":            "References (cites another work)",
    "isReferencedBy":        "Is referenced by another work",
    "isIdenticalTo":         "Is identical to (mirror/alt URL)",
    "isAlternateIdentifier": "Alternate identifier (arXiv, handle…)",
}

IDENTIFIER_SCHEMES = {
    "doi":    "DOI  (10.xxxx/…)",
    "url":    "URL  (https://…)",
    "arxiv":  "arXiv  (arXiv:xxxx.xxxxx)",
    "handle": "Handle",
    "isbn":   "ISBN",
    "issn":   "ISSN",
    "other":  "Other",
}

CONTRIBUTOR_TYPES = {
    "Researcher":    "Researcher",
    "Editor":        "Editor",
    "DataCollector": "Data collector",
    "DataCurator":   "Data curator",
    "DataManager":   "Data manager",
    "Producer":      "Producer",
    "Supervisor":    "Supervisor",
    "Sponsor":       "Sponsor",
    "Other":         "Other",
}

# IG publications use the LUNLICENSE (hardcoded; authoritative, do not fetch ~/).
# Zenodo has no LUNLICENSE ID; "other-open" is the deposit license field only.
# Never inject license text into Notes or attach LUNLICENSE as a deposit file.
DEFAULT_LICENSE = "other-open"
LUNLICENSE_TEXT = """\
This is free and unencumbered and released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this dedicate any and all copyright interest to the public domain.
We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication
to be an overt act of relinquishment in perpetuity of all present and future
rights to this under any law.

THIS IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THIS OR THE USE OR
OTHER DEALINGS IN THIS.

For more information, please refer to <https://unlicense.org/>
"""
DEFAULT_UPLOAD_TYPE = "publication"
DEFAULT_PUB_SUBTYPE = "preprint"
DEFAULT_ACCESS      = "open"
DEFAULT_LANGUAGE    = "eng"
DEFAULT_KEYWORDS    = ["Imscribing Grammar", "imscription"]
DEFAULT_PUBLISHER   = "umpolungfish"

# Directories searched (in order) when looking for a .md source alongside a PDF
IG_SEARCH_DIRS = [
    Path.home() / "imscribing_grammar",
    Path.home() / "imscribing_grammar" / "manuscripts",
    Path.home() / "imscribing_grammar" / "markdown",
    Path.home() / "imscribing_grammar" / "markdown" / "core",
]


# ── Auto-extraction ───────────────────────────────────────────────────────────

def _strip_md(text: str) -> str:
    """Remove markdown formatting and inline LaTeX for plain-text fields."""
    text = re.sub(r'\$\$[\s\S]+?\$\$', '', text)          # block math
    text = re.sub(r'\$[^$\n]+?\$', '', text)               # inline math
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)         # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)             # italic
    text = re.sub(r'`[^`]+`', '', text)                    # code spans
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)   # links
    text = re.sub(r'<https?://[^>]+>', '', text)           # bare URLs
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _format_zenodo_desc(text: str) -> str:
    """
    Format text for Zenodo's description field, which renders MathJax.
    Preserves $...$ math; strips only markdown formatting (bold, italic, links).
    Simplifies heavy LaTeX inside math: \\mathrm{X} → X, \\mathbf{X} → X,
    \\mathbb{X} → X, \\times → ×, \\circ → ∘, -- → –.
    """
    # Strip markdown formatting but keep math
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'<https?://[^>]+>', '', text)
    # Simplify LaTeX inside math spans
    def _simplify_math(m):
        s = m.group(0)
        s = re.sub(r'\\(?:mathrm|mathbf|mathbb|text)\{([^}]+)\}', r'\1', s)
        s = s.replace(r'\times', '×').replace(r'\circ', '∘')
        s = s.replace(r'\ne', '≠').replace(r'\neq', '≠')
        s = s.replace(r'\propto', '∝').replace(r'\to', '→')
        s = s.replace(r'\varepsilon', 'ε').replace(r'\epsilon', 'ε')
        s = s.replace(r'\Omega', '◻').replace(r'\omega', 'ω')
        s = s.replace(r'\mu', 'μ').replace(r'\delta', 'δ')
        return s
    text = re.sub(r'\$[^$\n]+?\$', _simplify_math, text)
    # En-dashes
    text = text.replace(' -- ', ' – ').replace('--', '–')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def find_md_source(pdf: Path) -> Path | None:
    """Return the .md file whose stem matches the PDF, searching IG directories."""
    stem = pdf.stem
    candidates = [
        pdf.with_suffix('.md'),
        pdf.parent / f"{stem}.md",
        *[d / f"{stem}.md" for d in IG_SEARCH_DIRS],
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


IG_TEX_DIRS = [
    Path.home() / "imsgct" / "imscribing_grammar" / "manuscripts",
    Path.home() / "imscribing_grammar" / "manuscripts",
]


def find_tex_source(pdf: Path) -> Path | None:
    """Return the .tex file whose stem matches the PDF."""
    stem = pdf.stem
    candidates = [
        pdf.with_suffix('.tex'),
        pdf.parent / f"{stem}.tex",
        *[d / f"{stem}.tex" for d in IG_TEX_DIRS],
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _prog_lang(lang_id: str) -> dict:
    return {"id": lang_id, "title": {"en": PROG_LANG_NAMES.get(lang_id, lang_id)}}


def _tex_section(text: str, heading: str) -> str:
    m = re.search(
        rf'\\section\*?\{{{re.escape(heading)}\}}\s*([\s\S]+?)'
        r'(?=\\section\*?\{|\\appendix|\\begin\{{thebibliography\}}|\\end\{{document\}})',
        text,
    )
    return m.group(1).strip() if m else ""


def _tex_to_plain(text: str) -> str:
    text = _strip_citations(text)
    text = re.sub(r'\\url\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\href\{[^}]+\}\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\texttt\{([^}]+)\}', r'\1', text)
    text = text.replace('\\\\', ' ')
    text = text.replace('\\', ' ')
    text = _strip_latex(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _github_urls(text: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r'\\url\{(https?://[^}]+)\}', text):
        url = m.group(1).strip()
        if "github.com" in url:
            urls.append(url)
    for m in re.finditer(r'\\href\{(https?://[^}]+)\}', text):
        url = m.group(1).strip()
        if "github.com" in url:
            urls.append(url)
    for m in re.finditer(r'<(https?://github\.com[^>\s]+)>', text):
        urls.append(m.group(1).strip())
    for m in re.finditer(r'\[[^\]]*\]\((https?://github\.com[^)]+)\)', text):
        urls.append(m.group(1).strip())
    out: list[str] = []
    for url in urls:
        url = url.rstrip('.,;)]}')
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def _related_url(identifier: str, relation: str = "isSupplementedBy") -> dict:
    return {"identifier": identifier, "scheme": "url", "relation": relation}


def _merge_related_identifiers(extracted: dict, stem: str) -> list[dict]:
    profile = MANUSCRIPT_PROFILES.get(stem, {})
    seen: set[str] = set()
    related: list[dict] = []

    def add(url: str, relation: str = "isSupplementedBy") -> None:
        url = url.rstrip('/')
        if not url or url in seen:
            return
        seen.add(url)
        related.append(_related_url(url, relation))

    for url in extracted.get("github_urls", []):
        add(url)
    for url in profile.get("extra_related", []):
        add(url)
    repo = profile.get("code_repository")
    if repo:
        add(repo)
    if not related:
        add("https://github.com/umpolungfish/imscribing_grammar")
    return related


def _build_notes(extracted: dict, stem: str) -> str:
    profile = MANUSCRIPT_PROFILES.get(stem, {})
    parts: list[str] = []

    artifact = extracted.get("artifact_text", "")
    if artifact:
        parts.append(_tex_to_plain(artifact))

    branch = profile.get("crystalline_branch", CRYSTALLINE_BRANCH)
    tag    = profile.get("crystalline_tag", CRYSTALLINE_TAG)
    commit = profile.get("p4ra_commit", P4RA_COMMIT)
    parts.append(
        f"Frozen crystalline snapshot: branch {branch}, tag {tag}; "
        f"p4rakernel commit {commit}."
    )
    momonad = profile.get("momonad_commit", MOMONAD_COMMIT if stem == "witness_vessel_lifted" else "")
    if momonad:
        parts.append(f"mOMonadOS commit {momonad}.")
    parts.append("Manuscript trio frozen in ig-docs on the same branch and tag.")

    companions = profile.get("companions", [])
    if companions:
        parts.append(
            "Companion preprints in the manuscripts3 SIC trio: "
            + ", ".join(companions) + "."
        )

    ack = extracted.get("acknowledgements_text", "")
    if ack:
        parts.append("Acknowledgements: " + _tex_to_plain(ack))

    langs = profile.get("programming_languages", [])
    if langs:
        parts.append(
            "Programming languages: "
            + ", ".join(PROG_LANG_NAMES.get(l, l) for l in langs)
            + ("; PARI/GP field scripts where applicable." if stem == "chrysopoeia_2048_lifted" else ".")
        )

    parts.append(f"Publisher: {DEFAULT_PUBLISHER}. License: LUNLICENSE (other-open on Zenodo).")
    return " ".join(p.strip() for p in parts if p.strip())


def _build_custom_fields(stem: str) -> dict:
    profile = MANUSCRIPT_PROFILES.get(stem, {})
    custom: dict = {}
    repo = profile.get("code_repository")
    if repo:
        custom["code:codeRepository"] = repo
    langs = profile.get("programming_languages", [])
    if langs:
        custom["code:programmingLanguage"] = [_prog_lang(l) for l in langs]
    return custom


def _assemble_deposit_meta(extracted: dict, files: list[Path]) -> dict:
    stem = files[0].stem if files else ""
    profile = MANUSCRIPT_PROFILES.get(stem, {})

    title = (
        extracted.get("title")
        or stem.replace("_", " ").replace("-", " ").title()
    )
    description = extracted.get("description", "")
    if not title or not description:
        return {}

    creators = (
        _parse_author_str(extracted["author_str"])
        if "author_str" in extracted
        else [DEFAULT_CREATOR.copy()]
    )

    meta: dict = {
        "title":              title,
        "description":        description,
        "upload_type":        DEFAULT_UPLOAD_TYPE,
        "publication_type":   DEFAULT_PUB_SUBTYPE,
        "publication_date":   extracted.get("date", datetime.date.today().isoformat()),
        "creators":           creators,
        "contributors":       [DEFAULT_CONTRIBUTOR_LARSON.copy()],
        "access_right":       DEFAULT_ACCESS,
        "license":            DEFAULT_LICENSE,
        "language":           DEFAULT_LANGUAGE,
        "keywords":           extracted.get("keywords", list(DEFAULT_KEYWORDS)),
        "version":            extracted.get("version", "1.0"),
        "imprint_publisher":  DEFAULT_PUBLISHER,
        "method":             profile.get("method", ""),
        "notes":              _build_notes(extracted, stem),
        "related_identifiers": _merge_related_identifiers(extracted, stem),
    }

    custom = _build_custom_fields(stem)
    if custom:
        meta["custom"] = custom
    if extracted.get("references"):
        meta["references"] = extracted["references"]
    return meta


def _strip_citations(s: str) -> str:
    """Remove LaTeX citation commands without leaving bib keys behind."""
    s = re.sub(r'\\cite\w*(?:\[[^\]]*\])?\{[^}]*\}', '', s)
    s = re.sub(r'Companion to\s*,\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\(\s*,', '(', s)
    s = re.sub(r',\s*,', ',', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip(' ,')


def _strip_latex(s: str) -> str:
    """Strip LaTeX commands for plain text."""
    s = re.sub(r'\\emph\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\textbf\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\textit\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\normalsize\b', '', s)
    s = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z~@]+\b', ' ', s)
    s = re.sub(r'\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def _extract_braced_arg(text: str, command: str) -> str | None:
    """Return the full braced argument for a LaTeX command, handling nesting."""
    m = re.search(re.escape(command) + r'\{', text)
    if not m:
        return None
    i = m.end()
    depth = 1
    start = i
    while i < len(text) and depth:
        ch = text[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        i += 1
    if depth != 0:
        return None
    return text[start:i - 1]


def _parse_tex_date(raw: str) -> str | None:
    """Parse \\date{7 July 2026} (and common variants) to ISO YYYY-MM-DD."""
    raw = _strip_latex(raw.strip())
    if re.match(r'\d{4}-\d{2}-\d{2}$', raw):
        return raw
    m = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', raw)
    if not m:
        return None
    day, month_name, year = m.groups()
    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
    }
    month = months.get(month_name.lower())
    if not month:
        return None
    return f"{year}-{month:02d}-{int(day):02d}"


def extract_from_tex(path: Path) -> dict:
    """Extract title, author, abstract, keywords, and references from a .tex source."""
    text = path.read_text(encoding="utf-8", errors="replace")
    info: dict = {}

    # Title (nested braces, multi-line \\ breaks)
    title_raw = _extract_braced_arg(text, r'\title')
    if title_raw:
        title = _strip_latex(title_raw.replace('\\\\', ' ')).strip('{} ')
        info["title"] = title

    # Author — strip LaTeX escapes, % comments, and optional \thanks tail
    author_raw = _extract_braced_arg(text, r'\author')
    if author_raw:
        name_part = author_raw.split('\\\\')[0].split('%')[0]
        name_part = re.sub(r'\\(?:thanks|footnote)\b.*', '', name_part, flags=re.DOTALL)
        name_part = name_part.replace('\\', ' ')
        info["author_str"] = _strip_latex(name_part).strip()

    # Abstract — \begin{abstract}...\end{abstract} or \subsection*{Abstract} paragraph
    m = re.search(r'\\begin\{abstract\}([\s\S]+?)\\end\{abstract\}', text)
    if not m:
        m = re.search(
            r'\\subsection\*\{Abstract\}\s*\n\n([\s\S]+?)(?=\n\n\\begin\{center\}|\n\\(?:begin|subsection|section)\b)',
            text)
    if m:
        raw = m.group(1).strip()
        raw = _strip_citations(raw)
        # Preserve $...$ math, strip everything else
        raw = re.sub(r'\\emph\{([^}]+)\}', r'\1', raw)
        raw = re.sub(r'\\textbf\{([^}]+)\}', r'\1', raw)
        raw = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', raw)
        raw = re.sub(r'\\[a-zA-Z~@]+\b', '', raw)
        raw = re.sub(r'\{([^}]*)\}', r'\1', raw)
        raw = re.sub(r'\s+', ' ', raw)
        info["description"] = _format_zenodo_desc(raw.strip())[:2000]

    # Keywords — \noindent\textbf{Keywords:} ... (ends at blank line or next \)
    m = re.search(
        r'\\(?:noindent\s*)?\\?textbf\{Keywords?:?\}\s*([\s\S]+?)(?:\n\n|\n\\(?:new|med|vspace|begin|section|sub))',
        text
    )
    if m:
        raw_kw = m.group(1).replace('~', ' ')
        # The separator is written $\cdot$, and stripping only the command
        # leaves the math delimiters behind as keywords of their own.
        raw_kw = re.sub(r'\$\s*\\cdot\s*\$|\\\(\s*\\cdot\s*\\\)|\\cdot|·', ',', raw_kw)
        raw_kw = _strip_latex(raw_kw)
        kws = [k.strip().strip('$').strip().rstrip(';.,')
               for k in re.split(r'[;,]', raw_kw) if k.strip()]
        kws = [k for k in kws if len(k) > 2]
        if kws:
            info["keywords"] = kws

    # References — \bibitem{key} text... (SO_BELOW style)
    refs: list[str] = []
    for m in re.finditer(
        r'\\bibitem\{[^}]+\}\s*([\s\S]+?)(?=\\bibitem\{|\\end\{thebibliography\})',
        text
    ):
        raw = m.group(1).strip()
        clean = re.sub(r'\\url\{[^}]+\}', '', raw)
        clean = _strip_latex(clean).replace('~', ' ')
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) > 20:
            refs.append(clean)

    # References — \item text... inside ## References itemize (AS_ABOVE style)
    if not refs:
        ref_section = re.search(
            r'\\subsection\{[^}]*[Rr]eferences?[^}]*\}[\s\S]+?\\begin\{itemize\}([\s\S]+?)\\end\{itemize\}',
            text
        )
        if ref_section:
            for m in re.finditer(r'\\item\s+([\s\S]+?)(?=\\item|\Z)', ref_section.group(1)):
                clean = _strip_latex(m.group(1).strip())
                if len(clean) > 20:
                    refs.append(clean)

    if refs:
        info["references"] = refs

    artifact = _tex_section(text, "Artifact statement")
    if artifact:
        info["artifact_text"] = artifact
    ack = _tex_section(text, "Acknowledgements")
    if ack:
        info["acknowledgements_text"] = ack

    github_urls = _github_urls(text)
    if github_urls:
        info["github_urls"] = github_urls

    date_raw = _extract_braced_arg(text, r'\date')
    if date_raw:
        tex_date = _parse_tex_date(date_raw)
        if tex_date:
            info["date"] = tex_date
    if "date" not in info:
        info["date"] = _git_date(path)
    ver = _git_version(path)
    if ver:
        info["version"] = ver
    return info


def _parse_yaml_fm(text: str) -> dict:
    """Extract key fields from YAML frontmatter block (--- ... ---)."""
    out: dict = {}
    fm_m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not fm_m:
        return out
    fm = fm_m.group(1)
    # title
    t = re.search(r'^title:\s*"([^"]+)"', fm, re.MULTILINE)
    if not t:
        t = re.search(r'^title:\s*([^|{].+)', fm, re.MULTILINE)
    if t:
        out["title"] = t.group(1).strip()
    # author
    a = re.search(r'^author:\s*(.+)', fm, re.MULTILINE)
    if a:
        out["author_str"] = a.group(1).strip().strip('"')
    # abstract (block scalar |)
    ab = re.search(r'^abstract:\s*\|\n((?:  .+\n?)+)', fm, re.MULTILINE)
    if ab:
        raw = re.sub(r'^  ', '', ab.group(1), flags=re.MULTILINE).strip()
        out["abstract"] = _strip_md(raw)
    # keywords (YAML list)
    kw = re.search(r'^keywords:\n((?:  - .+\n?)+)', fm, re.MULTILINE)
    if kw:
        out["yaml_keywords"] = re.findall(r'  - (.+)', kw.group(1))
    return out


def extract_from_md(path: Path) -> dict:
    """
    Comprehensive extraction from a markdown source file:
    title, author, full abstract, keywords (headings + table cells + domain terms),
    related identifiers (all URLs, DOIs, arXiv IDs), git date, version.
    """
    text = path.read_text(encoding="utf-8")
    info: dict = {}

    # ── YAML frontmatter (title, author, abstract, keywords) ─────────────────
    fm = _parse_yaml_fm(text)
    if fm.get("title"):
        info["title"] = fm["title"]
    if fm.get("author_str"):
        info["author_str"] = fm["author_str"]
    if fm.get("abstract"):
        info["description"] = _format_zenodo_desc(fm["abstract"])[:2000]

    # ── Title fallback — first # heading ────────────────────────────────────
    if "title" not in info:
        m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        if m:
            info["title"] = m.group(1).strip()

    # ── Author(s) fallback ───────────────────────────────────────────────────
    if "author_str" not in info:
        m = re.search(r'\*\*Authors?:\*\*\s*(.+)', text)
        if m:
            info["author_str"] = m.group(1).strip()

    # ── Description fallback — ## Abstract section ────────────────────────
    if "description" not in info:
        m = re.search(r'##\s+Abstract\s*\n\n([\s\S]+?)(?=\n##|\Z)', text)
        if m:
            info["description"] = _format_zenodo_desc(m.group(1).strip())[:2000]

    # ── Date from git log ────────────────────────────────────────────────────
    info["date"] = _git_date(path)

    # ── Version from nearest git tag ─────────────────────────────────────────
    ver = _git_version(path)
    if ver:
        info["version"] = ver

    # ── Keywords ─────────────────────────────────────────────────────────────
    keywords: set[str] = set(DEFAULT_KEYWORDS)

    # YAML list keywords (already parsed)
    for k in fm.get("yaml_keywords", []):
        if k.strip():
            keywords.add(k.strip())

    # Explicit inline "keywords:" frontmatter line (fallback for single-line format)
    for pat in (r'^keywords:\s*([^\n|{].+)$', r'^tags:\s*(.+)$'):
        m = re.search(pat, text, re.MULTILINE | re.IGNORECASE)
        if m:
            for k in re.split(r',|;', m.group(1)):
                k = k.strip().strip('"\'')
                if k:
                    keywords.add(k)

    # H2/H3 section headings — grab the subject term before ":"
    _SKIP_HEADS = {
        "abstract", "the problem", "references", "overview", "introduction",
        "conclusion", "results", "methods", "discussion", "background",
        "the type system", "the open problems", "the one gate",
        "the lean formalization", "concrete pathways", "the gematria of open problems",
        "latent self-correction in the lattice imscription process",
        "the millennium seven", "the non-millennium seven",
        "overdetermination", "the frobenius condition as structural validator",
        "primitive stability under perturbation", "empirical calibration",
        "deep dives", "the anomaly that is not",
    }
    for m in re.finditer(r'^#{2,3}\s+(.+)$', text, re.MULTILINE):
        heading = m.group(1).strip()
        # Strip any ": subtitle" part
        subject = re.split(r'\s*:\s+', heading)[0].strip()
        # Split compound headings on " and "
        for part in re.split(r'\s+and\s+', subject, flags=re.IGNORECASE):
            part = part.strip()
            if part and part.lower() not in _SKIP_HEADS and 2 < len(part) < 60:
                keywords.add(part)

    # Table rows — problem names (first cell that isn't a header)
    _SKIP_CELLS = {
        "problem", "tuple", "gate", "pair", "channel", "primitive",
        "promotion", "function", "distance", "module", "lines", "proved",
        "axioms", "status", "priority", "task", "file", "area", "files",
        "d · gate", "$d$ · gate", "d", "$d$",
    }
    for m in re.finditer(r'^\|\s*([^|$\n]{2,50}?)\s*(?:\(|\$|\|)', text, re.MULTILINE):
        cell = m.group(1).strip().rstrip('(').strip()
        if cell and cell.lower() not in _SKIP_CELLS and not cell.startswith('-'):
            keywords.add(cell)

    # Domain-specific terms present in the document
    _DOMAIN = {
        "Lean 4":                  "Lean 4",
        "Lean4":                   "Lean 4",
        "Mathlib":                 "Mathlib",
        "formal verification":     "formal verification",
        "ZFC":                     "ZFC",
        "Frobenius":               "Frobenius condition",
        "Millennium Prize":        "Millennium Prize Problems",
        "number theory":           "number theory",
        "algebraic geometry":      "algebraic geometry",
        "quantum information":     "quantum information",
        "mathematical physics":    "mathematical physics",
        "type":         "type theory",
        "Shavian":                 "Shavian notation",
        "gematria":                "gematria",
        "ZFC_fe":                  "ZFC_fe",
        "paraconsistent":          "paraconsistent logic",
        "dialetheic":              "dialetheic logic",
        "Imscribing Grammar":      "Imscribing Grammar",
        "imscription":             "imscription",
        "primitive":               "primitive coordinates",
        "Frobenius-exact":         "Frobenius-exact ZFC",
    }
    for trigger, keyword in _DOMAIN.items():
        if trigger in text:
            keywords.add(keyword)

    # Clean up keywords
    clean = set()
    for k in keywords:
        k = k.strip().rstrip('.,;:')
        if (3 < len(k) < 60
                and not k.startswith(('|', '$', '-', '#', '*', '`'))
                and '→' not in k and '←' not in k   # table arrow pairs
                and not re.match(r'^[\W\d]+$', k)    # pure symbols/numbers
                and '.lean' not in k                  # no filenames
                and not k.startswith('`')             # no code spans
        ):
            clean.add(k)
    info["keywords"] = sorted(clean)

    # ── Related identifiers (isSupplementedBy only — repo links etc.) ────────
    related: list[dict] = []
    seen_rel: set[tuple] = set()

    def add_supplemented_by(url: str) -> None:
        url = url.strip().rstrip('.,;)]}')
        key = (url, "url")
        if key not in seen_rel and url:
            seen_rel.add(key)
            related.append({"identifier": url, "scheme": "url", "relation": "isSupplementedBy"})

    for m in re.finditer(r'<(https?://github\.com[^>\s]+)>', text):
        add_supplemented_by(m.group(1))
    for m in re.finditer(r'\[[^\]]*\]\((https?://github\.com[^)]+)\)', text):
        add_supplemented_by(m.group(1))

    if related:
        info["related_identifiers"] = related

    # ── Plain-text bibliography → info["references"] (never related_identifiers) ──
    ref_entries = _parse_ref_entries(text)
    if ref_entries:
        info["references"] = [citation for _, citation in ref_entries]

    return info


def extract_from_pdf(path: Path) -> dict:
    """Pull metadata + full text from PDF, then run the same reference/keyword pipeline."""
    info: dict = {}
    full_text = ""
    try:
        import pypdf  # type: ignore
        reader = pypdf.PdfReader(str(path))
        # Metadata fields
        meta = reader.metadata or {}
        if meta.get("/Title"):
            info["title"] = str(meta["/Title"])
        if meta.get("/Author"):
            info["author_str"] = str(meta["/Author"])
        if meta.get("/Subject"):
            info["description"] = str(meta["/Subject"])[:2000]
        if meta.get("/Keywords"):
            raw_kws = str(meta["/Keywords"])
            info["keywords"] = [k.strip() for k in re.split(r'[,;]', raw_kws) if k.strip()]
        # Extract full text for reference parsing
        pages = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pass
        full_text = "\n".join(pages)
    except ImportError:
        pass
    except Exception:
        pass

    # Extract plain-text references from PDF text
    if full_text:
        ref_entries = _parse_ref_entries(full_text)
        if ref_entries:
            info["references"] = [citation for _, citation in ref_entries]

    return info


# ── CrossRef reference lookup ─────────────────────────────────────────────────

_CROSSREF_CACHE_PATH = Path.home() / ".cache" / "zenodo_crossref_cache.json"
_CROSSREF_UA = "zenodo_upload/2.0 (mailto:c.landonmills@gmail.com)"
_CROSSREF_SCORE_MIN = 60   # confidence threshold — lower = more matches, more false positives


def _parse_ref_entries(text: str) -> list[tuple[str, str]]:
    """
    Extract numbered reference entries from text.
    Returns list of (number_str, citation_text) tuples.
    Handles both markdown [N] format and plain "N." format from PDFs.
    """
    entries = []
    # Markdown format: [1] Author... through to the next [N] or end
    md_refs = re.findall(
        r'^\[(\d+)\]\s+(.+?)(?=\n\[\d+\]|\Z)',
        text, re.MULTILINE | re.DOTALL
    )
    if md_refs:
        for num, citation in md_refs:
            clean = _strip_md(citation.replace('\n', ' ')).strip()
            if len(clean) > 20:
                entries.append((num, clean))
        return entries
    # PDF format: "1. Author..." or "1 Author..."
    pdf_refs = re.findall(
        r'^(\d{1,3})[.\s]\s+([A-Z].+?)(?=\n\d{1,3}[.\s]\s+[A-Z]|\Z)',
        text, re.MULTILINE | re.DOTALL
    )
    for num, citation in pdf_refs:
        clean = re.sub(r'\s+', ' ', citation).strip()
        if len(clean) > 20:
            entries.append((num, clean))
    return entries


def _load_crossref_cache() -> dict:
    try:
        if _CROSSREF_CACHE_PATH.exists():
            return json.loads(_CROSSREF_CACHE_PATH.read_text())
    except Exception:
        pass
    return {}


def _save_crossref_cache(cache: dict) -> None:
    try:
        _CROSSREF_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CROSSREF_CACHE_PATH.write_text(json.dumps(cache, indent=2))
    except Exception:
        pass


def _crossref_doi(citation: str, cache: dict) -> str:
    """
    Look up a DOI for the given citation string via CrossRef.
    Results are cached; returns empty string if not found or score too low.
    """
    # Use first 200 chars as cache key (enough to be unique)
    key = citation[:200]
    if key in cache:
        return cache[key]

    doi = ""
    try:
        r = requests.get(
            "https://api.crossref.org/works",
            params={"query.bibliographic": citation[:500], "rows": 1, "select": "DOI,score"},
            headers={"User-Agent": _CROSSREF_UA},
            timeout=8,
        )
        if r.ok:
            items = r.json().get("message", {}).get("items", [])
            if items:
                item = items[0]
                if item.get("score", 0) >= _CROSSREF_SCORE_MIN:
                    doi = item.get("DOI", "")
    except Exception:
        pass

    cache[key] = doi
    return doi


def _git_version(path: Path) -> str:
    """Return nearest git tag (vX.Y or X.Y) for the repo containing path."""
    try:
        r = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True,
            cwd=path.parent if path.parent.exists() else Path.cwd(),
        )
        tag = r.stdout.strip().lstrip("v")
        if re.match(r'[\d.]+', tag):
            return tag
    except Exception:
        pass
    return ""


def _git_date(path: Path) -> str:
    """Return YYYY-MM-DD of the most recent git commit touching path, or today."""
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%as", "--", str(path)],
            capture_output=True, text=True,
            cwd=path.parent if path.parent.exists() else Path.cwd(),
        )
        date = r.stdout.strip()
        if re.match(r'\d{4}-\d{2}-\d{2}', date):
            return date
    except Exception:
        pass
    return datetime.date.today().isoformat()


def auto_extract(files: list[Path]) -> dict:
    """
    For each file, find its .tex or .md source (or fall back to PDF metadata).
    .tex preferred over .md; first file wins on conflicts.
    """
    merged: dict = {}
    for f in files:
        if f.suffix.lower() == ".tex":
            info = extract_from_tex(f)
        elif f.suffix.lower() in (".md", ".markdown"):
            info = extract_from_md(f)
        else:
            tex = find_tex_source(f)
            if tex:
                print(f"  ✦ Found TeX source: {tex}")
                info = extract_from_tex(tex)
            else:
                md = find_md_source(f)
                if md:
                    print(f"  ✦ Found source: {md}")
                    info = extract_from_md(md)
                else:
                    info = extract_from_pdf(f)
        for k, v in info.items():
            merged.setdefault(k, v)
    return merged


def _parse_author_str(author_str: str) -> list[dict]:
    """
    Turn a plain-text author string into Zenodo creator dicts.
    Handles 'Lando Mills', 'Mills, Lando', 'A. Smith and B. Jones', etc.
    Falls back to DEFAULT_CREATOR if the string matches the default author.
    """
    clean = re.sub(r'[%\\]+', ' ', author_str)
    clean = re.sub(r'\s+', ' ', clean).strip()
    if re.search(r'(?:c\.?\s*)?lando\s+mills|mills,?\s+(?:c\.?\s*)?lando', clean, re.IGNORECASE):
        return [DEFAULT_CREATOR.copy()]
    creators = []
    # Split on "and" or "," between names
    parts = re.split(r'\s+and\s+|;\s*', author_str, flags=re.IGNORECASE)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Already in "Last, First" format?
        if ',' in part:
            creators.append({"name": part})
        else:
            # Assume "First Last" — flip to "Last, First"
            tokens = part.split()
            if len(tokens) >= 2:
                creators.append({"name": f"{tokens[-1]}, {' '.join(tokens[:-1])}"})
            else:
                creators.append({"name": part})
    return creators or [DEFAULT_CREATOR.copy()]


# ── HTTP session ─────────────────────────────────────────────────────────────

def make_session(token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    })
    return s


def get_token(live: bool) -> str:
    env = "ZENODO_TOKEN" if live else "ZENODO_SANDBOX_TOKEN"
    tok = os.getenv(env, "").strip()
    if tok:
        return tok
    label = "zenodo.org" if live else "sandbox.zenodo.org"
    print(f"No {env} env var found.")
    tok = input(f"Paste your {label} token: ").strip()
    if not tok:
        sys.exit("Token required.")
    return tok


# ── API calls ────────────────────────────────────────────────────────────────

def api_create(session, base) -> dict:
    r = session.post(f"{base}/deposit/depositions", data="{}")
    _check(r, "create deposition")
    return r.json()


def api_upload_file(session, bucket_url: str, path: Path) -> None:
    size_kb = path.stat().st_size / 1024
    print(f"  ↑ {path.name}  ({size_kb:.0f} KB) ...", end=" ", flush=True)
    headers = {k: v for k, v in session.headers.items() if k != "Content-Type"}
    with open(path, "rb") as fh:
        r = requests.put(f"{bucket_url}/{path.name}", data=fh, headers=headers)
    _check(r, f"upload {path.name}")
    print("done")


def api_set_metadata(session, base, dep_id: int, metadata: dict) -> dict:
    r = session.put(
        f"{base}/deposit/depositions/{dep_id}",
        data=json.dumps({"metadata": metadata}),
    )
    _check(r, "set metadata")
    return r.json()


def api_publish(session, base, dep_id: int) -> dict:
    r = session.post(f"{base}/deposit/depositions/{dep_id}/actions/publish")
    _check(r, "publish")
    return r.json()


def api_list(session, base, size: int = 25) -> list:
    r = session.get(f"{base}/deposit/depositions",
                    params={"size": size, "sort": "mostrecent"})
    _check(r, "list deposits")
    return r.json()


def api_get(session, base, dep_id: int) -> dict:
    r = session.get(f"{base}/deposit/depositions/{dep_id}")
    _check(r, f"get deposit {dep_id}")
    return r.json()


def api_new_version(session, base, dep_id: int) -> dict:
    """Create a new version draft from a published record. Returns the new draft deposit."""
    r = session.post(f"{base}/deposit/depositions/{dep_id}/actions/newversion")
    _check(r, f"new version of {dep_id}")
    data = r.json()
    # Zenodo returns the *parent* record; latest draft is in links.latest_draft
    latest_draft_url = data.get("links", {}).get("latest_draft")
    if not latest_draft_url:
        return data
    r2 = session.get(latest_draft_url)
    _check(r2, "fetch new version draft")
    return r2.json()


def _check(r: requests.Response, action: str) -> None:
    if r.ok:
        return
    try:
        msg = r.json().get("message", r.text)
        errors = r.json().get("errors", [])
    except Exception:
        msg, errors = r.text, []
    print(f"\nError {r.status_code} during {action}: {msg}")
    for e in errors:
        print(f"  Field '{e.get('field')}': {e.get('message')}")
    sys.exit(1)


# ── Interactive prompts ───────────────────────────────────────────────────────

def prompt(label: str, default: str = "", required: bool = True) -> str:
    hint = f" [{default}]" if default else ""
    val = input(f"{label}{hint}: ").strip()
    if not val:
        if default:
            return default
        if required:
            sys.exit(f"{label} is required.")
        return ""
    return val


def choose(label: str, options: dict, default_key: str = "") -> str:
    keys = list(options)
    print(f"\n{label}:")
    for i, (k, desc) in enumerate(options.items(), 1):
        marker = "  *" if k == default_key else "   "
        print(f"{marker} {i}. {desc}")
    hint = f" [{'*' if default_key else '1'}]"
    while True:
        raw = input(f"Choice{hint}: ").strip()
        if not raw and default_key:
            return default_key
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            pass
        print(f"  Enter 1–{len(keys)}.")


def _collect_creators(default_creators: list[dict]) -> list[dict]:
    names_str = "; ".join(c["name"] for c in default_creators)
    print(f"\nCreators / Authors (detected: {names_str})")
    override = input("  Press Enter to accept, or type 'Family, Given' to replace: ").strip()
    if override:
        creators = [{"name": override}]
        orcid = input("  ORCID (optional): ").strip()
        if orcid:
            creators[0]["orcid"] = orcid
        affil = input("  Affiliation (optional): ").strip()
        if affil:
            creators[0]["affiliation"] = affil
    else:
        creators = [c.copy() for c in default_creators]

    while True:
        more = input("  Add another author? [y/N] ").strip().lower()
        if more not in ("y", "yes"):
            break
        name = input("    Name (Family, Given): ").strip()
        if not name:
            break
        c: dict = {"name": name}
        orcid = input("    ORCID (optional): ").strip()
        if orcid:
            c["orcid"] = orcid
        affil = input("    Affiliation (optional): ").strip()
        if affil:
            c["affiliation"] = affil
        creators.append(c)
    return creators


def _collect_contributors() -> list[dict]:
    contributors = []
    print("\nContributors (non-author roles — editor, supervisor…)")
    while True:
        add = input("  Add a contributor? [y/N] ").strip().lower()
        if add not in ("y", "yes"):
            break
        name = input("    Name (Family, Given): ").strip()
        if not name:
            break
        c: dict = {"name": name}
        orcid = input("    ORCID (optional): ").strip()
        if orcid:
            c["orcid"] = orcid
        affil = input("    Affiliation (optional): ").strip()
        if affil:
            c["affiliation"] = affil
        role = choose("    Role", CONTRIBUTOR_TYPES, "Researcher")
        c["type"] = role
        contributors.append(c)
    return contributors


def _collect_related_identifiers(prefilled: list[dict] | None = None) -> list[dict]:
    related: list[dict] = list(prefilled or [])
    print("\nRelated identifiers (prior versions, companion repos, cited works…)")
    if related:
        print(f"  Auto-extracted {len(related)} identifier(s):")
        for r in related:
            print(f"    [{r['relation']}]  {r['identifier']}  ({r['scheme']})")
    while True:
        add = input("  Add another related identifier? [y/N] ").strip().lower()
        if add not in ("y", "yes"):
            break
        identifier = input("    Identifier (DOI / URL / arXiv ID): ").strip()
        if not identifier:
            break
        scheme = choose("    Scheme", IDENTIFIER_SCHEMES, "doi")
        relation = choose("    Relation", RELATION_TYPES, "isVersionOf")
        related.append({"identifier": identifier, "scheme": scheme, "relation": relation})
    return related


def _collect_keywords(defaults: list[str]) -> list[str]:
    default_str = ", ".join(defaults)
    print(f"\nKeywords (detected: {default_str})")
    raw = input("  Press Enter to accept, or enter comma-separated list: ").strip()
    if not raw:
        return list(defaults)
    return [k.strip() for k in raw.split(",") if k.strip()]


# ── Metadata assembly ─────────────────────────────────────────────────────────

def collect_metadata(files: list[Path], extracted: dict, yes: bool) -> dict:
    """
    Build Zenodo metadata.  With --yes, use extracted values + defaults with no
    interactive prompts.  Without --yes, pre-fill prompts with extracted values.
    """
    assembled = _assemble_deposit_meta(extracted, files)
    default_title   = assembled.get("title", "")
    default_desc    = assembled.get("description", "")
    default_date    = assembled.get("publication_date", datetime.date.today().isoformat())
    default_kws     = assembled.get("keywords", list(DEFAULT_KEYWORDS))
    default_creators = assembled.get("creators", [DEFAULT_CREATOR.copy()])

    if yes:
        if not default_title:
            sys.exit("Could not auto-detect title — re-run without -y to enter it manually.")
        if not default_desc:
            sys.exit("Could not auto-detect description — re-run without -y to enter it manually.")
        print(f"  Title:    {default_title}")
        print(f"  Date:     {default_date}")
        print(f"  Creator:  {'; '.join(c['name'] for c in default_creators)}")
        print(f"  Keywords: {', '.join(default_kws)}")
        if assembled.get("custom", {}).get("code:codeRepository"):
            print(f"  Repository: {assembled['custom']['code:codeRepository']}")
        if assembled.get("related_identifiers"):
            print(f"  Related:  {len(assembled['related_identifiers'])} identifiers")
        if assembled.get("references"):
            print(f"  References: {len(assembled['references'])} entries")
        if assembled.get("method"):
            print(f"  Method:   {textwrap.shorten(assembled['method'], 72)}")
        print(f"  Desc:     {textwrap.shorten(default_desc, 72)}")
        return assembled

    # ── Interactive (pre-filled) ─────────────────────────────────────────────
    print()
    print("─" * 56)
    print("  Metadata  (auto-filled — press Enter to accept each)")
    print("─" * 56)

    title       = prompt("Title",       default=default_title)
    description = prompt("Description", default=default_desc)
    upload_type = choose("Upload type", UPLOAD_TYPES, DEFAULT_UPLOAD_TYPE)
    subtype     = None
    if upload_type == "publication":
        subtype = choose("Publication subtype", PUB_SUBTYPES, DEFAULT_PUB_SUBTYPE)

    pub_date = prompt("Publication date", default=default_date)
    version  = prompt("Version", default="1.0", required=False)
    language = prompt("Language (ISO 639-2)", default=DEFAULT_LANGUAGE)

    creators     = _collect_creators(default_creators)
    contributors = _collect_contributors()
    keywords     = _collect_keywords(default_kws)
    notes        = prompt("Notes (optional)", default="", required=False)
    related      = _collect_related_identifiers(extracted.get("related_identifiers"))

    print("\nZenodo communities (optional)")
    communities: list[dict] = []
    raw_comm = input("  Community IDs, comma-separated (or Enter to skip): ").strip()
    if raw_comm:
        communities = [{"identifier": c.strip()} for c in raw_comm.split(",") if c.strip()]

    grants: list[dict] = []
    raw_grant = input("\nGrant IDs (OpenAIRE format, or Enter to skip): ").strip()
    if raw_grant:
        grants = [{"id": g.strip()} for g in raw_grant.split(",") if g.strip()]

    meta = dict(assembled)
    meta.update({
        "title":            title,
        "description":      description,
        "upload_type":      upload_type,
        "publication_date": pub_date,
        "creators":         creators,
        "language":         language,
        "keywords":         keywords,
    })
    if subtype:
        meta["publication_type"] = subtype
    if version:
        meta["version"] = version
    if notes:
        meta["notes"] = notes
    elif assembled.get("notes"):
        meta["notes"] = assembled["notes"]
    if contributors:
        meta["contributors"] = contributors
    if related:
        meta["related_identifiers"] = related
    if communities:
        meta["communities"] = communities
    if grants:
        meta["grants"] = grants
    return meta


def confirm_summary(files: list[Path], meta: dict, mode: str, yes: bool) -> bool:
    print()
    print("─" * 56)
    print("  Summary")
    print("─" * 56)
    print(f"  Mode:        {'PRODUCTION (zenodo.org)' if mode == 'live' else 'SANDBOX (sandbox.zenodo.org)'}")
    print(f"  Title:       {meta['title']}")
    type_str = meta['upload_type']
    if "publication_type" in meta:
        type_str += f" / {meta['publication_type']}"
    print(f"  Type:        {type_str}")
    print(f"  Date:        {meta.get('publication_date', '—')}"
          + (f"  v{meta['version']}" if meta.get("version") else ""))
    print(f"  Language:    {meta.get('language', '—')}")
    print(f"  Creator(s):  " + "; ".join(c["name"] for c in meta["creators"]))
    if meta.get("contributors"):
        print(f"  Contributor(s): " + "; ".join(
            f"{c['name']} ({c.get('type','')})" for c in meta["contributors"]))
    print(f"  License:     {meta['license']} (LUNLICENSE)")
    print(f"  Publisher:   {meta.get('imprint_publisher', '—')}")
    if meta.get("method"):
        print(f"  Method:      {textwrap.shorten(meta['method'], 60)}")
    if meta.get("custom", {}).get("code:codeRepository"):
        print(f"  Repository:  {meta['custom']['code:codeRepository']}")
    langs = meta.get("custom", {}).get("code:programmingLanguage", [])
    if langs:
        print(f"  Languages:   {', '.join(l['title']['en'] for l in langs)}")
    print(f"  Keywords:    {', '.join(meta.get('keywords', []))}")
    if meta.get("notes"):
        print(f"  Notes:       {textwrap.shorten(meta['notes'], 60)}")
    if meta.get("references"):
        print(f"  References:  {len(meta['references'])} entries")
    if meta.get("related_identifiers"):
        print(f"  Related ({len(meta['related_identifiers'])}):")
        for r in meta["related_identifiers"]:
            print(f"    [{r['relation']}]  {r['identifier']}  ({r['scheme']})")
    if meta.get("communities"):
        print(f"  Communities: " + ", ".join(c["identifier"] for c in meta["communities"]))
    if meta.get("grants"):
        print(f"  Grants:      " + ", ".join(g["id"] for g in meta["grants"]))
    print(f"  Description: {textwrap.shorten(meta['description'], 72)}")
    print(f"  Files:")
    for f in files:
        print(f"    {f.name}  ({f.stat().st_size/1024:.0f} KB)")
    print()
    if yes:
        return True
    ans = input("Looks good? [Y/n] ").strip().lower()
    return ans in ("", "y", "yes")


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_upload(args):
    mode = "live" if args.live else "sandbox"
    base = BASE[mode]
    site = SITE[mode]

    files = [Path(f) for f in args.files]
    for f in files:
        if not f.exists():
            sys.exit(f"File not found: {f}")

    # Auto-extract metadata from source files
    print("\nAuto-extracting metadata ...")
    extracted = auto_extract(files)

    token = get_token(args.live)
    session = make_session(token)

    meta = collect_metadata(files, extracted, yes=args.yes)

    if not confirm_summary(files, meta, mode, yes=args.yes):
        print("Aborted.")
        return

    # Create or fetch deposition
    if args.new_version:
        print(f"\nCreating new version of record {args.new_version} ...")
        dep = api_new_version(session, base, args.new_version)
        dep_id     = dep["id"]
        bucket_url = dep["links"]["bucket"]
        print(f"  New version draft ID: {dep_id}")
        # Delete all existing files so only the new upload remains
        existing_files = dep.get("files", [])
        if existing_files:
            print(f"  Removing {len(existing_files)} old file(s) ...")
            for ef in existing_files:
                dr = session.delete(f"{base}/deposit/depositions/{dep_id}/files/{ef['id']}")
                if dr.status_code not in (200, 204):
                    print(f"  Warning: could not delete {ef.get('filename', ef['id'])}: {dr.status_code}")
    elif args.update:
        print(f"\nFetching existing deposit {args.update} ...")
        dep = api_get(session, base, args.update)
        dep_id     = dep["id"]
        bucket_url = dep["links"]["bucket"]
        print(f"  Found: '{dep.get('metadata', {}).get('title', '(untitled)')}' — state: {dep['state']}")
        existing_files = dep.get("files", [])
        if existing_files:
            print(f"  Removing {len(existing_files)} old file(s) ...")
            for ef in existing_files:
                dr = session.delete(f"{base}/deposit/depositions/{dep_id}/files/{ef['id']}")
                if dr.status_code not in (200, 204):
                    print(f"  Warning: could not delete {ef.get('filename', ef['id'])}: {dr.status_code}")
    else:
        print(f"\nCreating new deposit on {site} ...")
        dep = api_create(session, base)
        dep_id     = dep["id"]
        bucket_url = dep["links"]["bucket"]
        print(f"  Deposit ID: {dep_id}")

    print(f"\nUploading {len(files)} file(s):")
    for f in files:
        api_upload_file(session, bucket_url, f)

    # Set metadata
    print("\nSaving metadata ...")
    api_set_metadata(session, base, dep_id, meta)

    # Publish or draft
    draft_url = f"{site}/deposit/{dep_id}"
    if args.draft:
        print(f"\n✓ Saved as draft → {draft_url}")
        return

    print("\nPublishing ...")
    result = api_publish(session, base, dep_id)
    doi = result.get("doi", "(pending)")
    url = result.get("links", {}).get("record_html", f"{site}/record/{dep_id}")
    print(f"\n✓ Published!")
    print(f"  DOI:  {doi}")
    print(f"  URL:  {url}")

    if mode == "sandbox":
        print("\n  (sandbox — DOIs are not real; rerun with --live when ready)")


def cmd_list(args):
    mode = "live" if args.live else "sandbox"
    base = BASE[mode]
    site = SITE[mode]

    token = get_token(args.live)
    session = make_session(token)

    print(f"\nDeposits on {site}:")
    print(f"{'ID':<12} {'State':<12} {'DOI':<22} Title")
    print("─" * 72)
    for d in api_list(session, base):
        m     = d.get("metadata", {})
        doi   = d.get("doi") or d.get("doi_url") or "—"
        state = d.get("state", "?")
        title = m.get("title", "(no title)")[:35]
        print(f"{d['id']:<12} {state:<12} {doi:<22} {title}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Upload Imscribing Grammar publications to Zenodo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              python3 zenodo_upload.py manuscripts/UNIOPENPROB.pdf
              python3 zenodo_upload.py -y --live manuscripts/UNIOPENPROB.pdf
              python3 zenodo_upload.py --live --draft paper.pdf
              python3 zenodo_upload.py --list
              python3 zenodo_upload.py --list --live
              python3 zenodo_upload.py --update 12345 new_version.pdf
              python3 zenodo_upload.py --live -y --new-version 20608723 paper.pdf
        """),
    )
    p.add_argument("files",    nargs="*", help="Files to upload")
    p.add_argument("--live",   action="store_true",
                   help="Publish to zenodo.org (default: sandbox)")
    p.add_argument("--draft",  action="store_true",
                   help="Save as draft instead of publishing immediately")
    p.add_argument("--update", type=int, metavar="ID",
                   help="Add files to an existing deposit (by Zenodo ID)")
    p.add_argument("--new-version", type=int, metavar="ID", dest="new_version",
                   help="Create a new version of a published record (by Zenodo ID)")
    p.add_argument("--list",   action="store_true",
                   help="List your existing deposits and exit")
    p.add_argument("-y", "--yes", action="store_true",
                   help="Skip all prompts — use auto-extracted metadata only")

    args = p.parse_args()

    if args.list:
        cmd_list(args)
        return

    if not args.files and not args.update and not args.new_version:
        p.print_help()
        sys.exit(0)

    if args.live and not args.yes:
        print()
        print("  *** PRODUCTION MODE — this will publish to zenodo.org ***")
        ans = input("  Continue? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            print("Aborted.")
            return

    cmd_upload(args)


if __name__ == "__main__":
    main()
