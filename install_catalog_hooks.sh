#!/usr/bin/env bash
# install_catalog_hooks.sh — install git pre-commit guards that keep the unified
# IG catalog from drifting. Idempotent; re-run any time.
#
#   Canonical repo (imscribing_grammar): when IG_catalog.json is committed, it
#   auto-propagates to every consumer via sync_catalog.sh.
#
#   Consumer repos: a commit is BLOCKED if any IG_catalog.json in the tree has
#   drifted from the canonical (sync_catalog.sh --check). Skipped gracefully in a
#   standalone clone where the canonical isn't present.

set -euo pipefail

ROOT="/home/mrnob0dy666/imsgct"
SYNC="$ROOT/imscribing_grammar/sync_catalog.sh"
CANON_REPO="$ROOT/imscribing_grammar"
CONSUMER_REPOS=(
    "$ROOT/imscribe.com"
    "$ROOT/mOMonadOS"
    "$ROOT/ig-docs-public"
    "$ROOT/red-hot_rebis"
    "$ROOT/Voynich_Phytoglyphica"
    "$ROOT/Ars_Phytoglyphica"
)

MARK="# >>> ig-catalog-guard >>>"

install_hook() {
    local repo="$1" body="$2"
    local hook="$repo/.git/hooks/pre-commit"
    [ -d "$repo/.git" ] || { echo "skip (no .git): ${repo#$ROOT/}"; return; }
    if [ -f "$hook" ] && ! grep -qF "$MARK" "$hook"; then
        # An unrelated pre-commit already exists — append our guard, don't clobber.
        printf '\n%s\n%s\n' "$MARK" "$body" >> "$hook"
    else
        printf '#!/usr/bin/env bash\n%s\n%s\n' "$MARK" "$body" > "$hook"
    fi
    chmod +x "$hook"
    echo "installed: ${repo#$ROOT/}/.git/hooks/pre-commit"
}

# Canonical: auto-propagate on catalog change.
install_hook "$CANON_REPO" \
'if git diff --cached --name-only | grep -qx "IG_catalog.json"; then
    echo "[catalog] canonical changed -> propagating to consumers"
    "'"$SYNC"'" || { echo "[catalog] sync failed"; exit 1; }
    echo "[catalog] consumers updated; commit those repos to persist"
fi'

# Consumers: block on drift.
for repo in "${CONSUMER_REPOS[@]}"; do
    install_hook "$repo" \
'if [ -x "'"$SYNC"'" ]; then
    "'"$SYNC"'" --check || {
        echo "[catalog] DRIFT: run '"$SYNC"' to unify before committing" >&2
        exit 1
    }
fi'
done

echo
echo "done. Guard active. Test with: $SYNC --check"
