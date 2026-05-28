#!/usr/bin/env python3
"""
zenodo_upload.py — Zenodo uploader for Imscribing Grammar publications.

Quick start:
  python3 zenodo_upload.py paper.pdf               # sandbox draft (safe to test)
  python3 zenodo_upload.py --live paper.pdf        # publish to zenodo.org
  python3 zenodo_upload.py --list                  # see all your deposits
  python3 zenodo_upload.py --update 12345 new.pdf  # add file to existing deposit

Token setup (one-time):
  export ZENODO_SANDBOX_TOKEN=...   # from sandbox.zenodo.org/account/settings/applications
  export ZENODO_TOKEN=...           # from zenodo.org/account/settings/applications
  (both need scopes: deposit:write  deposit:actions)
"""

import os
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
    "name":  "Mills, Lando",
    "orcid": "0000-0003-0003-0552",
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

# All IG publications use the Unlicense; cc-zero is the closest Zenodo license.
DEFAULT_LICENSE     = "cc-zero"
DEFAULT_UPLOAD_TYPE = "publication"
DEFAULT_PUB_SUBTYPE = "preprint"
DEFAULT_ACCESS      = "open"


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
    # File uploads don't use JSON Content-Type
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


def collect_metadata(files: list[Path]) -> dict:
    """Interactive metadata collection with sensible defaults."""
    print()
    print("─" * 56)
    print("  Metadata")
    print("─" * 56)

    # Title: guess from first file if possible
    default_title = files[0].stem.replace("_", " ").replace("-", " ").title() if files else ""
    title = prompt("Title", default=default_title)

    description = prompt("Description (1–3 sentences)")

    upload_type = choose("Upload type", UPLOAD_TYPES, DEFAULT_UPLOAD_TYPE)

    subtype = None
    if upload_type == "publication":
        subtype = choose("Publication subtype", PUB_SUBTYPES, DEFAULT_PUB_SUBTYPE)

    # Creator — default is Mills, Lando; allow override or extra authors
    print(f"\nCreator (default: {DEFAULT_CREATOR['name']}, ORCID {DEFAULT_CREATOR['orcid']})")
    override = input("  Press Enter to use default, or type 'Family, Given' to change: ").strip()
    if override:
        creators = [{"name": override}]
    else:
        creators = [DEFAULT_CREATOR.copy()]

    access = DEFAULT_ACCESS  # always open for IG publications

    meta = {
        "title":        title,
        "description":  description,
        "upload_type":  upload_type,
        "creators":     creators,
        "access_right": access,
        "license":      DEFAULT_LICENSE,
    }
    if subtype:
        meta["publication_type"] = subtype

    return meta


def confirm_summary(files: list[Path], meta: dict, mode: str) -> bool:
    print()
    print("─" * 56)
    print("  Summary")
    print("─" * 56)
    print(f"  Mode:        {'PRODUCTION (zenodo.org)' if mode == 'live' else 'SANDBOX (sandbox.zenodo.org)'}")
    print(f"  Title:       {meta['title']}")
    print(f"  Type:        {meta['upload_type']}" +
          (f" / {meta.get('publication_type', '')}" if "publication_type" in meta else ""))
    print(f"  Creator:     {meta['creators'][0]['name']}")
    print(f"  License:     {meta['license']}")
    print(f"  Description: {textwrap.shorten(meta['description'], 60)}")
    print(f"  Files:")
    for f in files:
        print(f"    {f.name}  ({f.stat().st_size/1024:.0f} KB)")
    print()
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

    token = get_token(args.live)
    session = make_session(token)

    # Collect metadata interactively
    meta = collect_metadata(files)

    if not confirm_summary(files, meta, mode):
        print("Aborted.")
        return

    # Create or fetch deposition
    if args.update:
        print(f"\nFetching existing deposit {args.update} ...")
        dep = api_get(session, base, args.update)
        dep_id    = dep["id"]
        bucket_url = dep["links"]["bucket"]
        print(f"  Found: '{dep.get('metadata', {}).get('title', '(untitled)')}' — state: {dep['state']}")
    else:
        print(f"\nCreating new deposit on {site} ...")
        dep = api_create(session, base)
        dep_id     = dep["id"]
        bucket_url = dep["links"]["bucket"]
        print(f"  Deposit ID: {dep_id}")

    # Upload files
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
    doi  = result.get("doi", "(pending)")
    url  = result.get("links", {}).get("record_html", f"{site}/record/{dep_id}")
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
        m   = d.get("metadata", {})
        doi = d.get("doi") or d.get("doi_url") or "—"
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
              python3 zenodo_upload.py manuscripts/AS_ABOVE.pdf
              python3 zenodo_upload.py --live manuscripts/AS_ABOVE.pdf space_search/primitives.py
              python3 zenodo_upload.py --live --draft paper.pdf
              python3 zenodo_upload.py --list
              python3 zenodo_upload.py --list --live
              python3 zenodo_upload.py --update 12345 new_version.pdf
        """),
    )
    p.add_argument("files", nargs="*", help="Files to upload")
    p.add_argument("--live",   action="store_true",
                   help="Publish to zenodo.org (default: sandbox)")
    p.add_argument("--draft",  action="store_true",
                   help="Save as draft instead of publishing immediately")
    p.add_argument("--update", type=int, metavar="ID",
                   help="Add files to an existing deposit (by Zenodo ID)")
    p.add_argument("--list",   action="store_true",
                   help="List your existing deposits and exit")

    args = p.parse_args()

    if args.list:
        cmd_list(args)
        return

    if not args.files and not args.update:
        p.print_help()
        sys.exit(0)

    if args.live:
        print()
        print("  *** PRODUCTION MODE — this will publish to zenodo.org ***")
        ans = input("  Continue? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            print("Aborted.")
            return

    cmd_upload(args)


if __name__ == "__main__":
    main()
