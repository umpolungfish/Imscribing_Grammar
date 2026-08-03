"""
Vocal imscription — catalog entry → WAV.

Reads the 12-primitive tuple of a named catalog entry and concatenates the
corresponding phoneme WAV files from vocal_sounds/ into a single imscription.

Primitive order: ⊢ ⊣ > < ƒ Ç Γ ɢ ⊙ Ħ Σ Ω
"""

import wave
import numpy as np
from pathlib import Path

PRIMITIVE_ORDER = ["⊢", "⊣", ">", "<", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]

# Glyph primary key → vocal_sounds/ subdirectory name
PRIM_DIR: dict[str, str] = {
    "⊢": "D", "⊣": "T", ">": "R", "<": "P",
    "⋈": "F", "⊤": "K", "∈": "G", "∋": "Gamma",
    "⊙": "Phi", "⊥": "H", "⊞": "S", "◻": "Omega",
}

# ── Pronunciation guide ────────────────────────────────────────────────────────
# Each entry: (ipa, short_hint, detail)
#   ipa        — IPA symbol(s)
#   short_hint — one-phrase English anchor, fits in ~40 chars
#   detail     — fuller articulatory description for learners
PRONUNCIATION_GUIDES: dict[str, tuple[str, str, str]] = {
    # ⊢ — Dimensionality
    "𐑛": (
        "/w/",
        "like 'w' in 'wet'",
        "Labial-velar approximant. Lips round and part; voice flows through freely with no friction.",
    ),
    "𐑨": (
        "/ɜː/",
        "like 'ur' in 'bird'",
        "Open-mid central unrounded vowel. Tongue sits in the middle of the mouth, no rounding — the 'er' of 'her' or 'fern'.",
    ),
    "𐑼": (
        "/ʊ/",
        "like 'oo' in 'foot'",
        "Near-close back rounded vowel. A short, relaxed 'oo' — not as high or tense as 'food'. Also the 'u' in 'put'.",
    ),
    "𐑦": (
        "/ɒ/",
        "like 'o' in 'hot' (British)",
        "Open back rounded vowel. Mouth wide open, back of tongue low, lips loosely rounded — British 'lot', 'cot'.",
    ),

    # ⊣ — Topology
    "𐑡": (
        "/ɳ/",
        "retroflex 'n' — tongue curled back",
        "Retroflex nasal. Curl the tongue tip back toward the hard palate (not touching the ridge), then nasal air flows. Common in Hindi, Dravidian languages.",
    ),
    "𐑰": (
        "/ɻ/",
        "American English 'r' in 'red'",
        "Retroflex approximant. Tongue tip curled back, no trill or friction — the default 'r' in American and Canadian English.",
    ),
    "𐑥": (
        "/ʘ/",
        "bilabial click — a sealed-lip pop",
        "Seal both lips completely. Lower the tongue body to rarefy the air between lips and mouth. Release both lips simultaneously for a muffled pop. Rarer than dental clicks; found in Khoisan languages.",
    ),
    "𐑶": (
        "/ʐ/",
        "retroflex 'zh' — tongue curled back",
        "Retroflex sibilant. Like the 'zh' in 'measure' or 's' in 'vision', but with the tongue tip curled back rather than flat. Common in Mandarin (zh/r), Polish (ż).",
    ),
    "𐑸": (
        "/ɔ/",
        "like 'aw' in 'saw'",
        "Open-mid back rounded vowel. Mouth fairly open, lips rounded, back of tongue raised slightly — the 'aw' in 'saw', 'thought', 'caught'.",
    ),

    # > — Relational mode
    "𐑩": (
        "/r/",
        "rolled 'r' — tongue flutters",
        "Alveolar trill. Tongue tip vibrates rapidly against the ridge behind the upper teeth — Spanish or Italian 'rr', Scottish 'r'. Not the English rhotic.",
    ),
    "𐑑": (
        "/ts/",
        "like 'ts' in 'cats'",
        "Alveolar affricate. A short stop at the ridge that releases directly into a hiss — 'ts' in 'cats', 'pizza', or German 'z' in 'Zeit'.",
    ),
    "𐑽": (
        "/a↘/",
        "falling 'ah' — pitch drops",
        "Open vowel with descending tone. The voice begins on a full open 'ah' and steps or glides downward in pitch — a tonal downstep marker used in many African languages.",
    ),
    "𐑾": (
        "/j/",
        "like 'y' in 'yes'",
        "Palatal approximant. Tongue body arches toward the hard palate without touching it — 'y' in 'yes', 'year'. In yogh (ȝ), the Middle English counterpart.",
    ),

    # < — Parity / Symmetry
    "𐑗": (
        "/æ/",
        "like 'a' in 'cat'",
        "Near-open front unrounded vowel. Jaw drops, tongue pushes forward and low — the 'a' in 'cat', 'trap', 'bad'.",
    ),
    "𐑿": (
        "/ʊ/",
        "like 'oo' in 'foot'",
        "Near-close back rounded vowel. Same as 𐑼 — short, relaxed 'oo'. Upsilon (υ) in Ancient Greek had this quality.",
    ),
    "𐑬": (
        "/ǀ/",
        "dental click — 'tsk tsk'",
        "Dental click. Press the tongue tip against the back of the upper teeth. Create suction by pulling the tongue body down and back. Release the front seal: the sharp ingressive burst is the click. The 'tsk' of disapproval in English.",
    ),
    "𐑯": (
        "/ə/",
        "schwa — 'uh' in 'about'",
        "Mid central vowel. Tongue and jaw at their resting neutral position, lips unrounded — the most common vowel in English, appearing in every unstressed syllable: 'a'bout, 'sof'a, 'bett'er.",
    ),
    "𐑹": (
        "/ʔts/",
        "glottal catch then sharp 'ts'",
        "Glottal stop followed immediately by an alveolar affricate. Throat closes with a hard catch ('uh-oh' quality), then releases straight into a hissed 'ts'. The Frobenius snap: two distinct articulatory gestures fused into one.",
    ),

    # ⋈ — Fidelity
    "ƒ^ì": (
        "/ɬ/",
        "Welsh 'll' in 'Llanfair'",
        "Voiceless lateral fricative. Tongue tip touches the ridge behind the upper teeth (as for 'l'), but instead of voicing, air is forced over both sides of the tongue with friction — the 'll' in Welsh place names.",
    ),
    "ƒ^ð": (
        "/ð/",
        "like 'th' in 'this'",
        "Voiced dental fricative. Tongue tip between or just behind the upper teeth, voice on — 'th' in 'this', 'the', 'there'. Contrast with voiceless /θ/ in 'think'.",
    ),
    "ƒ^ż": (
        "/ʔ/",
        "glottal stop — 'uh-oh' catch",
        "Glottal stop. The vocal folds close completely, briefly halting all airflow, then release. The pause between the two syllables of 'uh-oh', or the Cockney replacement for 't' in 'bu'er' (butter).",
    ),

    # ⊤ — Kinetics
    "Ç^-": (
        "/ɣ/",
        "Spanish 'g' in 'agua'",
        "Voiced velar fricative. The back of the tongue approaches but does not touch the velum, and voice flows through with friction — the softened 'g' between vowels in Spanish 'agua', 'amigo'. A voiced version of the Scottish 'ch' in 'loch'.",
    ),
    "Ç^W": (
        "/ɯ/",
        "back 'oo' with spread lips",
        "Close back unrounded vowel. Like the 'oo' in 'food' but with lips completely flat and spread — the opposite of rounding. Common in Korean (으), Turkish (ı), Japanese (u in many contexts).",
    ),
    "Ç^@": (
        "/ə/",
        "schwa — 'uh' resting vowel",
        "Mid central vowel. The vocal tract at rest — tongue mid-height, mid-front-back, lips neutral. The default reduced vowel in English: 'a'bout, 'comm'a, 'bett'er. The acoustic center of gravity.",
    ),
    "Ç^Ù": (
        "/tʃ/",
        "like 'ch' in 'church'",
        "Voiceless palato-alveolar affricate. Tongue tip at the ridge behind the upper teeth, releasing into a 'sh'-like hiss — 'ch' in 'church', 'cheese', 'chair'.",
    ),
    "Ç^λ": (
        "/l/",
        "like 'l' in 'light'",
        "Alveolar lateral approximant. Tongue tip touches the ridge behind the upper teeth; voice flows around the sides of the tongue. The classical 'l' — clear before vowels, dark ('dark l') before consonants.",
    ),

    # Γ — Scope
    "𐑚": (
        "/β/",
        "bilabial 'v' — lips buzzing",
        "Voiced bilabial fricative. Both lips brought close together but not fully touching; voice and air flow between them with friction. Like a very relaxed 'b', or the 'v' sound made entirely with the lips (no teeth). Heard in Spanish 'b/v' between vowels.",
    ),
    "𐑔": (
        "/ɣ/",
        "Spanish 'g' in 'agua'",
        "Voiced velar fricative. Same as Ç^- — back of tongue near but not touching the velum, voice flowing through with turbulence. Greek γ, Dutch 'g', Arabic غ.",
    ),
    "𐑲": (
        "/ʔ/",
        "glottal stop — 'uh-oh' catch",
        "Glottal stop. Same as ƒ^ż — complete closure of the vocal folds, a hard catch, then release. The IPA symbol ʔ is derived from the reversed apostrophe, and aleph (א) in Semitic alphabets represents this sound.",
    ),

    # ∋ — Interaction grammar
    "ɢ^∧": (
        "/k/",
        "like 'k' in 'key'",
        "Voiceless velar stop. Back of tongue presses against the velum, air pressure builds, then releases abruptly with no voice — 'k' in 'key', 'cat', 'back'.",
    ),
    "ɢ^˝": (
        "/r…r/",
        "alternating rolled 'r'",
        "Repeated alveolar trill. Two rapid tongue-tip flutters in sequence, separated by a brief voiced interval — the oscillation of an alternating path.",
    ),
    "ɢ^ˌ": (
        "/ə/",
        "weak schwa — unstressed beat",
        "Mid central vowel at secondary stress. The same neutral 'uh' as Ç^@, but positioned at the lighter of two stress beats — the secondary pulse in a compound word or polysyllabic sequence.",
    ),
    "ɢ^Ş": (
        "/aː/",
        "long open 'aah'",
        "Long open vowel. Mouth fully open, tongue low, voice sustained — 'aah' said at full volume and held. The sound of broadcast: maximum acoustic projection.",
    ),

    # ⊙ — Criticality
    "𐑢": (
        "/j/",
        "like 'y' in 'yes'",
        "Palatal approximant. Same articulation as 𐑾 — tongue body toward hard palate, no friction, voice flows. In Slavic languages the soft sign (ь) marks palatalization of the preceding consonant, and /j/ is its onset gesture.",
    ),
    "⊙": (
        "/c/",
        "palatal stop — 'ky' as one sound",
        "Voiceless palatal stop. Like saying 'k' but with the tongue pressing the hard palate rather than the velum — further forward in the mouth. Hungarian 'ty', the 'k' in 'key' pushed to its extreme. The critical point: a single sharp closure at the palate.",
    ),
    "𐑮": (
        "/ɞ/",
        "rounded schwa — 'uh' with pursed lips",
        "Close-mid central rounded vowel. The schwa (ə) but with lips rounded as for 'o' — imagine saying 'uh' while pursing your lips. A rare vowel with no common English equivalent; heard in some Norwegian and Swedish dialects.",
    ),
    "𐑻": (
        "/ɛ/",
        "like 'e' in 'bed'",
        "Open-mid front unrounded vowel. Jaw open, tongue forward and mid-low — 'e' in 'bed', 'pet', 'red'. The reversed epsilon (ɛ) looks like a backwards 3, opening leftward.",
    ),
    "𐑣": (
        "/aː/",
        "long open 'aah' — rising or sustained",
        "Long open vowel, same acoustic quality as ɢ^Ş. Here the connotation is supercritical: the voice is at full aperture, sustained or rising — past the threshold into the runaway state.",
    ),

    # ⊥ — Chirality
    "𐑓": (
        "/o/",
        "pure 'o' as in French 'eau'",
        "Close-mid back rounded vowel. A pure, monophthong 'o' with no glide — the 'o' in French 'eau', Spanish 'no', or Italian 'solo'. English 'go' adds a glide (→ /oʊ/); this is the clean single vowel.",
    ),
    "𐑒": (
        "/a/",
        "short open 'ah'",
        "Open front vowel. Mouth wide, tongue low and forward — 'a' in Italian 'padre', Spanish 'casa', or 'ah' in a doctor's exam. Shorter and brighter than the back /ɑː/.",
    ),
    "𐑖": (
        "/ʒ/",
        "like 's' in 'measure'",
        "Voiced palato-alveolar fricative. The voiced counterpart of 'sh' — 's' in 'measure', 'g' in 'beige', 'j' in French 'jour'. A soft, buzzing hiss with voice.",
    ),
    "𐑫": (
        "/ɑː/",
        "long deep 'aah' — 'father'",
        "Long open back unrounded vowel. Mouth wide open, tongue low and pushed back, lips unrounded — 'a' in 'father', 'palm', 'spa' (British). Deeper and further back than /a/. The inverted script-a (ɑ) represents this open, unrestricted quality.",
    ),

    # Σ — Stoichiometry
    "𐑙": (
        "/ɧ/",
        "Swedish 'sj' — hushed double friction",
        "Simultaneous palatal and velar fricative (the Swedish sj-sound). Two places of constriction at once: the tongue front near the hard palate AND the tongue back near the velum. A wide, breathy hushing sound — 'sjö' (lake), 'skjorta' (shirt). Unique to Swedish phonology.",
    ),
    "𐑕": (
        "/n/",
        "like 'n' in 'no'",
        "Alveolar nasal. Tongue tip seals the ridge behind the upper teeth; soft palate lowers; voice resonates through the nasal cavity. The plain 'n' of every language.",
    ),
    "𐑳": (
        "/ɱ/",
        "labiodental 'n' — teeth-lip hum",
        "Labiodental nasal. Lower lip touches upper teeth (as for 'f' or 'v'), soft palate down, voice hums through the nose. The 'm' in 'triumph', 'circumvent', 'comfort' — the nasal that assimilates to a following /f/ or /v/.",
    ),

    # Ω — Topological invariant
    "𐑷": (
        "/e/",
        "pure 'e' as in French 'été'",
        "Close-mid front unrounded vowel. A pure, tense 'e' with no glide — French 'é', Spanish 'mesa', German 'See'. The English 'e' in 'they' adds a glide (→ /eɪ/); this is the clean monophthong.",
    ),
    "𐑴": (
        "/ø/",
        "German 'ö' — round lips, say 'e'",
        "Close-mid front rounded vowel. Round your lips as if to say 'o', then say 'e' — the result is 'ö'. French 'feu', 'bleu'; German 'schön', 'zwölf'. No native English equivalent.",
    ),
    "𐑭": (
        "/dz/",
        "like 'ds' in 'adds'",
        "Voiced alveolar affricate. A 'd' that releases into a 'z' — 'ds' in 'adds', 'ids'; Italian 'z' in 'zero', 'pizza' (in some dialects). The voiced counterpart of /ts/.",
    ),
    "𐑟": (
        "/ɐ/",
        "near-open central 'uh'",
        "Near-open central vowel. Slightly more open and central than the schwa — a relaxed 'uh' where the jaw drops just a little further. Common in German 'besser' (final syllable), and in unstressed syllables across many languages.",
    ),
}

