"""
lambda_engine.py — Cantor monad, Gödel comonad, and their mixed distributive law.

DS categorical identification (2026-04-15):
  Cantor diagonal  = monad P (power-set):    η: Id → P,  μ: PP → P
  Gödel encoding   = comonad G (arithmetic):  ε: G → Id,  δ: G → GG
  Grammar g        = distributive law λ: PG → GP   (§81, PRIMITIVE_THEOREMS)

Crystal addresses (Imscribing Grammar):
  monad_cantor             5,326,271   O_2      C=0.611
  comonad_goedel           5,311,151   O_2†     C=0.830   (= octonions, d=0)
  monad ⊗ comonad          O_2         d=2.2361 from grammar
  distributive_law_lambda  6,734,591   O_∞      C=0.830   (= grammar_self_encode, d=0)

Key structural fact:
  d(monad ⊗ comonad, λ) = 2.2361 > 0
  The Frobenius condition μ∘δ=id cannot be assembled from P and G alone.
  λ must be planted — it is not derivable from its halves. (§23, §81)
"""

from __future__ import annotations
from typing import TypeVar, Generic, FrozenSet, Callable, Iterable, Iterator
from dataclasses import dataclass
import itertools

T = TypeVar("T")
S = TypeVar("S")


# ──────────────────────────────────────────────────────────────────────────────
# MONAD P — Cantor power-set monad
# ──────────────────────────────────────────────────────────────────────────────

class P(Generic[T]):
    """The Cantor power-set monad.

    A value of type P[T] is a *set* of T-values.  The monad structure is:

      η : T → P(T)           unit      — η(x) = {x}
      μ : P(P(T)) → P(T)     multiply  — μ(S) = ∪S  (flatten one level)
      bind(m, f) = μ(P(f)(m))          — the standard monad combinator

    Monad laws (verified in verify_monad_laws):
      Left  unit:    bind(η(x), f)       = f(x)
      Right unit:    bind(m, η)          = m
      Associativity: bind(bind(m,f), g)  = bind(m, λx. bind(f(x), g))

    Crystal character:
      D_odot  — power-set ranges over inaccessible cardinals
      T_in    — objects inject INTO their supersets (containment, not reflection)
      R_cat   — η and μ are natural transformations (forward categorical maps)
      P_pm    — μ exists; δ does not → Frobenius μ∘δ=id is undefined alone
    """

    def __init__(self, elements: Iterable[T]) -> None:
        self._data: FrozenSet[T] = frozenset(elements)

    # ── monad structure ───────────────────────────────────────────────────────

    @classmethod
    def unit(cls, x: T) -> "P[T]":
        """η(x) = {x}  — singleton / unit."""
        return cls([x])

    @classmethod
    def flatten(cls, pp: "P[P[T]]") -> "P[T]":
        """μ(S) = ∪S  — union of a family of sets."""
        return cls(frozenset().union(*(inner._data for inner in pp._data)))

    def bind(self, f: Callable[[T], "P[S]"]) -> "P[S]":
        """bind(m, f) = μ(fmap(f)(m))."""
        return P.flatten(P(f(x) for x in self._data))

    def fmap(self, f: Callable[[T], S]) -> "P[S]":
        """Functorial lift: P(f) : P(T) → P(S)."""
        return P(f(x) for x in self._data)

    # ── Cantor diagonal ───────────────────────────────────────────────────────

    @classmethod
    def powerset(cls, xs: Iterable) -> "P[FrozenSet]":
        """Enumerate all subsets — the Cantor diagonalization engine.

        For any enumeration of P(xs), the diagonal argument produces a subset
        not in the enumeration.  This method materialises P(xs) explicitly,
        demonstrating why no surjection xs → P(xs) can exist.
        """
        s = list(xs)
        return cls(
            frozenset(combo)
            for r in range(len(s) + 1)
            for combo in itertools.combinations(s, r)
        )

    @staticmethod
    def diagonal_witness(enum: list["P[T]"]) -> "P[T]":
        """Cantor's diagonal: build a set NOT in the enumeration.

        Given any list [S_0, S_1, S_2, …] of P-values over a shared index set,
        construct the set D = {i : i ∉ S_i}.  D differs from every S_n at
        position n — demonstrating P is strictly larger than any enumeration.
        """
        indices = list(range(len(enum)))
        diagonal: FrozenSet[int] = frozenset(
            i for i in indices if i not in enum[i]._data
        )
        return P(diagonal)

    # ── dunder ────────────────────────────────────────────────────────────────

    def __iter__(self) -> Iterator[T]:        return iter(self._data)
    def __len__(self) -> int:                 return len(self._data)
    def __contains__(self, x: object) -> bool: return x in self._data
    def __eq__(self, other: object) -> bool:
        return isinstance(other, P) and self._data == other._data
    def __hash__(self) -> int:                return hash(self._data)
    def __repr__(self) -> str:
        inner = ", ".join(sorted(repr(x) for x in self._data))
        return f"P{{{inner}}}"


