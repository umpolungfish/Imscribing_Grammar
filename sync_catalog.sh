#!/usr/bin/env bash
# sync_catalog.sh — there is one catalog.
#
# The catalog lives at:
#     imscribing_grammar/IG_catalog.json
#
# Every other IG_catalog.json in the tree is a link to it. Not a copy kept in
# step, a link: one file, queried by everything. A copy can drift, which is why
# this script used to exist to detect drift and repair it; a link cannot, so
# there is nothing to detect and nothing to repair.
#
# Deployment that needs a standalone file resolves the link at build time
# (`cp -L`, `tar -h`, `docker build` with a dereferencing context), which is the
# build's concern and not a reason for a second catalog to exist.
#
# Usage:
#     ./sync_catalog.sh          # point every consumer at the catalog
#     ./sync_catalog.sh --check  # report any consumer that is not the catalog
#
set -euo pipefail

ROOT="/home/mrnob0dy666/imsgct"
SRC="$ROOT/imscribing_grammar/IG_catalog.json"
MODE="${1:-sync}"

[ -f "$SRC" ] || { echo "FATAL: the catalog is missing: $SRC" >&2; exit 2; }
SRC_N="$(python3 -c "import json;print(len(json.load(open('$SRC'))))")"
echo "catalog: $SRC"
echo "         $SRC_N entries"
echo

# ig-docs-public is a public mirror and is never written here: publishing there
# is the user's decision alone.
mapfile -t TARGETS < <(find "$ROOT" -name IG_catalog.json \
    -not -path '*/.venv/*' -not -path '*/node_modules/*' -not -path '*/.git/*' \
    -not -path '*/ig-docs-public/*' \
    | sort)

drift=0
linked=0
ok=0
for t in "${TARGETS[@]}"; do
    [ "$t" = "$SRC" ] && continue
    label="${t#$ROOT/}"

    if [ -L "$t" ] && [ "$(readlink -f "$t")" = "$SRC" ]; then
        ok=$((ok+1))
        continue
    fi

    reason="separate-copy"
    [ -e "$t" ] || reason="missing"

    if [ "$MODE" = "--check" ]; then
        echo "NOT THE CATALOG [$reason] $label"
        drift=1
    else
        rel="$(python3 -c "import os,sys;print(os.path.relpath(sys.argv[1], os.path.dirname(sys.argv[2])))" "$SRC" "$t")"
        rm -f "$t"
        ln -s "$rel" "$t"
        echo "linked [$reason -> the catalog] $label"
        linked=$((linked+1))
    fi
done

echo
if [ "$MODE" = "--check" ]; then
    if [ "$drift" -eq 0 ]; then
        echo "OK: all $ok consumers are the catalog."
        exit 0
    fi
    echo "A SECOND CATALOG EXISTS. Run ./sync_catalog.sh to make it a link."
    exit 1
fi
echo "done: $linked linked, $ok already the catalog."
