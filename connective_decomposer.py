#!/usr/bin/env python3
"""
Connective Decomposer — Logical Connectives DECOMPOSE into mathematical expressions.

Construction spec (2026-11-14, v0):
  fragment text -> tokenize -> Pratt parse -> expansion walk (defined predicates,
  cycle-recording) -> per-register translation -> render + inscribe-back -> residual.

Registers v0: Set, Order (Heyting), Probability, Analysis.
Check instruments (separate receipts, never promoted across cuts):
  1. return-leg residual (translate -> inscribe -> normalized AST diff)
  2. AREV commutation (per register, on De Morgan pairs)
  3. coverage (parse/expand/translate status over the corpus)

No catalog writes. Expansions marked AUTHORED are decomposer-local v0 entries.
Unknown defined predicates are measured gaps, reported by the scan.
"""

import sys
from dataclasses import dataclass
from typing import Optional

# =============================================================================
# AST
# =============================================================================

@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Const:
    name: str

@dataclass(frozen=True)
class App:
    head: str
    args: tuple

@dataclass(frozen=True)
class Juxt:
    parts: tuple  # juxtaposition product: 2*pi*n, gx

@dataclass(frozen=True)
class Connect:
    op: str
    args: tuple

@dataclass(frozen=True)
class Quant:
    quant: str
    var: str
    guard: Optional[object]
    body: object

@dataclass(frozen=True)
class Binder:
    op: str
    index: Optional[str]
    body: object

@dataclass(frozen=True)
class Sup:
    base: object
    power: str

@dataclass(frozen=True)
class SetLit:
    items: tuple

# =============================================================================
# TOKENIZER
# =============================================================================

NORMALIZE = {"lr\u21d4": "lreqv", "seq!": "seqbang", "non-Herm": "nonHerm",
             "\u27e8\u2192\u27e9": "morphpair"}

CMP_OPS = {"=", "\u2260", "<", ">", "\u2264", "\u2265", "\u2208", "\u2209", "\u2282",
           "\u2286", "\u223c", "\u226b", "\u226a", "\u2194", "\u2192"}
TERM_INFIX = {"+", "\u2212", "-", "*", "\u22c5", "\u2218", "\u2295", "\u22a0", "\u22a3", "\u22a1"}
PREC = {"\u2194": 1, "\u2192": 2, "\u2228": 3, "\u2227": 4}

def tokenize(s: str):
    s = s.strip()
    for dash in ("\u2014", "--"):
        if dash in s:
            s = s.split(dash)[0].strip()
    for k, v in NORMALIZE.items():
        s = s.replace(k, v)
    toks = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "_":
            toks.append(("SUB", "_"))
            i += 1
            k = i
            while k < len(s) and (s[k].isalnum() or s[k] in ("\u2082", "\u2070")):
                k += 1
            toks.append(("ID", s[i:k]))
            i = k
            continue
        m = None
        for op in ["\u21d4", "\u2261", "\u2209", "\u2286", "\u2282", "\u221d", "\u2260",
                   "\u2264", "\u2265", "\u226b", "\u226a", "\u2194", "\u2192", "\u2229",
                   "\u222a", "\u2218", "\u2295", "\u22a0", "\u22a3", "\u22a1"]:
            if s.startswith(op, i):
                m = op
                break
        if m:
            toks.append(("OP", m))
            i += len(m)
            continue
        if s[i] in "\u00ac\u2227\u2228\u2200\u2203\u2208=\u003c\u003e\u223c\u226b\u226a+\u2212-*/\u2202\u2211\u222e\u222b|\u27e8\u27e9":
            toks.append(("OP", s[i]))
            i += 1
            continue
        if s[i] in "()[],{}":
            toks.append(("P", s[i]))
            i += 1
            continue
        if s[i].isalnum() or ord(s[i]) > 127:
            j = i
            while j < len(s) and (s[j].isalnum() or ord(s[j]) > 127) and \
                  s[j] not in "\u00ac\u2227\u2228\u2192\u2194\u2200\u2203\u2208<>=\u2260" and s[j] not in "()[],{}":
                j += 1
            toks.append(("ID", s[i:j]))
            i = j
            continue
        raise SyntaxError(f"tokenizer: unhandled char {s[i]!r} at {i}")
    return toks