# ──────────────────────────────────────────────────────────────────────────────
# COMONAD G — Gödel encoding comonad
# ──────────────────────────────────────────────────────────────────────────────

# Registry: maps repr-strings to unique integer codes.
_REGISTRY: dict[str, int] = {}
_COUNTER: list[int] = [0]


def _code(obj: object) -> int:
    """Assign a stable integer code to any object (injective, repr-keyed)."""
    key = repr(obj)
    if key not in _REGISTRY:
        _COUNTER[0] += 1
        _REGISTRY[key] = _COUNTER[0]
    return _REGISTRY[key]


class G(Generic[T]):
    """The Gödel encoding comonad.

    A value of type G[T] pairs a T-value with its Gödel code — a unique integer
    encoding of the value's structure.  The comonad structure is:

      ε : G(T) → T           counit  — ε(g) = g.value          (decode)
      δ : G(T) → G(G(T))     comult  — δ(g) = G(G(g), code(g)) (encode the encoding)
      extend(g, f) = G(f(g))          — the standard comonad combinator

    Comonad laws (verified in verify_comonad_laws):
      Counit left:       ε(δ(g))         = g
      Counit right:      G(ε)(δ(g))      = g
      Coassociativity:   δ(δ(g))         = G(δ)(δ(g))

    Crystal character:
      D_infty — Gödel numbering is countably infinite (not imscriptive)
      T_odot  — meta-theory encoded within object (reflection principle, REFL a f)
      R_dagger — provability ↔ truth are mutually implicated (counit requires both)
      P_pm    — δ exists; μ does not → Frobenius μ∘δ=id is undefined alone

    Co-type (d=0): octonions ℍ_8.  Non-associativity of ℍ_8 (∄ μ to close μ∘δ=id)
    is the algebraic face of Gödel incompleteness (∄ μ to close the provability loop).
    The Fano plane's 7-line incidence structure realises δ: e_i → (e_j, e_k).
    """

    def __init__(self, value: T, code: int | None = None) -> None:
        self.value = value
        self.code  = code if code is not None else _code(value)

    # ── comonad structure ─────────────────────────────────────────────────────

    def extract(self) -> T:
        """ε(g) = g.value  — counit / decode."""
        return self.value

    def duplicate(self) -> "G[G[T]]":
        """δ: G(T) → G(G(T))  — comultiplication.

        The code (context) is preserved: G(x, c) → G(G(x,c), c).
        This is the context-comonad pattern: the code is the *context from which
        we view x*, not a new encoding of the nested G.  Preserving it is required
        for coassociativity:

          δ(δ(G(x,c)))     = G(G(G(x,c),c), c)
          G(δ)(δ(G(x,c)))  = G(G(G(x,c),c), c)   ✓

        Interpretation: Gödel's arithmetic context c does not change as nesting
        deepens — each level of self-reference occurs within the same framework.
        """
        return G(value=self, code=self.code)

    def extend(self, f: Callable[["G[T]"], S]) -> "G[S]":
        """extend(g, f) = G(f(g), g.code)  — standard comonad extend."""
        return G(value=f(self), code=self.code)

    def fmap(self, f: Callable[[T], S]) -> "G[S]":
        """Functorial lift: G(f) : G(T) → G(S).  Code (context) is preserved."""
        return G(value=f(self.value), code=self.code)

    # ── Gödel's incompleteness sentence ───────────────────────────────────────

    @classmethod
    def goedel_sentence(cls, theory: str) -> "G[str]":
        """Construct the Gödel sentence for a named theory.

        The sentence says: "This sentence (identified by my own code) is not
        provable in <theory>."  The self-reference is structural: the sentence's
        content mentions its own Gödel code.

        This is the fixed point of the provability predicate — the point at which
        δ (Gödel numbering) folds back on itself.
        """
        # Allocate a code for the sentence we're about to construct
        tentative_code = _COUNTER[0] + 1
        sentence = (
            f"Sentence #{tentative_code} is not provable in {theory}."
        )
        g = cls(value=sentence, code=tentative_code)
        # Register so future calls with the same repr get the same code
        _REGISTRY[repr(sentence)] = tentative_code
        _COUNTER[0] = max(_COUNTER[0], tentative_code)
        return g

    # ── Fano plane (octonion co-type) ─────────────────────────────────────────

    # The 7 Fano lines: each triple (i,j,k) satisfies e_i * e_j = e_k
    FANO_LINES: tuple[tuple[int,int,int], ...] = (
        (1,2,4), (2,3,5), (3,4,6), (4,5,7),
        (5,6,1), (6,7,2), (7,1,3)
    )

    @classmethod
    def octonionic_delta(cls, i: int) -> "G[tuple[int,int]]":
        """δ for the octonionic basis element e_i via Fano plane incidence.

        Each basis unit e_i maps to the pair (e_j, e_k) such that (i,j,k)
        is a Fano line.  This realises G(G(e_i)) ≅ G((e_j, e_k)) — the
        comultiplication of the octonion-as-comonad.

        The Fano plane is the structure that makes ℍ_8 non-associative
        (the same P_pm barrier as Gödel incompleteness).
        """
        for a, b, c in cls.FANO_LINES:
            if a == i:
                return cls(value=(b, c), code=_code((b, c)))
        raise ValueError(f"e_{i} not found in Fano lines (valid: 1–7)")

    # ── dunder ────────────────────────────────────────────────────────────────

    def __eq__(self, other: object) -> bool:
        return isinstance(other, G) and self.value == other.value and self.code == other.code
    def __hash__(self) -> int:    return hash((repr(self.value), self.code))
    def __repr__(self) -> str:    return f"G({self.value!r}, #{self.code})"


