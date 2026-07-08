#!/usr/bin/env python3
"""One-shot hand-filled Zenodo upload for manuscripts3 SIC trio."""

import json
import os
import sys
from pathlib import Path

import requests

BASE = "https://zenodo.org/api"
SITE = "https://zenodo.org"
ROOT = Path(__file__).resolve().parents[2] / "ig-docs_lifted" / "manuscripts3"

CREATOR = {
    "name": "Mills, Lando",
    "orcid": "0000-0003-0003-0552",
    "affiliation": "Independent Researcher",
}
CONTRIBUTOR_LARSON = {"name": "Larson, Harry T.", "type": "Other"}
COMMON = {
    "upload_type": "publication",
    "publication_type": "preprint",
    "publication_date": "2026-07-07",
    "creators": [CREATOR],
    "contributors": [CONTRIBUTOR_LARSON],
    "access_right": "open",
    "license": "other-open",
    "language": "eng",
    "version": "1.0",
    "imprint_publisher": "umpolungfish",
}

CRYSTALLINE = (
    "Frozen crystalline snapshot: branch crystalline/manuscripts3-2026-07-07, "
    "tag crystalline-manuscripts3-v1; p4rakernel commit eea2c0c. "
    "Manuscript trio frozen in ig-docs on the same branch and tag."
)


def rel(url: str, relation: str = "isSupplementedBy") -> dict:
    return {"identifier": url, "scheme": "url", "relation": relation}


def lean_lang() -> dict:
    return {"id": "lean", "title": {"en": "Lean"}}


def rust_lang() -> dict:
    return {"id": "rust", "title": {"en": "Rust"}}