_SOUNDS_DIR = Path(__file__).resolve().parent.parent / "vocal_sounds"


def _load_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0
    return samples, sr


def _silence(sr: int, ms: int) -> np.ndarray:
    return np.zeros(int(sr * ms / 1000), dtype=np.float32)


def make_imscription(
    entry: dict,
    sounds_dir: Path = _SOUNDS_DIR,
    gap_ms: int = 120,
) -> tuple[np.ndarray, int]:
    """
    Concatenate the phoneme sounds for a catalog entry in primitive order.
    Returns (float32 samples, sample_rate).
    Raises FileNotFoundError if any sound file is missing.
    """
    chunks: list[np.ndarray] = []
    sr: int | None = None
    missing: list[str] = []

    for primitive in PRIMITIVE_ORDER:
        value = entry.get(primitive)
        if not value:
            continue
        wav_path = sounds_dir / PRIM_DIR[primitive] / f"{value}.wav"
        if not wav_path.exists():
            missing.append(f"{primitive}={value} ({wav_path})")
            continue
        samples, file_sr = _load_wav(wav_path)
        if sr is None:
            sr = file_sr
        chunks.append(samples)
        chunks.append(_silence(sr, gap_ms))

    if missing:
        raise FileNotFoundError(
            "Missing sound files (run: uv run generate_vocal_expressions.py):\n"
            + "\n".join(f"  {m}" for m in missing)
        )
    if not chunks:
        raise ValueError("Entry has no recognisable primitive values.")

    combined = np.concatenate(chunks)
    return combined, sr


def save_wav(samples: np.ndarray, sr: int, path: Path) -> None:
    samples_int = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(samples_int.tobytes())