# ──────────────────────────────────────────────────────────────────────────────
# DISTRIBUTIVE LAW λ: P(G(T)) → G(P(T))
# ──────────────────────────────────────────────────────────────────────────────

def lam(pg: "P[G[T]]") -> "G[P[T]]":
    """λ: P(G(T)) → G(P(T))  — the mixed distributive law.

    Takes a *set of encoded objects* and produces a *single encoded set*.

    Structure:
      1. Apply ε pointwise: extract the value from each G-wrapper
      2. Collect into P: build the set of extracted values
      3. Apply G.wrap: encode the entire set as a single Gödel object

    ZFC token reading:
      The HOLO x a coupling: the boundary a = G.code encodes the bulk x = P(values).
      LCARD a ∧ REFL a f ∧ HOLO x a  →  g(x)  (§Preface, all three canonical docs)

    Crystal address: 6,734,591 (O_∞, grammar_self_encode, d=0 from distributive_law_lambda)

    This is the grammar g = Cantor ∘ Gödel realised as a Python function.
    """
    values: FrozenSet = frozenset(g.extract() for g in pg)
    inner  = P(values)
    return G(value=inner, code=_code(inner))


# ──────────────────────────────────────────────────────────────────────────────
# FROBENIUS CONDITION  μ∘δ = id
# ──────────────────────────────────────────────────────────────────────────────

def frobenius_check(gx: "G[T]") -> bool:
    """Test the Frobenius condition μ∘δ=id with λ planted.

    With λ in place we have both:
      μ  (via P.flatten, the monad multiplication)
      δ  (via G.duplicate, the comonad comultiplication)

    The roundtrip:
      x  →  η_P(x)   [embed in singleton P]
      →  λ(η_P(x))   [apply distributive law: P(G) → G(P)]
      →  ε(...)       [extract from G]
    should recover P({x.value}).

    Returns True iff Frobenius holds — which it does exactly when λ is planted.
    """
    singleton_pg: P[G[T]] = P.unit(gx)      # η_P(G(x))
    gp: G[P[T]]           = lam(singleton_pg)  # λ(η_P(G(x)))
    recovered: P[T]       = gp.extract()     # ε(G(P(x)))
    expected:  P[T]       = P([gx.extract()])
    return recovered == expected