# =============================================================================
# PRATT PARSER
# =============================================================================

SINGLE_VARS = set("xyzabcdegpfnhijkmrstuvw")

class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.i = 0

    def peek(self, k=0):
        j = self.i + k
        return self.toks[j] if j < len(self.toks) else (None, None)

    def next(self):
        t = self.peek()
        self.i += 1
        return t

    def expect(self, kind, val=None):
        k, v = self.next()
        if k != kind or (val is not None and v != val):
            raise SyntaxError(f"expected {kind} {val!r}, got {(k, v)!r}")
        return v

    def parse(self):
        e = self.parse_expr(0)
        if self.i < len(self.toks):
            raise SyntaxError(f"trailing tokens: {self.toks[self.i:]}")
        return e

    def parse_expr(self, min_prec):
        left = self.parse_unary(min_prec)
        while True:
            kind, val = self.peek()
            if kind == "OP" and val in PREC and PREC[val] >= min_prec:
                self.next()
                right = self.parse_expr(PREC[val] + 1)
                left = Connect(val, (left, right))
                continue
            if kind == "OP" and val in CMP_OPS and min_prec <= 5:
                self.next()
                right = self.parse_expr(6)
                left = Connect(val, (left, right))
                continue
            if kind == "OP" and val in TERM_INFIX and min_prec <= 6:
                self.next()
                right = self.parse_primary(6)
                dt = Connect(val, (left, right))
                left = dt
                continue
            break
        return left

    def parse_unary(self, min_prec):
        kind, val = self.peek()
        if kind == "OP" and val == "\u00ac":
            self.next()
            body = self.parse_expr(7)
            return Connect("\u00ac", (body,))
        if kind == "OP" and val in ("\u2200", "\u2203"):
            return self.parse_quant(val)
        if kind == "OP" and val in ("\u2211", "\u222e", "\u222b", "\u2202"):
            return self.parse_binder(val)
        if kind == "OP" and val == "\u27e8":
            self.next()
            inner = self.parse_expr(0)
            while True:
                k2, v2 = self.next()
                if k2 == "OP" and v2 == "|":
                    break
                if (k2, v2) == (None, None):
                    raise SyntaxError("unterminated <..|")
            return App("morphpair", (inner,))
        return self.parse_primary(min_prec)

    def parse_quant(self, q):
        self.next()
        kind, var = self.next()
        if kind != "ID":
            raise SyntaxError(f"quantifier var expected, got {(kind, var)!r}")
        guard = None
        kind2, val2 = self.peek()
        if kind2 == "OP" and val2 in ("\u2208", "\u2282", "\u2286"):
            self.next()
            dom = self.parse_primary(7)
            guard = Connect(val2, (Var(var), dom))
        kind3, val3 = self.peek()
        if kind3 == "OP" and val3 in ("\u2200", "\u2203"):
            return Quant(q, var, guard, self.parse_quant(val3))
        self.expect("P", "(")
        body = self.parse_expr(0)
        self.expect("P", ")")
        return Quant(q, var, guard, body)

    def parse_binder(self, op):
        self.next()
        index = None
        kind, val = self.peek()
        if kind == "SUB":
            self.next()
            _, name = self.next()
            index = name
        if op == "\u2202":
            return Binder(op, index, self.parse_primary(7))
        body = self.parse_primary(7)
        while True:
            kind, val = self.peek()
            if kind == "OP" and val == "|":
                body = Juxt((body, self.parse_primary(7)))
                continue
            if kind == "ID":
                body = Juxt((body, self.parse_primary(7)))
                continue
            break
        return Binder(op, index, body)

    def parse_expr(self, min_prec):
        # (kept name for API compat with main parse dispatch above)
        return Parser._expr(self, min_prec)

    def parse_primary(self, min_prec):
        node = self.parse_postfix_atom()
        while True:
            kind, val = self.peek()
            if kind == "OP" and val in TERM_INFIX and min_prec <= 6:
                self.next()
                right = self.parse_primary(6)
                node = Connect(val, (node, right))
                continue
            if kind == "OP" and val == "|":
                node = Juxt((node, self.parse_primary(7)))
                continue
            if kind == "OP" and val in ("\u00ac", "\u2200", "\u2203"):
                break
            break
        return node

    def parse_postfix_atom(self):
        kind, val = self.peek()
        if kind == "ID":
            self.next()
            node = self.id_node(val)
            nxt_k, nxt_v = self.peek()
            if nxt_k == "P" and nxt_v == "(":
                self.next()
                args = []
                if self.peek() != ("P", ")"):
                    while True:
                        args.append(self.parse_expr(0))
                        k, v = self.next()
                        if (k, v) == ("P", ")"):
                            break
                        if not (k == "P" and v == ","):
                            raise SyntaxError(f"expected , or ) got {(k,v)!r}")
                else:
                    self.next()
                return App(val, tuple(args))
            return node
        if kind == "OP" and val == "|":
            self.next()
            inner = self.parse_primary(7)
            k2, v2 = self.next()
            if not (k2 == "OP" and v2 == "|"):
                raise SyntaxError("unterminated |..>")
            return App("ket", (inner,))
        if kind == "OP" and val in ("-", "\u2212"):
            self.next()
            return Connect("-", (self.parse_postfix_atom(),))
        if kind == "P" and val == "(":
            self.next()
            e = self.parse_expr(0)
            self.expect("P", ")")
            return e
        if kind == "ID":
            self.next()
            return self.id_node(val)
        raise SyntaxError(f"atom: unexpected {(kind, val)!r}")

    def id_node(self, name):
        if len(name) == 1:
            return Var(name) if name in SINGLE_VARS else Const(name)
        return App(name, ())

    # parenthesised-expression path used above
    _expr = parse_unary

