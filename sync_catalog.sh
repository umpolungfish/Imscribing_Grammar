#!/usr/bin/env bash
# sync_catalog.sh — enforce a single unified IG catalog across the ig ecosystem.
#
# Canonical source of truth:
#     imscribing_grammar/IG_catalog.json   (the file the grammar tooling writes)
#
# Every other IG_catalog.json in the tree is a CONSUMER and must be a byte-identical
# real copy of the canonical (real copies, not symlinks, so each deployable repo —
# imscribe.com, ig-docs-public, mOMonadOS — builds standalone; imscribe.com's
# Dockerfile does `COPY IG_catalog.json`, which a symlink would break).
#
# Usage:
#     ./sync_catalog.sh          # propagate canonical to every consumer
#     ./sync_catalog.sh --check  # report drift only; exit 1 if any consumer diverges
#
# Re-run (without --check) after any update to the canonical catalog.

set -euo pipefail

ROOT="/home/mrnob0dy666/imsgct"
SRC="$ROOT/imscribing_grammar/IG_catalog.json"
MODE="${1:-sync}"

[ -f "$SRC" ] || { echo "FATAL: canonical catalog missing: $SRC" >&2; exit 2; }
SRC_HASH="$(md5sum "$SRC" | cut -d' ' -f1)"
SRC_N="$(python3 -c "import json;print(len(json.load(open('$SRC'))))")"
echo "canonical: $SRC"
echo "           $SRC_N entries, md5 ${SRC_HASH:0:8}"
echo

# Discover every consumer catalog in the tree (exclude venvs, node_modules, git internals).
mapfile -t TARGETS < <(find "$ROOT" -name IG_catalog.json \
    -not -path '*/.venv/*' -not -path '*/node_modules/*' -not -path '*/.git/*' \
    | sort)

drift=0
synced=0
ok=0
for t in "${TARGETS[@]}"; do
    [ "$t" = "$SRC" ] && continue           # skip the canonical itself
    label="${t#$ROOT/}"

    kind="real"; [ -L "$t" ] && kind="symlink"
    thash=""; [ -e "$t" ] && thash="$(md5sum "$t" | cut -d' ' -f1)"

    if [ "$kind" = "real" ] && [ "$thash" = "$SRC_HASH" ]; then
        ok=$((ok+1))
        continue
    fi

    # divergent: symlink, wrong content, or missing
    reason="content-differs"
    [ "$kind" = "symlink" ] && reason="is-symlink"
    [ -z "$thash" ] && reason="missing"

    if [ "$MODE" = "--check" ]; then
        echo "DRIFT [$reason] $label"
        drift=1
    else
        rm -f "$t"                          # drop symlink/old file WITHOUT following it
        cp "$SRC" "$t"                       # write a fresh real copy
        echo "synced [$reason -> real copy] $label"
        synced=$((synced+1))
    fi
done

echo
if [ "$MODE" = "--check" ]; then
    if [ "$drift" -eq 0 ]; then
        echo "OK: all $ok consumers match the canonical catalog."
        exit 0
    fi
    echo "DRIFT DETECTED. Run ./sync_catalog.sh to unify."
    exit 1
fi
echo "done: $synced synced, $ok already current."
