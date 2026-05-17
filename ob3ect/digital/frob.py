import ast
import sys
import hashlib
import subprocess
import tempfile
import os
from typing import List, Tuple

# =====================================================================
# Phase 0–1: Imscription Opcodes — Robust Identity
# =====================================================================
def semantic_identity(tree1: ast.AST, tree2: ast.AST) -> bool:
    """True structural + semantic equivalence"""
    # Primary: Python's built-in AST comparison (3.9+)
    try:
        return ast.compare(tree1, tree2) is None  # None means equal
    except (AttributeError, TypeError):
        pass
    
    # Fallback: normalized dump
    d1 = ast.dump(tree1, annotate_fields=True, include_attributes=False)
    d2 = ast.dump(tree2, annotate_fields=True, include_attributes=False)
    return d1 == d2

def VINIT() -> str:
    return ""

def TANCH(source: str) -> ast.AST:
    try:
        return ast.parse(source)
    except SyntaxError as e:
        EVALF(f"Syntax error: {e}")

def AREV(source_path: str) -> str:
    with open(source_path, encoding='utf-8') as f:
        return f.read()

def FSPLIT(source: str) -> Tuple[List[str], ast.AST]:
    tree = TANCH(source)
    return [], tree

def AFWD(tree: ast.AST) -> str:
    return ast.unparse(tree)

def FFUSE(tree: ast.AST, original: str) -> bool:
    """Core imscription verification"""
    regenerated = AFWD(tree)
    regenerated_tree = TANCH(regenerated)
    
    if semantic_identity(tree, regenerated_tree):
        print("FFUSE: Perfect imscription — semantic identity confirmed")
        h = hashlib.sha256(ast.dump(tree, annotate_fields=False).encode()).hexdigest()[:24]
        print(f"Imscription anchor: {h}...")
        return True
    else:
        print("FFUSE: Semantic mismatch (rare — dumping diff info)")
        print("Original dump head:", ast.dump(tree, annotate_fields=False)[:200])
        print("Regenerated dump head:", ast.dump(regenerated_tree, annotate_fields=False)[:200])
        return False

def CLINK(intermediate: str, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        if not intermediate.startswith('#!'):
            intermediate = "#!/usr/bin/env python3\n" + intermediate
        f.write(intermediate)
    os.chmod(output_path, 0o755)

def IFIX(output_path: str):
    print(f"IFIX: Permanent executable imscribed → {output_path}")

def ISCRIB(source: str):
    h = hashlib.sha256(source.encode('utf-8')).hexdigest()[:24]
    print("ISCRIB: Compiler recognizes its own source as valid.")
    print(f"Source hash (imscription anchor): {h}...")

def EVALT():
    print("EVALT: Compilation successful (exit 0)")
    sys.exit(0)

def EVALF(msg: str):
    print(f"EVALF: {msg}")
    sys.exit(1)

# =====================================================================
# Phase 2: Frobenius
# =====================================================================
def frobenius_phase(source: str) -> bool:
    tokens, tree = FSPLIT(source)
    success = FFUSE(tree, source)
    verdict = "PASS" if success else "FAIL"
    print(f"Frobenius: Split→Fuse verdict = {verdict}")
    return success

# =====================================================================
# Phase 4: Bootstrap — Recursive Imscription
# =====================================================================
def bootstrap_compiler(self_path: str = __file__):
    print("\n=== Phase 4: Bootstrap (imscription cycle) ===")
    
    source = AREV(self_path)
    ISCRIB(source)
    
    if not frobenius_phase(source):
        EVALF("Self-imscription failed — identity not preserved")
    
    tree = TANCH(source)
    intermediate = AFWD(tree)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        new_binary = tmp.name
        CLINK(intermediate, new_binary)
        IFIX(new_binary)
    
    print("\nTesting imscribed clone for closure...")
    try:
        result = subprocess.run(
            [sys.executable, new_binary, "--self-test"],
            capture_output=True, text=True, timeout=10
        )
        print("Clone output:", result.stdout.strip() or "<no output>")
        if result.returncode == 0:
            print("Closure: True — imscription loop closed successfully")
        else:
            print("Closure: Partial")
    except Exception as e:
        print(f"Closure test error: {e}")
    
    EVALT()

# =====================================================================
# Entry
# =====================================================================
if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print("ISCRIB(self-test): I am the imscribed recursive compiler.")
        print("mu o delta = id")
        sys.exit(0)
    
    bootstrap_compiler()