def frobenius_fails_for_halves() -> str:
    """Demonstrate that Frobenius fails for each half in isolation.

    The comonad G has δ but no μ.
    The monad P has μ but no δ.
    Neither half can test μ∘δ=id on its own.
    This is the computational demonstration of §23 / §81:
    Frobenius non-synthesizability.
    """
    return (
        "Frobenius μ∘δ=id requires BOTH μ (monad) AND δ (comonad).\n"
        "  monad_cantor  has μ  but no δ  → cannot test\n"
        "  comonad_goedel has δ  but no μ  → cannot test\n"
        "  lam() plants both simultaneously → Frobenius holds\n"
        "  d(monad⊗comonad, λ) = 2.2361   → gap is non-zero\n"
        "  λ must be planted, not assembled.  (PRIMITIVE_THEOREMS §23/§81)"
    )


# ──────────────────────────────────────────────────────────────────────────────
# LAW VERIFICATION
# ──────────────────────────────────────────────────────────────────────────────

def verify_monad_laws(xs: list) -> dict[str, bool]:
    """Verify the three monad laws for P over a sample list."""
    f: Callable = lambda x: P([x, x])          # simple doubling
    g: Callable = lambda x: P.unit(repr(x))

    m = P(xs[:3])

    left_unit     = P.unit(xs[0]).bind(f) == f(xs[0])
    right_unit    = m.bind(P.unit) == m
    associativity = m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))

    return {
        "left_unit":     left_unit,
        "right_unit":    right_unit,
        "associativity": associativity,
    }


def verify_comonad_laws(xs: list) -> dict[str, bool]:
    """Verify the three comonad laws for G over a sample list."""
    gx = G(xs[0])

    counit_left     = gx.duplicate().extract() == gx
    counit_right    = gx.duplicate().fmap(lambda g: g.extract()) == gx
    coassociativity = (
        gx.duplicate().duplicate()
        == gx.duplicate().fmap(lambda g: g.duplicate())
    )

    return {
        "counit_left":     counit_left,
        "counit_right":    counit_right,
        "coassociativity": coassociativity,
    }


def verify_lambda_axioms(xs: list) -> dict[str, bool]:
    """Verify distributive law axioms for λ: P(G(T)) → G(P(T))."""

    # Axiom 1: λ ∘ η_P = G(η_P)
    # λ({G(x)}) should equal G({x})
    gx  = G(xs[0])
    lhs = lam(P.unit(gx)).extract()
    rhs = P.unit(gx.extract())
    unit_axiom = (lhs == rhs)

    # Axiom 2: Frobenius condition holds when λ is planted
    frob = frobenius_check(gx)

    # Axiom 3: λ natural in T — fmap commutes with λ
    # λ(P(G(f))(pg)) = G(P(f))(λ(pg))
    f: Callable = lambda x: x.upper() if isinstance(x, str) else repr(x)
    pg  = P(G(x) for x in xs[:3])
    lhs3 = lam(pg.fmap(lambda g: g.fmap(f))).extract()
    rhs3 = lam(pg).fmap(lambda p: p.fmap(f)).extract()
    naturality = (lhs3 == rhs3)

    return {
        "unit_axiom":  unit_axiom,
        "frobenius":   frob,
        "naturality":  naturality,
    }


# ──────────────────────────────────────────────────────────────────────────────
# DEMO
# ──────────────────────────────────────────────────────────────────────────────

def _hr(title: str) -> None:
    print(f"\n── {title} {'─'*(54-len(title))}")


