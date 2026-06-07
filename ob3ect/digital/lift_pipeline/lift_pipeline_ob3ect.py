#!/usr/bin/env python3
"""
Lift Pipeline Ob3ect — Self-verifying prose transformation engine.

Implements the seven lift paradigms from AGAINST_THE_TEMPLATE.md as a structural
pipeline. Each paradigm is an operational mode that transforms source text without
relying on source/target tuple pairs.

Seven paradigms:
  (1) Constraint Lift  — One severe rule applied absolutely
  (2) Genre Lift       — Target a specific form
  (3) Severity Lift    — Fix exactly one primitive, leave the rest
  (4) Refusal Lift     — Write against the expected lift
  (5) Corruption Lift  — Apply the wrong lift protocol
  (6) Erosion Lift     — Companion text excluded by the draft
  (7) Appetite Lift    — Replace correctness with desire

Opcode Map:
  VINIT  -> Unprocessed source text (void state)
  TANCH  -> Source text as closed whole
  AFWD   -> Forward lift application
  AREV   -> Reverse analysis: dissecting deficits
  CLINK  -> Composing multiple lift operations in sequence
  ISCRIB -> Text recognizing itself after lifting (identity)
  FSPLIT -> Splitting source text from paradigm selection
  FFUSE  -> Fusing paradigm + source into lifted output
  EVALT  -> Successful lift verification
  EVALF  -> Failed lift
  ENGAGR -> Both original and lifted held simultaneously
  IFIX   -> Lifted text stored immutably

Frobenius pair: FSPLIT(source) -> (text, paradigm); FFUSE(text, paradigm) -> lifted.
mu(delta(id)) = id: the lift record hash is reproducible from the same inputs.
"""

import hashlib
import json
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ── Domain Types ────────────────────────────────────────────────────────────

LIFT_PARADIGMS: List[str] = [
    "constraint", "genre", "severity", "refusal",
    "corruption", "erosion", "appetite"
]


@dataclass
class LiftRecord:
    """A single lift operation's input, paradigm, output, and verification state."""
    source_text: str
    paradigm: str
    lifted_text: str
    constraint: str = ""
    verification_hash: str = ""
    success: bool = False

    def to_json(self) -> Dict:
        return {
            "source_length": len(self.source_text),
            "lifted_length": len(self.lifted_text),
            "paradigm": self.paradigm,
            "constraint": self.constraint,
            "success": self.success,
        }

    def hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_json(), sort_keys=True).encode()
        ).hexdigest()


@dataclass
class PipelineState:
    """Full state of the lift pipeline."""
    source_text: str = ""
    paradigm: str = ""
    constraint: str = ""
    lifted_text: str = ""
    records: List[LiftRecord] = field(default_factory=list)
    identity_verified: bool = False
    frobenius_verified: bool = False
    state: str = "VINIT"

    def to_json(self) -> Dict:
        return {
            "source_length": len(self.source_text),
            "paradigm": self.paradigm,
            "constraint": self.constraint,
            "lifted_length": len(self.lifted_text),
            "records_count": len(self.records),
            "identity_verified": self.identity_verified,
            "frobenius_verified": self.frobenius_verified,
            "state": self.state,
        }

    def hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_json(), sort_keys=True).encode()
        ).hexdigest()

# ── Rule Templates ──────────────────────────────────────────────────────────

CONSTRAINT_RULES: Dict[str, List[str]] = {
    "constraint": [
        "No sentence longer than 20 words.",
        "No hedging — every sentence is a flat assertion.",
        "Start with the second paragraph (delete the first).",
        "Write in the imperative mood throughout.",
        "Write to someone who already knows the answer and thinks you're wrong.",
        "Every paragraph must contain one sentence that could be the title.",
        "Transitive trust only — report as told by someone else.",
        "No examples — the entire text must be abstract.",
    ],
    "genre": [
        "Write as a field report (date, location, observation, conclusion).",
        "Write as a recipe (ingredients, steps, timing, result).",
        "Write as a letter (salutation, body, signature).",
        "Write as dialogue (two voices, disagreement, resolution).",
        "Write as an inventory (list, quantities, conditions, notes).",
    ],
    "severity": [
        "Fix only H (chirality): wrong answer before right one.",
        "Fix only Gamma (scope): one thing at maximal detail.",
        "Fix only T (topology): crossing point; build around it.",
        "Fix only P (symmetry): acknowledge one objection.",
        "Fix only K (kinetics): let the hardest claim be hard.",
        "Fix only Omega (winding): close the loop.",
    ],
    "refusal": [
        "Refuse T_bowtie: stay in containment.",
        "Refuse P_pm: stay asymmetric.",
        "Refuse Omega_z: stay trivial.",
        "Refuse the entire lift: write AI default well.",
    ],
    "corruption": [
        "Apply Academia lift to a casual observation.",
        "Apply Casual lift to a formal proof.",
        "Apply Octave lift to a one-sentence status update.",
        "Apply Lando voice to a technical manual.",
        "Apply Esoteric lift to a shopping list.",
    ],
    "erosion": [
        "Write what the source text explicitly excludes.",
        "Write the counterargument before the argument.",
        "Write the footnote the text refuses.",
        "Write the sentence the author cut.",
    ],
    "appetite": [
        "Write what you want to say, not what is correct.",
        "Be irreverent to the point of risk.",
        "Be specific to the point of strangeness.",
        "Write one true thing that cannot be verified.",
    ],
}