DEPOSITS = [
    {
        "pdf": "sic_povm_stark_hilbert12_lifted.pdf",
        "metadata": {
            **COMMON,
            "title": (
                "SIC-POVMs, a Stark Conjecture, and the 12th: "
                "A Formalization via Paraconsistent Belnap Multilattices"
            ),
            "description": (
                "This paper establishes, inside the Lean 4 proof assistant, a three-level formal "
                "identification. The levels are: (i) Belnap multilattice axioms for "
                "Weyl–Heisenberg covariant SIC-POVMs at $d=2^n$; (ii) the Zauner conjecture; and "
                "(iii) the mixed-signature Stark conjecture for the ray class field "
                "$K_d=\\mathbb{Q}(\\sqrt{(d-3)(d+1)})$, a real-quadratic case of Hilbert's "
                "Twelfth Problem. Fiducials are unit-normalized and satisfy "
                "$(d+1)|\\langle\\psi,D_{a,b}\\psi\\rangle|^2=1$.\n\n"
                "The equivalence hilbert_embedding_equiv_zauner is proved by rfl: the Belnap "
                "embedding into $\\mathbb{C}^{2^n}$ and the Zauner conjecture at $d=2^n$ are "
                "definitionally the same proposition. The Belnap skeleton (orbit size $4^n$, "
                "Frobenius closure $\\mu\\circ\\delta=\\mathrm{id}$, join-equiangularity, Born rule) "
                "contains zero sorries. Open arithmetic content is marked by named gap axioms for "
                "Stark units on WH frames; a proof of Stark would close all three levels at once.\n\n"
                "For dimension $d=12$ we prove SICPOVM_Exists 12 outright. We construct an exact "
                "fiducial in a finitely presented $\\mathbb{Q}$-algebra, verify 143 overlap "
                "identities with native_decide, and transfer everything to $\\mathbb{C}^{12}$ along "
                "a ring homomorphism. The theorem crystal_forces_d12_sic depends on no axiom beyond "
                "Lean 4's standard foundations and compiler trust. This is, to our knowledge, the "
                "first machine-checked SIC-POVM existence in any dimension.\n\n"
                "For the frontier dimension $d=2048=2^{11}$ the transport apparatus is formalized "
                "and sorry-free. It includes a forward map "
                "$\\varphi\\colon B^{\\oplus 11}\\to\\mathbb{C}^{2048}$, a reduction $\\psi$ with "
                "$\\psi\\circ\\varphi=\\mathrm{id}$, a conditional reduction to Stark, and a non-real "
                "character obstruction that blocks the false branch. Unconditional existence remains "
                "open; the machinery that surrounds it is closed."
            ),
            "keywords": [
                "SIC-POVM",
                "Belnap multilattice",
                "Stark conjecture",
                "Hilbert's Twelfth Problem",
                "Zauner conjecture",
                "Lean 4",
                "paraconsistent logic",
                "Weyl-Heisenberg group",
                "ray class fields",
                "machine-checked proof",
                "Imscribing Grammar",
                "imscription",
            ],
            "method": (
                "Lean 4 machine-checked formalization of SIC-POVM existence, Belnap multilattice "
                "structure, and the Stark–Zauner–Hilbert identification chain."
            ),
            "notes": (
                "All cited Lean modules live in the p4ramill library of p4rakernel "
                "(https://github.com/umpolungfish/p4rakernel). "
                + CRYSTALLINE
                + " Companion preprints: witness_vessel, chrysopoeia_2048. "
                "Acknowledgements: The author thanks Harry T. Larson for imparting the importance "
                "of catching rising problems and never letting them go. The present formalization "
                "is written in that spirit: the Stark–Zauner–Hilbert identification was not "
                "abandoned at the honest gap markers, and dimension d=12 was carried from arithmetic "
                "prediction to a machine-checked existence theorem rather than left as a "
                "conjectural witness. Programming languages: Lean 4. Publisher: umpolungfish. "
                "License: LUNLICENSE (other-open on Zenodo)."
            ),
            "custom": {
                "code:codeRepository": "https://github.com/umpolungfish/p4rakernel",
                "code:programmingLanguage": [lean_lang()],
            },
            "related_identifiers": [
                rel("https://github.com/umpolungfish/p4rakernel"),
                rel("https://github.com/umpolungfish/ig-docs"),
                rel("https://github.com/umpolungfish/imscribing_grammar"),
                rel("https://github.com/umpolungfish"),
                rel("https://orcid.org/0000-0003-0003-0552", "isAlternateIdentifier"),
                rel("https://landomills.com/", "isAlternateIdentifier"),
                rel("https://imscribe.com/", "isAlternateIdentifier"),
            ],
            "references": [
                "D. M. Appleby, H. Yadsan-Appleby, and G. Zauner, Galois automorphisms of a symmetric measurement, Quantum Inf. Comput. 13 (2013), 672–720.",
                "M. Appleby, S. Flammia, G. McConnell, and J. Yard, SICs and algebraic number theory, Found. Phys. 47 (2017), 1042–1059.",
                "M. Appleby, S. Flammia, G. McConnell, and J. Yard, Generating ray class fields of real quadratic fields via complex equiangular lines, Acta Arith. 192 (2020), 211–233.",
                "N. D. Belnap, A Useful Four-Valued Logic, in: J. M. Dunn and G. Epstein (eds.), Modern Uses of Multiple-Valued Logic, Reidel, Dordrecht, 1977, pp. 5–37.",
                "H. T. Larson, Catch a Rising Problem… and Never Ever Let it Go, IRE Transactions on Engineering Management 8(4) (1961), 173–174.",
                "L. de Moura and S. Ullrich, The Lean 4 Theorem Prover and Programming Language, in: CADE-28, Lecture Notes in Comput. Sci. vol. 12699, Springer, 2021, pp. 625–635.",
                "C. L. Mills, p4rakernel: Lean 4 paraconsistent kernel fork, https://github.com/umpolungfish/p4rakernel, branch crystalline/manuscripts3-2026-07-07, tag crystalline-manuscripts3-v1 (commit eea2c0c), 2026.",
                "H. M. Stark, L-functions at s=1, IV: First-order zeroes at s=1 for Dirichlet L-functions with real characters, Advances in Mathematics 35 (1980), 197–235.",
                "G. Zauner, Quantum designs: Foundations of a noncommutative design theory, PhD thesis, University of Vienna, 1999.",
            ],
        },
    },
    {
        "pdf": "witness_vessel_lifted.pdf",
        "metadata": {
            **COMMON,
            "title": "The Witness Vessel: Lossless Transport on the Dual-Link SIC-POVM",
            "description": (
                "The Lean 4 library p4ramill and the bare-metal OS mOMonadOS carry Clay Witness "
                "verdicts between composition dialects. Earlier cargo-style transports lost "
                "information in a reproducible way: the tensor reading is denied at the "
                "dimensionality–topology pair. Here a Witness rides as the vessel's split/fuse "
                "structure, not inside it, and losslessness is checked on both substrates without "
                "mutual trust.\n\n"
                "In Lean 4, $\\mu\\circ\\delta=\\mathrm{id}$ follows from propext alone; BSD and "
                "Hodge board as T, and Yang–Mills boards as the dialetheia B. witness_vessel_lossless "
                "delivers the transported $d=12$ fiducial still satisfying the SIC conditions, "
                "importing the existence theorem without re-deriving it. On bare metal the same "
                "protocol runs in QEMU over three Witnesses and 88 dialects; the verdict matrix is "
                "unchanged and $\\Delta S=0$. Losslessness means literal equality after read-back."
            ),
            "keywords": [
                "lossless transport",
                "SIC-POVM",
                "Belnap logic",
                "composition dialects",
                "Clay Millennium problems",
                "Lean 4",
                "Frobenius closure",
                "formal verification",
                "bare-metal OS",
                "witness vessel",
                "Imscribing Grammar",
                "imscription",
            ],
            "method": (
                "Lean 4 proof verification of witness-vessel lossless transport, paired with "
                "bare-metal Rust execution in mOMonadOS under QEMU."
            ),
            "notes": (
                "Proof half: SIC_D12_WitnessVessel.lean in p4ramill (p4rakernel). Runtime half: "
                "src/witness_vessel.rs in mOMonadOS. Canonical tuples from IG_catalog.json; "
                "88 dialects from dialect_expansion.rs. No tuple, verdict, or payload is "
                "hand-entered. "
                + CRYSTALLINE
                + " mOMonadOS commit 16da4a9. Companion preprints: sic_povm_stark_hilbert12, "
                "chrysopoeia_2048. Acknowledgements: The author thanks Harry T. Larson for "
                "imparting the importance of catching rising problems and never letting them go. "
                "The lossy cargo reading of transport was such a problem: once the Grammar "
                "localized the malformation at the dimensionality–topology pair, the corrected "
                "protocol was pursued until the round-trip law held on both substrates. "
                "Programming languages: Lean 4, Rust. Publisher: umpolungfish. "
                "License: LUNLICENSE (other-open on Zenodo)."
            ),
            "custom": {
                "code:codeRepository": "https://github.com/umpolungfish/p4rakernel",
                "code:programmingLanguage": [lean_lang(), rust_lang()],
            },
            "related_identifiers": [
                rel("https://github.com/umpolungfish/p4rakernel"),
                rel("https://github.com/umpolungfish/momonad_os"),
                rel("https://github.com/umpolungfish/ig-docs"),
                rel("https://github.com/umpolungfish/imscribing_grammar"),
                rel("https://github.com/umpolungfish"),
                rel("https://orcid.org/0000-0003-0003-0552", "isAlternateIdentifier"),
                rel("https://landomills.com/", "isAlternateIdentifier"),
                rel("https://imscribe.com/", "isAlternateIdentifier"),
            ],
            "references": [
                "N. D. Belnap, A Useful Four-Valued Logic, in: J. M. Dunn and G. Epstein (eds.), Modern Uses of Multiple-Valued Logic, Reidel, Dordrecht, 1977, pp. 5–37.",
                "H. T. Larson, Catch a Rising Problem… and Never Ever Let it Go, IRE Transactions on Engineering Management 8(4) (1961), 173–174.",
                "L. de Moura and S. Ullrich, The Lean 4 Theorem Prover and Programming Language, in: CADE-28, Lecture Notes in Comput. Sci. vol. 12699, Springer, 2021, pp. 625–635.",
                "G. Zauner, Quantum designs: Foundations of a noncommutative design theory, PhD thesis, University of Vienna, 1999.",
                "D. M. Appleby, H. Yadsan-Appleby, and G. Zauner, Galois automorphisms of a symmetric measurement, Quantum Inf. Comput. 13 (2013), 672–720.",
            ],
        },
    },
    {
        "pdf": "chrysopoeia_2048_lifted.pdf",
        "metadata": {
            **COMMON,
            "title": "The 2048 Chrysopoeia: An Explicit Construction Program for the $d=2048$ SIC-POVM Moduli",
            "description": (
                "Companion to the SIC–Stark–12th formalization, this paper lays out an explicit "
                "program for the diagonal moduli $N_k=|\\psi_k|^2$ of the $d=2048$ SIC-POVM. It "
                "reports what direct computation has settled and what remains open. Five results "
                "are in place. The $a=0$ stratum reduces to a flat autocorrelation condition on "
                "the real moduli, a condition verified on $d=12$ to a residual near $10^{-58}$. "
                "Unconstrained numerical recovery is blocked by a genuine local minimum (residual "
                "$3.9\\times 10^{-3}$). The moduli field is the real index-2 subfield, of degree "
                "$2^{27}$, of the ray class field of conductor $(d)\\,\\infty_1\\infty_2$, "
                "calibrated on the $d=12$ fiducial where the moduli have degree 4 or 8 and "
                "generate a field of degree 16; its unramified ascent is verified to degree 128. "
                "Stark-unit $L$-values supply the moduli without building the full field, a method "
                "validated end to end on $d=12$. An integer norm sieve separates degenerate "
                "$S$-unit aliases by discriminant $-m_d$. Still open: the reduced character set "
                "for the 1024 moduli and unconditional existence."
            ),
            "keywords": [
                "SIC-POVM",
                "moduli field",
                "ray class field",
                "Stark units",
                "integer norm sieve",
                "algebraic number theory",
                "Zauner conjecture",
                "PARI/GP",
                "d=2048",
                "Imscribing Grammar",
                "imscription",
            ],
            "method": (
                "Explicit algebraic construction program for the d=2048 SIC-POVM moduli; PARI/GP "
                "field computations with Lean 4 companion formalization."
            ),
            "notes": (
                "Companion formalization and Lean modules live in p4ramill (p4rakernel). "
                + CRYSTALLINE
                + " Companion preprints: sic_povm_stark_hilbert12, witness_vessel. "
                "Acknowledgements: The author thanks Harry T. Larson for imparting the importance "
                "of catching rising problems and never letting them go. The d=2048 moduli program "
                "was undertaken in the same spirit: when unconstrained recovery stalled at a spurious "
                "local minimum, the route through Stark units, the ray class tower, and the integer "
                "norm sieve was not dropped. Programming languages: Lean 4; PARI/GP field scripts. "
                "Publisher: umpolungfish. License: LUNLICENSE (other-open on Zenodo)."
            ),
            "custom": {
                "code:codeRepository": "https://github.com/umpolungfish/p4rakernel",
                "code:programmingLanguage": [lean_lang()],
            },
            "related_identifiers": [
                rel("https://github.com/umpolungfish/p4rakernel"),
                rel("https://github.com/umpolungfish/ig-docs"),
                rel("https://github.com/umpolungfish/imscribing_grammar"),
                rel("https://github.com/umpolungfish"),
                rel("https://orcid.org/0000-0003-0003-0552", "isAlternateIdentifier"),
                rel("https://landomills.com/", "isAlternateIdentifier"),
                rel("https://imscribe.com/", "isAlternateIdentifier"),
            ],
            "references": [
                "G. Zauner, Quantendesigns: Grundzüge einer nichtkommutativen Designtheorie, Ph.D. thesis, Universität Wien, 1999.",
                "D. M. Appleby, H. Yadsan-Appleby, and G. Zauner, Galois automorphisms of a symmetric measurement, Quantum Inf. Comput. 13 (2013), 672–720.",
                "M. Appleby, S. Flammia, G. McConnell, and J. Yard, SICs and algebraic number theory, Found. Phys. 47 (2017), 1042–1059.",
                "M. Appleby, S. Flammia, G. McConnell, and J. Yard, Generating ray class fields of real quadratic fields via complex equiangular lines, Acta Arith. 192 (2020), 211–233.",
                "C. L. Mills, SIC-POVMs, a Stark Conjecture, and the 12th: A Formalization via Paraconsistent Belnap Multilattices, companion manuscript, 2026.",
                "The PARI Group, PARI/GP version 2.13, Univ. Bordeaux, 2021, https://pari.math.u-bordeaux.fr/.",
                "H. T. Larson, Catch a Rising Problem… and Never Ever Let it Go, IRE Transactions on Engineering Management 8(4) (1961), 173–174.",
            ],
        },
    },
]


def upload_one(session: requests.Session, pdf: Path, metadata: dict) -> int:
    dep = session.post(f"{BASE}/deposit/depositions", data="{}").json()
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    with open(pdf, "rb") as fh:
        r = requests.put(
            f"{bucket}/{pdf.name}",
            data=fh,
            headers={"Authorization": session.headers["Authorization"]},
        )
        r.raise_for_status()
    r = session.put(
        f"{BASE}/deposit/depositions/{dep_id}",
        data=json.dumps({"metadata": metadata}),
    )
    r.raise_for_status()
    return dep_id


def main() -> None:
    tok = os.getenv("ZENODO_TOKEN", "").strip()
    if not tok:
        sys.exit("ZENODO_TOKEN not set")
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
    })
    for item in DEPOSITS:
        pdf = ROOT / item["pdf"]
        if not pdf.exists():
            sys.exit(f"Missing {pdf}")
        dep_id = upload_one(session, pdf, item["metadata"])
        print(f"✓ {item['metadata']['title'][:60]}")
        print(f"  Repository: {item['metadata']['custom']['code:codeRepository']}")
        print(f"  Draft → {SITE}/deposit/{dep_id}\n")


if __name__ == "__main__":
    main()