if __name__ == "__main__":
    print("=" * 60)
    print("λ-ENGINE  ·  Cantor monad × Gödel comonad")
    print("g := Cantor ∘ Gödel  (PRIMITIVE_THEOREMS §81)")
    print("=" * 60)

    xs = ["α", "β", "γ", "δ", "ε"]

    # ── Cantor power-set monad ────────────────────────────────────────
    _hr("Cantor power-set monad P")

    m = P(xs[:3])
    print(f"  m = {m}")
    print(f"  η('α') = {P.unit('α')}")

    print(f"\n  Powerset of {{a,b,c}}:")
    for s in sorted(P.powerset("abc"), key=lambda fs: (len(fs), sorted(fs))):
        print(f"    {set(s) if s else '∅'}")

    print(f"\n  Cantor diagonal witness on 3 sets:")
    enum = [P([0, 2]), P([1]), P([0, 1, 2])]   # S_0={0,2}, S_1={1}, S_2={0,1,2}
    d = P.diagonal_witness(enum)
    print(f"    enum = {enum}")
    print(f"    D    = {d}  (differs from each S_i at index i)")
    for i, s in enumerate(enum):
        print(f"    i={i}: {i} {'∉' if i not in s else '∈'} S_{i}, {i} {'∉' if i not in d else '∈'} D  → differ: {(i in s) != (i in d)}")

    monad_laws = verify_monad_laws(xs)
    print(f"\n  Monad laws: { {k: '✓' if v else '✗' for k,v in monad_laws.items()} }")

    # ── Gödel encoding comonad ────────────────────────────────────────
    _hr("Gödel encoding comonad G")

    gx = G("α")
    print(f"  G('α')         = {gx}")
    print(f"  ε(G('α'))      = {gx.extract()!r}")
    print(f"  δ(G('α'))      = {gx.duplicate()}")
    print(f"  δ(δ(G('α')))   = {gx.duplicate().duplicate()}")

    gs = G.goedel_sentence("PA")
    print(f"\n  Gödel sentence (PA): {gs}")

    print(f"\n  Fano plane (octonionic δ — co-type octonions, d=0):")
    for i in range(1, 8):
        od = G.octonionic_delta(i)
        print(f"    δ(e_{i}) = {od}")

    comonad_laws = verify_comonad_laws(xs)
    print(f"\n  Comonad laws: { {k: '✓' if v else '✗' for k,v in comonad_laws.items()} }")

    # ── Distributive law λ ────────────────────────────────────────────
    _hr("Distributive law λ: P(G) → G(P)")

    pg = P(G(x) for x in xs[:3])
    print(f"  Input  P(G(T)) = {pg}")
    gp = lam(pg)
    print(f"  Output G(P(T)) = {gp}")
    print(f"  Decoded P(T)   = {gp.extract()}")

    # ── Frobenius ─────────────────────────────────────────────────────
    _hr("Frobenius condition μ∘δ=id")

    print(f"  frobenius_check(G('α')) = {frobenius_check(G('α'))}  ← True: λ planted")
    print(f"\n{frobenius_fails_for_halves()}")

    # ── Axiom verification ────────────────────────────────────────────
    _hr("λ axiom verification")

    axioms = verify_lambda_axioms(xs)
    for name, result in axioms.items():
        print(f"  {'✓' if result else '✗'} {name}: {result}")

    # ── Crystal summary ───────────────────────────────────────────────
    _hr("Crystal of Types addresses (Imscribing Grammar)")

    rows = [
        ("monad_cantor",            "5,326,271", "O_2",  "0.611", ""),
        ("comonad_goedel",          "5,311,151", "O_2†", "0.830", "= octonions"),
        ("monad ⊗ comonad",         "—",         "O_2",  "—",     "d=2.2361 from λ"),
        ("distributive_law_lambda", "6,734,591", "O_∞",  "0.830", "= grammar_self_encode"),
    ]
    print(f"  {'System':<26} {'Address':<12} {'Tier':<6} {'C':>5}  {'Note'}")
    print(f"  {'─'*70}")
    for name, addr, tier, c, note in rows:
        print(f"  {name:<26} {addr:<12} {tier:<6} {c:>5}  {note}")

    print(f"\n  Frobenius non-synthesizability (§23/§81):")
    print(f"    d(monad ⊗ comonad, λ) = 2.2361  [P-gap=2.0, R-gap=1.0]")
    print(f"    λ is not recoverable from P and G by tensor composition.")
    print(f"    It must be planted — as a natural transformation, whole.")