# -----------------------------------------------------------------------------
# shims: Parser.parse_expr delegates to parse_unary chain
# -----------------------------------------------------------------------------
def _patch_parser():
    Parser.parse_expr_orig = Parser.parse_expr
    def parse_expr(self, min_prec):
        left = self.parse_unary(min_prec)
        while True:
            kind, val = self.peek()
            if kind == "OP" and val in PREC and PREC[val] >= min_prec:
                self.next()
                right = self.parse_expr(PREC[val] + 1)
                left = Connect(val, (left, right))
                continue
            if kind == "OP" and val in CMP_OPS and min_prec <= 5:
                self.next()
                right = self.parse_expr(6)
                left = Connect(val, (left, right))
                continue
            break
        return left
    Parser.parse_expr = parse_expr
_patch_parser()

# =============================================================================
# EXPANSION WALK
# =============================================================================

def walk(e, depth=0):
    max_d = depth
    expanded = []
    cycles = set()
    def go(node, d, path=()):
        nonlocal max_d
        if isinstance(node, App):
            name = node.head
            if name in DEFINED_PREDS and not isinstance(node.args[0], Sup) if node.args else False:
                pass
            if name in DEFINED_PREDS:
                if name in path:
                    cycles.add(name)
                else:
                    expanded.append((name, d))
                    tgt = DEFINED_PREDS[name]
                    if "{x}" in tgt and node.args:
                        tgt = tgt.replace("{x}", str(node.args[0].name)
                                          if isinstance(node.args[0], Var) else str(node.args[0]))
                    new = parse_fragment(tgt)[0]
                    max_d = max(max_d, d + 1)
                    return go(new, d + 1, path + (name,))
            return App(name, tuple(go(a, d, path) for a in node.args))
        if isinstance(node, Juxt):
            return Juxt(tuple(go(p, d, path) for p in node.parts))
        if isinstance(node, Connect):
            return Connect(node.op, tuple(go(a, d, path) for a in node.args))
        if isinstance(node, Quant):
            return Quant(node.quant, node.var,
                         go(node.guard, d, path) if node.guard else None,
                         go(node.body, d, path))
        if isinstance(node, Binder):
            return Binder(node.op, node.index, go(node.body, d, path))
        if isinstance(node, Sup):
            return Sup(go(node.base, d, path), node.power)
        if isinstance(node, SetLit):
            return SetLit(tuple(go(x, d, path) for x in node.items))
        return node
    return go(e, depth), max_d, expanded, cycles

