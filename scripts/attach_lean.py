#!/usr/bin/env python3
"""Attach the relevant Lean source to each published Zenodo manuscript.

For every Erdős-batch deposit, this mints a new version that keeps the existing
PDF and metadata untouched and adds the Lean file the manuscript cites in its
own \\url{.../Imscribing/....lean}. Metadata is never re-derived, so titles and
descriptions are preserved.

  python3 attach_lean.py            # dry run: print the plan, touch nothing
  python3 attach_lean.py --id 22849293 --go   # one deposit, live
  python3 attach_lean.py --go       # the whole batch, live
"""
import os, re, sys, argparse, pathlib, requests

BASE = "https://zenodo.org/api"
MDIR = pathlib.Path(__file__).resolve().parents[2] / "ig-docs/000_MANUSCRIPTS/manuscripts_erdos"
KERN = pathlib.Path(__file__).resolve().parents[2] / "p4rakernel/p4ramill/Imscribing"


def session():
    tok = os.environ.get("ZENODO_TOKEN")
    if not tok:
        sys.exit("ZENODO_TOKEN not set")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {tok}"
    return s


def stem_to_lean():
    m = {}
    for tex in MDIR.glob("*.tex"):
        le = re.findall(r"Imscribing/([A-Za-z0-9_/]+\.lean)", tex.read_text(errors="ignore"))
        if le:
            m[tex.stem] = le[0]
    return m


def build_plan(s):
    s2l = stem_to_lean()
    deps = s.get(f"{BASE}/deposit/depositions", params={"size": 100, "sort": "mostrecent"}).json()
    plan = []
    for d in deps:
        if d.get("state") != "done":
            continue
        files = [f.get("filename", "") for f in d.get("files", [])]
        if any(f.endswith(".lean") or f.endswith("lean.zip") for f in files):
            continue
        for f in files:
            if f.endswith(".pdf"):
                ps = pathlib.Path(f).stem
                if ps in s2l:
                    lp = KERN / s2l[ps]
                    if lp.exists():
                        plan.append((d["id"], ps, s2l[ps], lp))
                    break
    return plan


def attach(s, dep_id, lean_path):
    # 1. new version (copies files + metadata)
    r = s.post(f"{BASE}/deposit/depositions/{dep_id}/actions/newversion")
    r.raise_for_status()
    draft_url = r.json()["links"]["latest_draft"]
    draft = s.get(draft_url).json()
    did = draft["id"]
    bucket = draft["links"]["bucket"]
    # 2. if a same-named lean already there, drop it (idempotent re-runs)
    for ef in draft.get("files", []):
        if ef.get("filename") == lean_path.name:
            s.delete(f"{BASE}/deposit/depositions/{did}/files/{ef['id']}")
    # 3. upload the lean into the copied draft; metadata left as copied
    with open(lean_path, "rb") as fh:
        up = s.put(f"{bucket}/{lean_path.name}", data=fh)
    up.raise_for_status()
    # 4. publish the new version
    pub = s.post(f"{BASE}/deposit/depositions/{did}/actions/publish")
    pub.raise_for_status()
    j = pub.json()
    return j.get("doi", "(pending)"), did


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, help="only this deposit id")
    ap.add_argument("--go", action="store_true", help="actually publish (default: dry run)")
    args = ap.parse_args()
    s = session()
    plan = build_plan(s)
    if args.id:
        plan = [p for p in plan if p[0] == args.id]
    print(f"{'ID':>10}  {'manuscript':30s}  lean")
    for pid, ps, le, _ in plan:
        print(f"{pid:>10}  {ps:30s}  {le}")
    print(f"\n{len(plan)} deposit(s) to update.")
    if not args.go:
        print("dry run — pass --go to publish new versions.")
        return
    for pid, ps, le, lp in plan:
        try:
            doi, did = attach(s, pid, lp)
            print(f"  {pid} -> new version {did}  DOI {doi}  (+{lp.name})")
        except Exception as e:
            print(f"  {pid} FAILED: {e}")


if __name__ == "__main__":
    main()