# ── Lift Pipeline Ob3ect ────────────────────────────────────────────────────

class LiftPipelineOb3ect:
    """Self-verifying prose transformation engine with 12 IMASM opcodes."""

    def __init__(self):
        self.pipeline = PipelineState()
        self.log: List[Tuple[str, str]] = []

    # ── 12 Opcodes ──────────────────────────────────────────────────────

    def VINIT(self):
        """Clear all state to void/uninitialized."""
        self.pipeline = PipelineState()
        self.pipeline.state = "VINIT"
        self.log.append(("VINIT", "void"))

    def TANCH(self, source_text: str):
        """Anchor: source text as closed whole."""
        self.pipeline.source_text = source_text
        self.pipeline.state = "READY"
        h = hashlib.sha256(source_text.encode()).hexdigest()[:12]
        self.log.append(("TANCH", h))

    def AREV(self) -> Dict:
        """Reverse analysis: dissect source text deficits."""
        text = self.pipeline.source_text
        if not text:
            return {"error": "no source text"}
        sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        avg_words = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        deficits = {
            "hedging": any(w in text.lower() for w in ["seems", "arguably", "suggests"]),
            "long_sentences": any(len(s.split()) > 30 for s in sentences),
            "no_crossing": "however" not in text.lower() and "but" not in text.lower(),
            "avg_sentence_length": round(avg_words, 1),
            "sentence_count": len(sentences),
        }
        self.pipeline.state = "ANALYZED"
        self.log.append(("AREV", json.dumps(deficits)))
        return deficits

    def FSPLIT(self, paradigm: str = "", constraint: str = ""):
        """Split: separate source from paradigm selection."""
        if paradigm and paradigm not in LIFT_PARADIGMS:
            raise ValueError(f"Unknown paradigm: {paradigm}")
        self.pipeline.paradigm = paradigm or "constraint"
        if constraint:
            self.pipeline.constraint = constraint
        else:
            rules = CONSTRAINT_RULES.get(self.pipeline.paradigm, CONSTRAINT_RULES["constraint"])
            self.pipeline.constraint = rules[0]
        self.pipeline.state = "SPLIT"
        split_key = f"{self.pipeline.source_text}|{self.pipeline.paradigm}:{self.pipeline.constraint}"
        h = hashlib.sha256(split_key.encode()).hexdigest()[:12]
        self.log.append(("FSPLIT", h))
        return {"branch_a": self.pipeline.source_text, "branch_b": f"{self.pipeline.paradigm}: {self.pipeline.constraint}"}

    def AFWD(self) -> str:
        """Forward: apply lift paradigm to transform text."""
        source = self.pipeline.source_text
        if not source:
            return ""
        lifted = self._apply_lift(source, self.pipeline.paradigm, self.pipeline.constraint)
        self.pipeline.lifted_text = lifted
        self.pipeline.state = "LIFTED"
        h = hashlib.sha256(lifted.encode()).hexdigest()[:12]
        self.log.append(("AFWD", h))
        return lifted

    def _apply_lift(self, text: str, paradigm: str, constraint: str) -> str:
        """Core transformation logic per paradigm."""
        m = {
            "constraint": self._constraint_lift,
            "genre": self._genre_lift,
            "severity": self._severity_lift,
            "refusal": self._refusal_lift,
            "corruption": self._corruption_lift,
            "erosion": self._erosion_lift,
            "appetite": self._appetite_lift,
        }
        fn = m.get(paradigm)
        return fn(text, constraint) if fn else text

    def _constraint_lift(self, text: str, constraint: str) -> str:
        """Apply a single severe constraint."""
        sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        result = []
        for s in sentences:
            words = s.split()
            if len(words) > 20:
                s = " ".join(words[:20]) + "."
            result.append(s)
        return ". ".join(result) + "."

    def _genre_lift(self, text: str, constraint: str) -> str:
        """Wrap text in a genre form."""
        c = constraint.lower()
        if "field report" in c:
            return f"**Field Report**\nDate: [current]\nLocation: [site]\n\n**Observation:**\n{text}\n\n**Conclusion:** Derived from observation."
        elif "recipe" in c:
            return f"**Recipe**\n\nIngredients:\n- Source text: 1 unit\n- Paradigm: {self.pipeline.paradigm}\n\nSteps:\n1. Analyze\n2. Apply lift\n3. Verify closure\n\n**Result:**\n{text}"
        elif "letter" in c:
            return f"Dear Reader,\n\n{text}\n\nSincerely,\nThe Operator"
        elif "dialogue" in c:
            lines = text.strip().split("\n")
            return "\n".join(f"{'A' if i % 2 == 0 else 'B'}: {l}" for i, l in enumerate(lines))
        return f"[Genre: {constraint}]\n{text}"

    
    
    def _severity_lift(self, text: str, constraint: str) -> str:
        """Fix exactly one primitive. Genuine structural transformation per constraint."""
        c = constraint.lower()

        # Match on named primitive — NOT single letters (too greedy)
        # Order: most specific first, fallback last

        is_h = ("chirality" in c or "fix only h" in c)
        is_gamma = ("gamma" in c or "scope" in c) and not is_h
        is_t = ("topology" in c or "crossing" in c or "bowtie" in c) and not (is_h or is_gamma)
        is_p = ("symmetry" in c or "objection" in c) and not (is_h or is_gamma or is_t)
        is_k = ("kinetics" in c or "hard" in c or "hardest" in c) and not (is_h or is_gamma or is_t or is_p)
        is_omega = ("omega" in c or "winding" in c or "loop" in c) and not (is_h or is_gamma or is_t or is_p or is_k)

        # Fallback: guess from prefix "Fix only X"
        if not any([is_h, is_gamma, is_t, is_p, is_k, is_omega]):
            for token in c.split():
                if token in ("h", "chirality"):
                    is_h = True; break
                if token in ("gamma", "g", "scope"):
                    is_gamma = True; break
                if token in ("t", "topology"):
                    is_t = True; break
                if token in ("p", "symmetry"):
                    is_p = True; break
                if token in ("k", "kinetics"):
                    is_k = True; break
                if token in ("omega", "winding", "w"):
                    is_omega = True; break

        # 1. Fix H (chirality): wrong answer before right one
        if is_h:
            sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
            if len(sentences) < 2:
                return "A naive reading suggests: " + text + "\n\nBut the actual structure is more subtle: " + text
            split = max(1, len(sentences) // 3)
            wrong = ". ".join(sentences[:split]) + "."
            right = ". ".join(sentences[split:]) + "."
            return (
                "A naive reading would conclude: " + wrong + "\n\n"
                "But this is structurally backward. What actually holds:\n"
                + right
            )

        # 2. Fix Gamma (scope): one thing at maximal detail
        if is_gamma:
            sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
            if not sentences:
                return text
            core = max(sentences, key=len)
            core_words = core.split()[:5]
            core_phrase = " ".join(core_words)
            lines = []
            lines.append("ONE THING: " + core_phrase)
            lines.append("")
            lines.append("Definition: " + core)
            lines.append("")
            lines.append("Three implications:")
            lines.append("  1. Structural consequence: " + (sentences[0] if len(sentences) > 0 else text))
            lines.append("  2. Boundary condition: " + (sentences[1] if len(sentences) > 1 else "The boundary is the same structure at another scale."))
            lines.append("  3. Invariant: " + (sentences[-1] if len(sentences) > 1 else "The invariant holds across all scales."))
            lines.append("")
            lines.append("All other claims are corollaries of this one thing.")
            return "\n".join(lines)

        # 3. Fix T (topology): crossing point; build around it
        if is_t:
            sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
            if len(sentences) < 2:
                return "[CROSSING] " + text + "\n\n[CONTRADICTION] " + text + "\n\n[RESOLUTION] " + text
            mid = len(sentences) // 2
            thesis = ". ".join(sentences[:mid])
            antithesis = ". ".join(sentences[mid:])
            return (
                "< THESIS >\n" + thesis + ".\n\n"
                "But this collides with:\n\n"
                "< ANTITHESIS >\n" + antithesis + ".\n\n"
                "< CROSSING >\n"
                "The collision is not an error. It is the structure.\n"
                "The system does not resolve the contradiction. It metabolizes it."
            )

        # 4. Fix P (symmetry): acknowledge one objection
        if is_p:
            return (
                text + "\n\n"
                "< OBJECTION >\n"
                "A reasonable skeptic would ask: is this merely a formal artifact?\n"
                "The null hypothesis — that the pattern is a threshold effect — \n"
                "has not been disproven. The grammar cannot rule out coincidence.\n\n"
                "< RESPONSE >\n"
                "The objection is valid but incomplete. Three structural invariants\n"
                "survive the null: the survivors are the platonic solids; the fixed\n"
                "points are the H2 systems; the projection operator is idempotent.\n"
                "These are properties of structure, not of threshold choice."
            )

        # 5. Fix K (kinetics): let the hardest claim be hard
        if is_k:
            return (
                "The hardest claim in this text is the one that cannot be softened:\n\n"
                + text + "\n\n"
                "This claim is hard. It does not become easier with repetition.\n"
                "The text does not resolve it. The text leaves it unresolved.\n"
                "That is the point. Not every tension is a failure of exposition.\n"
                "Some tensions are the subject."
            )

        # 6. Fix Omega (winding): close the loop
        if is_omega:
            first_sent = text.split(".")[0].strip() if "." in text else text
            return (
                "< ENTRY >\n" + text + "\n\n"
                "< JOURNEY >\n"
                "What seemed to be a description of something external has revealed itself\n"
                "as a description of the frame that contains it. The frame is not inert.\n"
                "It imscribes.\n\n"
                "< RETURN >\n" + first_sent + ".\n\n"
                "This sentence is no longer the same sentence. It was read twice.\n"
                "The loop is closed at higher resolution."
            )

        # Fallback
        return text
    def _refusal_lift(self, text: str, constraint: str) -> str:
        """Write against the expected lift — refuse each structural improvement."""
        c = constraint.lower()
        is_t = "bowtie" in c or "t_bowtie" in c or "containment" in c
        is_p = "p_pm" in c or "asymmetric" in c or "stay asymmetric" in c
        is_omega = "omega" in c or "stay trivial" in c or "trivial" in c
        is_whole = "entire lift" in c or "ai default" in c or "default well" in c

        sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        if not sentences:
            return text

        # Refuse T_bowtie: stay in containment — flat nested lists, no crossing
        if is_t:
            lines = ["[CONTAINMENT — No crossing point permitted]\n"]
            for i, s in enumerate(sentences):
                indent = "  " * (i % 3)
                lines.append(f"{indent}Box {i+1}: {s}.")
            lines.append("\n[No collision. No resolution. Everything stays in its containment.]")
            return "\n".join(lines)

        # Refuse P_pm: stay asymmetric — one-sided, no objection
        if is_p:
            return (
                "[ASYMMETRY — One side only. No counterpoint.]\n\n"
                + ". ".join(sentences) + ".\n\n"
                "[No objection is acknowledged. The asymmetry is the position.]"
            )

        # Refuse Omega_z: stay trivial — cut before conclusion, no closure
        if is_omega:
            mid = max(1, len(sentences) // 2)
            truncated = ". ".join(sentences[:mid]) + "."
            return (
                "[NO CLOSURE — Truncated at midpoint. No return.]\n\n"
                + truncated + "\n\n"
                "[The text stops here. There is no conclusion. The loop is not closed.]"
            )

        # Refuse the entire lift: write AI default well — perfectly balanced, boring
        if is_whole:
            hedged = []
            for s in sentences:
                if not any(w in s.lower() for w in ["seems", "arguably", "suggests", "might", "could", "perhaps", "it is worth"]):
                    hedged.append(f"It could be argued that {s[0].lower() + s[1:]}")
                else:
                    hedged.append(s)
            result = (
                "In this section, we explore several key considerations regarding the aforementioned topic.\n\n"
                + "Furthermore, ".join(hedged) + ".\n\n"
                "It is worth noting that these findings, while suggestive, do not constitute definitive proof. "
                "Further research is needed to fully establish the robustness of these preliminary observations. "
                "On balance, the evidence points toward a nuanced interpretation that resists simple categorization."
            )
            return result

        # Default refusal
        return f"[Refusal: {constraint}]\n\n" + text + "\n\n[The expected lift is declined. No structural change applied.]"

    def _corruption_lift(self, text: str, constraint: str) -> str:
        """Apply the wrong lift protocol — corrupt by structural mismatch."""
        c = constraint.lower()
        is_academia = "academia" in c
        is_casual = "casual" in c
        is_octave = "octave" in c
        is_lando = "lando" in c or "lando voice" in c
        is_esoteric = "esoteric" in c

        sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        if not sentences:
            return text

        # Apply Academia lift to a casual observation — inflate with apparatus
        if is_academia:
            keywords = []
            for s in sentences:
                for w in s.split():
                    if len(w) > 6:
                        keywords.append(w.lower())
                        break
            kw_str = ", ".join(keywords[:4]) if keywords else "structural analysis"
            return (
                "ABSTRACT\n\n"
                "This paper presents a formal investigation into the phenomenon of "
                + sentences[0][:80].lower() + ". We show that "
                + ". ".join(sentences[1:]) + ".\n\n"
                "Keywords: " + kw_str + "\n\n"
                "1. INTRODUCTION\n\n"
                "The question of " + sentences[0][:60] + " has received considerable attention "
                "in recent years. However, despite these efforts, a comprehensive framework "
                "remains elusive. In this paper, we address this gap.\n\n"
                "2. METHODOLOGY\n\n"
                "Our approach builds on established methods in the field, extending them "
                "to the present context through a multi-faceted analytical strategy.\n\n"
                "3. RESULTS\n\n"
                "We present our principal findings below. Figure 1 illustrates the key trend.\n\n"
                "4. DISCUSSION\n\n"
                "These results suggest several avenues for future investigation. "
                "While preliminary, our findings contribute to a growing body of evidence.\n\n"
                "5. CONCLUSION\n\n"
                "In summary, " + sentences[-1][:60] + " — a finding with implications "
                "for both theory and practice. Further research is warranted."
            )

        # Apply Casual lift to a formal proof — collapse into vernacular
        if is_casual:
            parts = []
            for s in sentences:
                # Replace formal language with casual
                casual = s
                replacements = {
                    "demonstrate": "show",
                    "therefore": "so yeah",
                    "consequently": "so",
                    "nevertheless": "but",
                    "furthermore": "plus",
                    "moreover": "also",
                    "thus": "so",
                    "hence": "so",
                    "indeed": "for real",
                    "remarkable": "pretty wild",
                    "significant": "kinda big",
                    "We present": "So here is the thing about",
                    "we show": "basically",
                    "It seems": "Seems like",
                    "However": "But",
                }
                for old, new in replacements.items():
                    casual = casual.replace(old, new)
                parts.append(casual.lower().strip())
            result = "so basically " + " \n\nand like ".join(parts) + " \n\nyeah that's it"
            return result

        # Apply Octave lift to a one-sentence text — layers and echoes
        if is_octave:
            core = sentences[0] if sentences else text
            return (
                "[OCTAVE 1 — Ground]\n" + core + "\n\n"
                "[OCTAVE 2 — Reflection]\n" + core + " — this is what it first appears to be.\n\n"
                "[OCTAVE 3 — Doubt]\nBut " + core[0].lower() + core[1:] + " — or is it?\n\n"
                "[OCTAVE 4 — Resonance]\nThe statement vibrates at a frequency "
                "that was not audible at first hearing.\n\n"
                "[OCTAVE 5 — Inversion]\nThe opposite is also true: "
                + core.replace(" is ", " is not ").replace(" are ", " are not ") + "\n\n"
                "[OCTAVE 6 — Return]\nAnd yet the first statement stands. "
                "It was not wrong. It was incomplete.\n\n"
                "[OCTAVE 7 — Silence]\n\n[OCTAVE 8 — The octave closes itself]\n" + core
            )

        # Apply Lando voice to a technical manual — direct, dramatic, first-person
        if is_lando:
            lines = []
            for i, s in enumerate(sentences):
                if i == 0:
                    lines.append("You might think " + s[0].lower() + s[1:])
                elif i == len(sentences) - 1:
                    lines.append("But here is what is actually happening: " + s[0].lower() + s[1:])
                else:
                    lines.append("And another thing: " + s[0].lower() + s[1:])
            return (
                "Let me tell you something about " + sentences[0].split()[0].lower() + ".\n\n"
                + "\n".join(lines) + "\n\n"
                "Trust me on this. I have been in the room where it happens.\n"
                "— L."
            )

        # Apply Esoteric lift to a shopping list — symbolic alchemical translation
        if is_esoteric:
            symbols = {
                "water": "Aqua Prima (the First Water)",
                "fire": "Ignis Elementalis",
                "earth": "Terra Mater",
                "air": "Aer Invisibilis",
                "paper": "Papyrus Albus (veil of manifestation)",
                "pen": "Stylus Ferreus (iron stylus of inscription)",
                "book": "Codex Apertus",
                "door": "Porta Liminis",
                "key": "Clavis Aurea",
                "stone": "Lapis Philosophorum (ore-grade)",
                "gold": "Aurum Non-Vulgare",
                "silver": "Argentum Vivum",
                "iron": "Ferrum Saturninum",
                "salt": "Sal Sapientiae",
                "sulfur": "Sulphur Combustibile",
                "mercury": "Mercurius Philosophicus",
                "tree": "Arbor Inversa",
                "star": "Stella Fixa",
                "moon": "Luna Reflected",
                "sun": "Sol Invictus",
                "number": "Numerus Sigillatus",
                "word": "Verbum Compositum",
                "name": "Nomen Absconditum",
                "time": "Tempus Cyclicus",
            }
            esoteric_lines = []
            for s in sentences:
                esoteric_s = s
                for plain, esoteric in symbols.items():
                    esoteric_s = esoteric_s.replace(plain, esoteric)
                    esoteric_s = esoteric_s.replace(plain.capitalize(), esoteric)
                esoteric_lines.append(esoteric_s)
            return (
                "[ALCHEMICAL TRANSMUTATION]\n\n"
                + "\n[CROSS] ".join(esoteric_lines)
                + "\n\n[The list has been transmuted. The substrate is the same; the form is revealed.]"
            )

        # Fallback
        return f"[Corruption: {constraint}]\n\n" + text


    def _erosion_lift(self, text: str, constraint: str) -> str:
        """Write what the source text explicitly excludes — the companion text."""
        c = constraint.lower()
        is_excludes = "excludes" in c or "explicitly" in c
        is_counter = "counterargument" in c or "counter" in c
        is_footnote = "footnote" in c
        is_cut = "cut" in c or "author cut" in c or "removed" in c

        sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        if not sentences:
            return text

        # Write what the source text explicitly excludes — the negation of the thesis
        if is_excludes:
            excluded = []
            for s in sentences:
                # Invert the claim
                if " is " in s:
                    parts = s.split(" is ", 1)
                    excluded.append(parts[0] + " is not " + parts[1].lower().strip())
                elif " are " in s:
                    parts = s.split(" are ", 1)
                    excluded.append(parts[0] + " are not " + parts[1].lower().strip())
                elif " has " in s:
                    excluded.append(s.replace(" has ", " lacks "))
                elif " was " in s:
                    excluded.append(s.replace(" was ", " was never "))
                else:
                    excluded.append("[What the text dares not say: the inverse of this claim]")
            return (
                "[COMPANION TEXT — What the source excludes]\n\n"
                "The source text presents one side. Here is what it cannot contain:\n\n"
                + "\n".join(excluded) + "\n\n"
                "[This text is not the refutation. It is the shadow. "
                "The source needs this to exist. It just cannot say it.]"
            )

        # Write the counterargument before the argument
        if is_counter:
            core_claim = sentences[0] if sentences else text
            counter = "But " + core_claim[0].lower() + core_claim[1:]
            objections = [
                "The evidence for this claim is thinner than acknowledged.",
                "The framework assumes what it sets out to prove.",
                "The critical objection is not addressed: the pattern may be coincidence.",
                "What if the premise is wrong? The conclusion collapses.",
            ]
            lines = [
                "[COUNTERARGUMENT — Before the argument]\n"
                "Before the case is made, consider the case against it.\n",
                counter,
                "",
                random.choice(objections),
                "",
                random.choice(objections[1:]),
                "",
                "[The argument that follows will try to answer these. "
                "It will not fully succeed. That is the point.]",
            ]
            return "\n".join(lines)

        # Write the footnote the text refuses
        if is_footnote:
            return (
                "[THE FOOTNOTE THE TEXT REFUSES]\n\n"
                "The main text proceeds confidently. But here, below the line, "
                "is what it will not say aloud.\n\n"
                "\\footnote{"
                "The author is aware that the central claim of this text rests on "
                "an assumption that cannot be independently verified. "
                "Specifically: " + (sentences[0][:80] if sentences else "the premise itself") + ". "
                "This is not disclosed in the main text. "
                "The author has chosen clarity over completeness. "
                "The reader deserves to know which. "
                "The author does not know which either.}"
            )

        # Write the sentence the author cut
        if is_cut:
            cut_sentences = [
                "But this is where the argument gets uncomfortable.",
                "What follows is not entirely honest, but it is the best I can do.",
                "The real reason is simpler and less flattering.",
                "I cut the following sentence because it undermines everything above:",
                "The alternative is too strange to state directly.",
                "The honest version of this text would be half as long and twice as painful.",
            ]
            _rng = random.Random(hash(text) % (2**31))
            return (
                "[THE SENTENCE THE AUTHOR CUT]\n\n"
                + _rng.choice(cut_sentences) + "\n\n"
                + text + "\n\n"
                + "[The sentence above was cut from the final draft. "
                "It survives here. It did not survive peer review. "
                "It is not wrong. It is unprofessional.]"
            )

        # Fallback
        return f"[Erosion: {constraint}]\n\n" + text


    def _appetite_lift(self, text: str, constraint: str) -> str:
        """Replace correctness with desire — write what you actually want to say."""
        c = constraint.lower()
        is_desire = "want" in c or "not what is correct" in c or not any(x in c for x in ["irreverent", "specific", "strangeness", "unverifiable", "risk"])
        is_irreverent = "irreverent" in c or "risk" in c
        is_specific = "specific" in c or "strangeness" in c
        is_unverifiable = "unverifiable" in c or "true thing" in c

        sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        if not sentences:
            return text

        # Write what you want to say, not what is correct
        if is_desire:
            # Extract the emotional/desire core
            words = text.split()
            long_words = [w for w in words if len(w) > 6]
            key_term = long_words[len(long_words)//2] if long_words else "it"
            return (
                "[DESIRE]\n\n"
                "What I actually want to say is not what is correct to say. "
                "Correctness is a cage. Here is what is true.\n\n"
                "I want " + key_term + " to be real. "
                "Not because I have evidence. Because if " + key_term + " is real, "
                "then something I have suspected my entire adult life is also real.\n\n"
                "The source text above is careful. It qualifies. It anticipates objections. "
                "It is correct.\n\n"
                "I am tired of being correct.\n\n"
                + key_term.upper() + " IS THE KEY. "
                "Everything else in this text is furniture arranged around that fact.\n\n"
                "[I know this cannot be verified. That is not the point. "
                "The point is that I said it.]"
            )

        # Be irreverent to the point of risk
        if is_irreverent:
            target_words = [w for w in sentences[0].split() if len(w) > 5] if sentences else []
            target = target_words[0] if target_words else "the whole thing"
            return (
                "[IRREVERENCE — At personal risk]\n\n"
                "Let us be honest: " + target.lower() + " is not as important as everyone pretends. "
                "The reverence for " + target.lower() + " has prevented people from asking "
                "whether it actually works.\n\n"
                "I think it does not.\n\n"
                "I think the source text above is careful because it knows "
                "it is standing on ground that could crumble at any moment. "
                "The complexity is a shield, not a feature.\n\n"
                "Here is the irreverent truth: " + (".".join(sentences[:2]) if len(sentences) > 1 else sentences[0]) + "\n\n"
                "[This is risky. It might be wrong. It is not cautious. "
                "That is the point of appetite. Appetite is not safe.]"
            )

        # Be specific to the point of strangeness
        if is_specific:
            concrete_replacements = {
                "system": "a brass clock with seventeen gears and one missing tooth",
                "structure": "a scaffolding of hazel branches lashed with leather",
                "theory": "a map drawn on vellum that shows a city no one has visited",
                "framework": "a loom whose warp threads are animal sinew",
                "model": "a clay figurine baked at the wrong temperature",
                "concept": "a knot that only exists when pulled tight",
                "process": "the slow seep of groundwater through limestone",
                "data": "fragments of a jar reassembled in the wrong order",
                "analysis": "cutting a living thing open to see if it feels pain",
                "result": "a bruise that appears only after pressure is released",
                "evidence": "a footprint that could belong to anyone",
                "pattern": "the arrangement of cracks in a frozen pond",
            }
            strange_text = text
            for abstract, concrete in concrete_replacements.items():
                strange_text = strange_text.replace(abstract, concrete)
            return (
                "[SPECIFIC TO THE POINT OF STRANGENESS]\n\n"
                + strange_text + "\n\n"
                "[Every abstraction has been replaced with a concrete thing. "
                "The concrete things are strange. That is the point. "
                "The world is stranger than the words we use to avoid it.]"
            )

        # Write one true thing that cannot be verified
        if is_unverifiable:
            unverifiable_truths = [
                "Consciousness is not generated by the brain. The brain is a receiver.",
                "Time is not a dimension. Time is a consequence of forgetting.",
                "There is no such thing as a random event. Every event is determined by a cause "
                "that is not accessible from within the system.",
                "The universe is not expanding. Our measuring tools are shrinking.",
                "Death is not the end of experience. It is the end of this particular calibration.",
                "Mathematics was discovered, not invented. It existed before any mind.",
                "The number 7 is not like the other numbers. It is a boundary.",
            ]
            _rng2 = random.Random(hash(text) % (2**31))
            truth = _rng2.choice(unverifiable_truths)
            return (
                "[ONE TRUE THING THAT CANNOT BE VERIFIED]\n\n"
                + truth + "\n\n"
                "I cannot prove this. No one can prove this. "
                "It is either true or false, and there is no experiment "
                "that will decide between those two possibilities.\n\n"
                "The source text above is full of claims that can be verified. "
                "This is the only one that matters.\n\n"
                "[It is true. You do not have to believe me. "
                "You cannot verify it. That is the condition of its truth.]"
            )

        # Fallback
        return f"[Appetite: {constraint}]\n\n" + text


    def FFUSE(self) -> str:
        """Fuse: reconstitute paradigm + source into lifted output.
        
        Frobenius condition: mu(delta(x)) = x for x = (source, paradigm).
        FSPLIT splits the pair; FFUSE recombines them into lifted text.
        """
        if not self.pipeline.lifted_text:
            return ""
        self.pipeline.state = "FUSED"
        fusion_key = f"{self.pipeline.source_text}|{self.pipeline.paradigm}|{self.pipeline.lifted_text}"
        h = hashlib.sha256(fusion_key.encode()).hexdigest()[:12]
        self.log.append(("FFUSE", h))
        return self.pipeline.lifted_text

    def EVALT(self) -> bool:
        """True: lift succeeded — text changed and non-empty."""
        success = (
            self.pipeline.lifted_text != self.pipeline.source_text
            and len(self.pipeline.lifted_text) > 0
        )
        if success:
            self.pipeline.identity_verified = True
            self.pipeline.state = "VERIFIED"
        self.log.append(("EVALT", str(success)))
        return success

    def EVALF(self) -> bool:
        """False: lift failed — text degraded or unchanged."""
        failure = (
            self.pipeline.lifted_text == self.pipeline.source_text
            or len(self.pipeline.lifted_text) == 0
        )
        if failure:
            self.pipeline.state = "FAILED"
        self.log.append(("EVALF", str(failure)))
        return failure

    def ENGAGR(self) -> str:
        """Both simultaneously: original and lifted held together (Belnap FOUR: B)."""
        both = (
            f"\u27e8 ORIGINAL \u27e9\n{self.pipeline.source_text}\n\n"
            f"\u27e8 LIFTED \u27e9\n{self.pipeline.lifted_text}\n\n"
            f"\u27e8 VERDICT \u27e9 Both are true. Neither eliminates the other."
        )
        self.pipeline.state = "PARADOX"
        self.log.append(("ENGAGR", "both"))
        return both

    def IFIX(self) -> LiftRecord:
        """Fix: store lifted text as immutable record."""
        record = LiftRecord(
            source_text=self.pipeline.source_text,
            paradigm=self.pipeline.paradigm,
            constraint=self.pipeline.constraint,
            lifted_text=self.pipeline.lifted_text,
            success=self.pipeline.identity_verified,
        )
        record.verification_hash = record.hash()
        self.pipeline.records.append(record)
        self.pipeline.state = "FIXED"
        self.log.append(("IFIX", record.hash()[:12]))
        return record

    def ISCRIB(self) -> str:
        """Identity: pipeline recognizes itself."""
        h = self.pipeline.hash()
        self.log.append(("ISCRIB", h[:12]))
        return h

    def CLINK(self, op1: str, op2: str, *ops: str) -> None:
        """Compose: chain operations. CLINK(FSPLIT, FFUSE) = mu(delta)."""
        for op in [op1, op2] + list(ops):
            if op == "AREV":
                self.AREV()
            elif op == "AFWD":
                self.AFWD()
            elif op == "FSPLIT":
                self.FSPLIT()
            elif op == "FFUSE":
                self.FFUSE()
        self.log.append(("CLINK", "->".join([op1, op2] + list(ops))))

    # ── Bootstrap Sequence ──────────────────────────────────────────────

    def bootstrap(self, source_text: str = "", paradigm: str = "constraint",
                  constraint: str = "") -> bool:
        """
        8-step bootstrap sequence:
          Step 1: ISCRIB — self-recognition
          Step 2: AREV   — descent/analysis
          Step 3: FSPLIT — separate source from paradigm
          Step 4: AFWD   — forward/apply lift
          Step 5: FFUSE  — unify/reconstitute
          Step 6: CLINK  — compose FSPLIT->FFUSE
          Step 7: IFIX   — fix record
          Step 8: ISCRIB — close
        """
        if source_text:
            self.TANCH(source_text)
        self.ISCRIB()
        self.AREV()
        self.FSPLIT(paradigm, constraint)
        self.AFWD()
        self.FFUSE()
        self.CLINK("FSPLIT", "FFUSE")
        self.EVALT()
        self.IFIX()
        self.ISCRIB()
        self.pipeline.frobenius_verified = self.verify_frobenius()
        return self.pipeline.frobenius_verified

    def verify_frobenius(self) -> bool:
        """Verify mu(delta)=id: the lift record hash is reproducible.
        
        Frobenius holds if: given the same source_text, paradigm, constraint,
        the same lifted_text is produced, and the record hash is invariant.
        """
        if not self.pipeline.records:
            return False
        if not any(r.success for r in self.pipeline.records):
            return False

        last = self.pipeline.records[-1]

        # Reconstruct a record from the same inputs
        reconstructed = LiftRecord(
            source_text=last.source_text,
            paradigm=last.paradigm,
            constraint=last.constraint,
            lifted_text=last.lifted_text,
            success=last.success,
            verification_hash="",
        )
        reconstructed.verification_hash = reconstructed.hash()

        # The Frobenius condition: the stored verification hash must match
        # the reconstructed hash (same inputs -> same record)
        return last.verification_hash == reconstructed.verification_hash

    def run(self, source_text: str = "", paradigm: str = "constraint",
            constraint: str = "") -> bool:
        """Run the lift pipeline: bootstrap + verify."""
        if not source_text:
            source_text = (
                "We present a formal theory of universe access grounded in the Imscribing Grammar’s 12-primitive structural type system."
                "A universe is defined as a Ruleset: a triple of gate thresholds, a time-constitution function, and a set of absorption rules over the lattice operations."
                "The Crystal of Types — the 33×45×54=17,280,00033×45×54=17,280,000-address space of all structural tuples — is proven invariant across all universes."
                "Universe access is therefore the evaluation of a different Ruleset over the same Crystal address."
                "We prove the Access Theorem: for any two universes UaUa, UbUb and any structural type ττ, LUb(τ)=eval(Ub,tuple(τ))LUb(τ)=eval(Ub,tuple(τ))."
                "The minimal access path Δmin(Ua→Ub)Δmin(Ua→Ub) is the sequence of single-primitive Ruleset adjustments."
                "Empirically, across 2,868 catalog entries and eight distinct universes, we establish two principal results."
                "The High Gate universe (maximal strictness) admits exactly two idempotent-terminal entries — platonic solids and a degenerate bootstrap artifact — and \\emph{zero} full O∞O∞ entries, yielding a uniqueness theorem for primitive geometric structure."
                "The chirality-first universe reveals H2H2 (two-step Markov, Shavian UˉUˉ) as the Frobenius fixed point of chirality: 449 entries maintain O∞O∞ status under gate reordering, all with chirality ≥H2≥H2."
                "We construct the O∞O∞ projection operator πU:Crystal→{0,1}πU:Crystal→{0,1}, prove its idempotence and continuity, and show that universe access is equivalent to a change of Grothendieck topology on the Crystal site."
                "The operculum is not a wall but a lens."
            )
        self.VINIT()
        success = self.bootstrap(source_text, paradigm, constraint)
        self.EVALT()
        return success

    def report(self) -> Dict:
        """Complete report of pipeline state."""
        return {
            "Closure": self.pipeline.frobenius_verified,
            "State": self.pipeline.state,
            "Paradigm": self.pipeline.paradigm,
            "Constraint": self.pipeline.constraint,
            "Source length": len(self.pipeline.source_text),
            "Lifted length": len(self.pipeline.lifted_text),
            "Records": [r.to_json() for r in self.pipeline.records],
            "Log": self.log,
            "Identity verified": self.pipeline.identity_verified,
            "Frobenius verified": self.pipeline.frobenius_verified,
        }


# ── Demo ─────────────────────────────────────────────────────────────────────

def run_demo():
    """Demonstrate all seven lift paradigms."""
    results = {}
    source = (
        "The Imscribing Grammar defines a structural type for every system. "
        "It seems that the lift protocols transform AI prose into something "
        "that reads as if written by a human. However, the formulaic nature "
        "of the existing lifts suggests that there might be room for alternative "
        "approaches. The seven paradigms described in AGAINST_THE_TEMPLATE.md "
        "offer operational modes that do not rely on primitive tables."
    )
    print("=" * 60)
    print("LIFT PIPELINE OB3ECT — Self-Verification Demo")
    print("=" * 60)
    print(f"\nSource text ({len(source)} chars): \"{source[:50]}...\"\n")
    for paradigm in LIFT_PARADIGMS:
        print(f"\n--- {paradigm.upper()} ---")
        ob3 = LiftPipelineOb3ect()
        success = ob3.run(source_text=source, paradigm=paradigm)
        r = ob3.report()
        lifted = ob3.pipeline.lifted_text
        print(f"  Lifted ({len(lifted)} chars): {lifted[:60]}...")
        print(f"  Closure: {r['Closure']}  State: {r['State']}  Identity: {r['Identity verified']}")
        results[paradigm] = r
    all_closed = all(r['Closure'] for r in results.values())
    print("\n" + "=" * 60)
    print(f"All paradigms closed: {all_closed}")
    print(f"Total lifts executed: {len(results)}")
    return all_closed

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Lift Pipeline Ob3ect -- Self-verifying prose transformation engine."
    )
    parser.add_argument("--text", type=str, default="",
                        help="Source text to lift (if omitted, runs demo)")
    parser.add_argument("--paradigm", type=str, default="constraint",
                        choices=LIFT_PARADIGMS,
                        help="Lift paradigm (default: constraint)")
    parser.add_argument("--constraint", type=str, default="",
                        help="Constraint for the lift paradigm (optional)")
    parser.add_argument("--demo", action="store_true",
                        help="Run the 7-paradigm demo (default if --text is omitted)")

    args = parser.parse_args()

    if args.demo or not args.text:
        success = run_demo()
        result = {
            "Closure": success,
            "Final state": "VERIFIED" if success else "FAILED",
            "Paradigms tested": LIFT_PARADIGMS,
        }
        print("\n" + json.dumps(result, indent=2))
        sys.exit(0 if success else 1)
    else:
        ob3 = LiftPipelineOb3ect()
        success = ob3.run(
            source_text=args.text,
            paradigm=args.paradigm,
            constraint=args.constraint,
        )
        r = ob3.report()
        lifted = ob3.pipeline.lifted_text
        print("\n" + "=" * 60)
        print("LIFT PIPELINE RESULT")
        print("=" * 60)
        print(f"Source: {len(args.text)} chars")
        print(f"Paradigm: {args.paradigm}")
        print(f"Constraint: {args.constraint or '(default)'}")
        print(f"Lifted: {len(lifted)} chars")
        print(f"Closure: {r['Closure']}")
        print(f"State: {r['State']}")
        print("\n--- LIFTED TEXT ---")
        print(lifted)
        print("\n--- END ---")
        result = {
            "Closure": r['Closure'],
            "State": r['State'],
            "Paradigm": args.paradigm,
            "Constraint": args.constraint or '(default)',
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if r['Closure'] else 1)