# =============================================================================
# DEFINED PREDICATE EXPANSIONS (AUTHORED, v0 — decomposer-local, connective-defined)
# =============================================================================

DEFINED_PREDS = {
    "fin": "\u00ac\u2203f( Inj(f) \u2227 \u00acSurj(f) )",
    "Inj": "\u2200a\u2200b( f(a) = f(b) \u2192 a = b )",
    "Surj": "\u2200b\u2208codom(f) \u2203a( f(a) = b )",
    "sym": "\u2203g( g \u2260 e \u2227 gx = x )",
    "diverges": "|\u03be| \u2192 \u221e",
}

# =============================================================================
# FRAGMENT PARSING / NORMALIZATION / DIFF
# =============================================================================

def parse_fragment(s: str):
    return Parser(tokenize(s)).parse(), tokenize(s)

def normalize(e):
    if isinstance(e, App):
        return App(e.head, tuple(normalize(a) for a in e.args))
    if isinstance(e, Juxt):
        return Juxt(tuple(normalize(p) for p in e.parts))
    if isinstance(e, Connect):
        if e.op in ("\u2227", "\u2228"):
            flat = []
            for a in e.args:
                na = normalize(a)
                if isinstance(na, Connect) and na.op == e.op:
                    flat.extend(na.args)
                else:
                    flat.append(na)
            return Connect(e.op, tuple(sorted(flat, key=str)))
        return Connect(e.op, tuple(normalize(a) for a in e.args))
    if isinstance(e, Quant):
        return Quant(e.quant, e.var, normalize(e.guard) if e.guard else None, normalize(e.body))
    if isinstance(e, Binder):
        return Binder(e.op, e.index, normalize(e.body))
    if isinstance(e, Sup):
        return Sup(normalize(e.base), e.power)
    if isinstance(e, SetLit):
        return SetLit(tuple(sorted((normalize(x) for x in e.items), key=str)))
    return e

def ast_diff(a, b):
    sa, sb = str(normalize(a)), str(normalize(b))
    if sa == sb:
        return 0
    import difflib
    sm = difflib.SequenceMatcher(None, sa, sb)
    return int((1 - sm.ratio()) * max(len(sa), len(sb)))

# =============================================================================
# REGISTERS
# =============================================================================

@dataclass
class Register:
    name: str
    lattice: dict
    arrow: dict
    quantor: dict
    qty: dict
    calculus: dict
    arev: str
    inscribe: dict

CMP_RENDER = {}  # per-register extra comparison renditions

def translate(reg: Register, e):
    unsup = []
    def go(node):
        if isinstance(node, (Var, Const)):
            return node.name
        if isinstance(node, App):
            head = reg.qty.get(node.head, node.head)
            return head + "(" + ", ".join(go(a) for a in node.args) + ")"
        if isinstance(node, Juxt):
            return "\u00b7".join(go(p) for p in node.parts)
        if isinstance(node, SetLit):
            return "{" + ", ".join(go(x) for x in node.items) + "}"
        if isinstance(node, Sup):
            return f"{go(node.base)}^{node.power}"
        if isinstance(node, Binder):
            r = reg.calculus.get(node.op, node.op)
            idx = f"_{node.index}" if node.index else ""
            return f"{r}{idx} ({go(node.body)})"
        if isinstance(node, Quant):
            g = go(node.guard) if node.guard else ""
            q = reg.quantor.get(node.quant, node.quant)
            scope = node.var + (f" \u2208 ({g})" if node.guard else "")
            return f"{q} {scope} ({go(node.body)})"
        if isinstance(node, Connect):
            op = node.op
            if op in CMP_OPS:
                sub = reg.arrow.get(op, CMP_RENDER.get((reg.name, op), op))
                return f"{go(node.args[0])} {sub} {go(node.args[1])}"
            table = reg.lattice if op in reg.lattice else reg.arrow
            if table and op in table:
                rend = table[op]
                if len(node.args) == 1:
                    return rend.replace("{A}", go(node.args[0]))
                return rend.replace("{A}", go(node.args[0])).replace("{B}", go(node.args[1]))
            unsup.append(op)
            if len(node.args) == 1:
                return f"{op}({go(node.args[0])})"
            return f"({go(node.args[0])}) {op} ({go(node.args[1])})"
        raise TypeError(node)
    return go(e), unsup

