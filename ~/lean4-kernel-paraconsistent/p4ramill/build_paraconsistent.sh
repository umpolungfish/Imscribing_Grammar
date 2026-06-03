#!/usr/bin/env bash
#=============================================================================
# build_paraconsistent.sh — Build MillenniumAnkh with Paraconsistent Kernel
#=============================================================================
# This script uses the paraconsistent Lean 4 fork's lake binary to build
# the full MillenniumAnkh formalization. The kernel has False.rec blocked
# at the C++ level, enabling Belnap-B dialetheic reasoning.
#
# Usage: ./build_paraconsistent.sh [target]
#   target: "all" (default), "Imscribing", "ParaconsistentMillennium",
#           "ParaconsistentKernelTest", "clean"
#
# Author: Lando ⊗ ⊙perator
#=============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FORK_DIR="$(dirname "$SCRIPT_DIR")"
LAKE_BIN="${FORK_DIR}/build/stage1/bin/lake"
LEAN_BIN="${FORK_DIR}/build/stage1/bin/lean"

# Banner
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  p4rakernel — Paraconsistent MillenniumAnkh Build            ║"
echo "║  Kernel: lean4-kernel-paraconsistent (False.rec blocked)    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Validate fork binaries
if [ ! -f "$LAKE_BIN" ]; then
    echo "ERROR: Paraconsistent lake binary not found at:"
    echo "  $LAKE_BIN"
    echo ""
    echo "Build the fork first:"
    echo "  cd $FORK_DIR && mkdir -p build && cd build"
    echo "  cmake .. -DCMAKE_BUILD_TYPE=Release"
    echo "  make stage0 -j\$(nproc)"
    echo "  make stage1 -j\$(nproc)"
    exit 1
fi

cd "$SCRIPT_DIR"

export PATH="${FORK_DIR}/build/stage1/bin:$PATH"

TARGET="${1:-all}"

echo "  Target:      $TARGET"
echo "  Lake:        $LAKE_BIN"
echo "  Lean:        $LEAN_BIN"
echo "  Project dir: $SCRIPT_DIR"
echo ""

case "$TARGET" in
    all)
        echo ">>> Building all targets..."
        "$LAKE_BIN" build
        echo ""
        echo ">>> Running ParaconsistentMillennium..."
        "$LEAN_BIN" --run ParaconsistentMillennium.lean
        ;;
    Imscribing)
        echo ">>> Building Imscribing library..."
        "$LAKE_BIN" build Imscribing
        ;;
    ParaconsistentMillennium)
        echo ">>> Running ParaconsistentMillennium..."
        "$LEAN_BIN" --run ParaconsistentMillennium.lean
        ;;
    ParaconsistentKernelTest)
        echo ">>> Running ParaconsistentKernelTest..."
        "$LEAN_BIN" --run ParaconsistentKernelTest.lean
        ;;
    clean)
        echo ">>> Cleaning build artifacts..."
        "$LAKE_BIN" clean
        rm -rf .lake/build
        echo "   Clean done."
        ;;
    *)
        echo "Unknown target: $TARGET"
        echo "Usage: ./build_paraconsistent.sh [all|Imscribing|ParaconsistentMillennium|ParaconsistentKernelTest|clean]"
        exit 1
        ;;
esac

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Build complete — μ∘δ = id verified                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