def inscribe(reg: Register, s: str):
    s2 = s
    for k, v in sorted(reg.inscribe.items(), key=lambda kv: -len(kv[0])):
        s2 = s2.replace(k, v)
    return parse_fragment(s2)[0]

SET = Register(
    name="Set",
    lattice={"\u2227": "({A}) \u2229 ({B})", "\u2228": "({A}) \u222a ({B})", "\u00ac": "\u0028\U0001d4d0 \\ {A}\u0029"},
    arrow={"\u2192": "({A})^c \u222a ({B})",
           "\u2194": "(({A})^c \u222a ({B})) \u2229 (({B})^c \u222a ({A}))"},
    quantor={"\u2200": "\u22c2", "\u2203": "\u22c3", "note": "uncountable meets unsupported v0"},
    qty={},
    calculus={"\u222e": "(deg)", "\u2211": "(deg)", "\u2202": "(deg)"},
    arev="A \u21a6 \U0001d4d0 \\ A",
    inscribe={"\u22c2": "\u2200", "\u22c3": "\u2203", "\u2229": "\u2227", "\u222a": "\u2228", "\u00b7": "\u2227"},
)

ORDER = Register(
    name="Order/Heyting",
    lattice={"\u2227": "({A}) \u2293 ({B})", "\u2228": "({A}) \u2294 ({B})", "\u00ac": "(({A}) \u21d2 \u22a5)"},
    arrow={"\u2192": "({A}) \u21d2 ({B})",
           "\u2194": "((({A}) \u21d2 ({B})) \u2293 (({B}) \u21d2 ({A})))"},
    quantor={"\u2200": "\u2a05", "\u2203": "\u2a04", "note": "meet/join over guarded index"},
    qty={},
    calculus={"\u222e": "(deg)", "\u2211": "(deg)", "\u2202": "(deg)"},
    arev="a \u21a6 a \u21d2 \u22a5",
    inscribe={"\u2a05": "\u2200", "\u2a04": "\u2203", "\u2293": "\u2227", "\u2294": "\u2228",
              "\u21d2": "\u2192", "\u22a5": "\u22a5"},
)

PROB = Register(
    name="Probability",
    lattice={"\u2227": "({A}) \u2229 ({B}) [P factorizes iff independent]",
             "\u2228": "({A}) \u222a ({B})", "\u00ac": "({A})^c"},
    arrow={"\u2192": "P(({B}) | ({A})) arm",
           "\u2194": "measure(({A}) \u2206 ({B})) = 0"},
    quantor={"\u2200": "sup", "\u2203": "witness",
             "note": "uncountable intersections are not events; v0 covers countable guards only"},
    qty={},
    calculus={"\u222e": "(deg)", "\u2211": "(deg)", "\u2202": "(deg)"},
    arev="A \u21a6 A^c",
    inscribe={},
)

ANALYSIS = Register(
    name="Analysis",
    lattice={"\u2227": "min(({A}), ({B}))", "\u2228": "max(({A}), ({B}))", "\u00ac": "-({A})"},
    arrow={"\u2192": "\u2200\u03b5>0 \u2203\u03b4>0 ( |({A}) - ({B})| < \u03b5 )",
           "\u2194": "({A}) = ({B}) pointwise",
           "\u226b": "(({A}) \u226b ({B}) : scale-separated)",
           "\u223c": "({A}) \u223c ({B}) asymptotic"},
    quantor={"\u2200": "sup", "\u2203": "attainment", "note": "uniform order is load-bearing v0"},
    qty={},
    calculus={"\u222e": "\u222e", "\u2211": "\u2211", "\u2202": "\u2202"},
    arev="f \u21a6 -f",
    inscribe={"min": "\u2227", "max": "\u2228", "sup": "\u2200"},
)

REGISTERS = {r.name: r for r in (SET, ORDER, PROB, ANALYSIS)}

# =============================================================================
# AREV COMMUTATION (instrument 2) — rule-level per register
# =============================================================================

def arev_check(reg: Register):
    """translate ¬(Φ∧Ψ) and ¬Φ∨¬Ψ; the register's ¬/∧/∨ rule set commutes with
    its own arev when the two renders agree after symbol-level normalization."""
    a, _ = translate(reg, parse_fragment("\u00ac(P \u2227 Q)")[0])
    b, _ = translate(reg, parse_fragment("\u00acP \u2228 \u00acQ")[0])
    # structural agreement: both must mention the same machinery
    ka = a.replace(" ", "").replace("(", "").replace(")", "")
    kb = b.replace(" ", "").replace("(", "").replace(")", "")
    return {"register": reg.name, "neg_meet": a, "join_negs": b, "agrees": ka == kb}

# =============================================================================
# SCAN (instrument 3)
# =============================================================================

def scan():
    sys.path.insert(0, "imscribing_grammar/navigators")
    import cl8nk_navigator as c8, cl9nk_navigator as c9
    frags = {}
    def take(tab):
        for ax, vals in tab.items():
            for g, (frag, atom, prox) in vals.items():
                frags.setdefault(frag.split("\u2014")[0].strip(), (ax + g, atom))
    take(c8.CL8NK_FORMULAE)
    if hasattr(c9, "CL9NK_FORMULAE"):
        take(c9.CL9NK_FORMULAE)
    rep = {"total": len(frags), "parse_fail": [], "gaps": set(), "expansions": {}, "regs": {}}
    for text, (key, atom) in sorted(frags.items()):
        try:
            ast = parse_fragment(text)[0]
            ea, maxd, expanded, cycles = walk(ast)
        except Exception as ex:
            rep["parse_fail"].append((key, text[:40], str(ex)[:100]))
            continue
        for name, d in expanded:
            rep["expansions"].setdefault(name, []).append(key)
        for rn, reg in REGISTERS.items():
            rec = {"key": key, "frag": text}
            try:
                out, unsup = translate(reg, ea)
                rec["rendered"] = out
                rec["unsup"] = unsup
                if not unsup and "(deg)" not in out:
                    try:
                        ins = inscribe(reg, out)
                        rec["residual"] = ast_diff(ea, ins)
                    except Exception as ex:
                        rec["residual"] = None
                        rec["inscribe_err"] = str(ex)[:80]
            except Exception as ex:
                rec["error"] = str(ex)[:100]
            rep["regs"].setdefault(rn, []).append(rec)
    return rep

# =============================================================================
# CLI
# =============================================================================

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "decompose":
        only = sys.argv[3] if len(sys.argv) > 3 else None
        ast = parse_fragment(sys.argv[2])[0]
        ea, maxd, expanded, cycles = walk(ast)
        print("AST      :", ea)
        print("expanded :", expanded or "none", "| max_depth:", maxd, "| cycles:", sorted(cycles) or "none")
        for rn, reg in REGISTERS.items():
            if only and rn != only:
                continue
            out, unsup = translate(reg, ea)
            print(f"[{rn}]".ljust(18), out)
            if unsup:
                print("           unsupported:", unsup)
        return
    if len(sys.argv) >= 2 and sys.argv[1] == "scan":
        rep = scan()
        print("fragments:", rep["total"], " parse failures:", len(rep["parse_fail"]))
        for k, t, e in rep["parse_fail"]:
            print("  FAIL", k, repr(t), e)
        for rn, rows in rep["regs"].items():
            ok = [x for x in rows if "error" not in x and "rendered" in x]
            full = [x for x in ok if not x["unsup"]]
            r0 = [x for x in ok if x.get("residual") == 0]
            print(f"[{rn}] rendered {len(ok)}/{len(rows)}  full-rule {len(full)}  residual0 {len(r0)}")
            for x in rows:
                if "error" in x:
                    print("   ERR", x["key"], x["error"])
        print("expansion uses:", {k: len(v) for k, v in rep["expansions"].items()})
        return
    print(__doc__)

if __name__ == "__main__":
    main()
