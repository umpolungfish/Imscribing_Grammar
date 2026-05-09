#!/usr/bin/env python3
"""
Vocal Expression Generator — each file IS the IPA phoneme the subscript symbol represents.

Synthesis methods:
  [[SAMPA]]          espeak-ng phoneme notation, optional voice override
  CLICK:dental       programmatic dental click /ǀ/ (tsk)
  CLICK:bilabial     programmatic bilabial click /ʘ/
"""

import subprocess
import argparse
import wave
import struct
from pathlib import Path

import numpy as np

SR = 22050  # sample rate for all files (matches espeak-ng default)


def _bandpass_noise(rng: np.random.Generator, n: int,
                    center_hz: float, bandwidth_hz: float) -> np.ndarray:
    """White noise filtered to a Gaussian band around center_hz."""
    white = rng.standard_normal(n)
    spectrum = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    envelope = np.exp(-((freqs - center_hz) ** 2) / (2.0 * bandwidth_hz ** 2))
    filtered = np.fft.irfft(spectrum * envelope, n=n)
    # normalise to unit RMS
    rms = np.sqrt(np.mean(filtered ** 2))
    return filtered / rms if rms > 1e-9 else filtered


def generate_click(path: Path, click_type: str) -> None:
    """
    Synthesise a click consonant.

    Model: ingressive stop = sub-ambient rarefaction → abrupt release → damped resonance.
    The release is the perceptually dominant event: a short transient burst whose
    spectral centre frequency distinguishes click types.

      dental   /ǀ/  — tongue tip on upper teeth, high-frequency release (~4 kHz)
      bilabial /ʘ/  — lip closure, lower-frequency release (~1.5 kHz)

    The noise component is bandpass-filtered so each click sits in its true register
    (white noise would push both centroids toward Nyquist regardless of carrier).

    Structure per file:
      1. Pre-click silence  (50 ms) — simulates the closure phase
      2. Impulse burst      — Gaussian onset envelope × (damped sinusoid + bandlimited noise)
      3. Post-burst silence (100 ms)
    """
    rng = np.random.default_rng(42)

    if click_type == "dental":
        center_hz   = 4200.0   # dominant resonance
        bandwidth_hz = 1800.0  # noise band half-width (1-sigma)
        burst_ms    = 10.0     # Gaussian onset sigma
        decay_ms    = 14.0     # sinusoid exponential decay
        noise_ratio = 0.45
        amplitude   = 0.88
    elif click_type == "bilabial":
        center_hz   = 1500.0
        bandwidth_hz = 700.0
        burst_ms    = 16.0
        decay_ms    = 22.0
        noise_ratio = 0.55
        amplitude   = 0.72
    else:
        raise ValueError(f"Unknown click type: {click_type}")

    pre_silence_s  = 0.050
    post_silence_s = 0.100
    burst_window_s = 0.060

    total_s = pre_silence_s + burst_window_s + post_silence_s
    n_total = int(SR * total_s)
    signal  = np.zeros(n_total)

    n_burst = int(SR * burst_window_s)
    t_burst = np.arange(n_burst) / SR

    tau      = decay_ms / 1000.0
    decay    = np.exp(-t_burst / tau)
    sinusoid = np.sin(2 * np.pi * center_hz * t_burst) * decay

    # Bandlimited noise — confined to the same spectral region as the carrier
    noise = _bandpass_noise(rng, n_burst, center_hz, bandwidth_hz) * decay

    sigma_s   = burst_ms / 1000.0 / 3.0
    onset_env = np.exp(-(t_burst / sigma_s) ** 2)

    burst = ((1 - noise_ratio) * sinusoid + noise_ratio * noise) * onset_env

    start = int(SR * pre_silence_s)
    end   = start + n_burst
    signal[start:end] = burst[:end - start]

    peak = np.max(np.abs(signal))
    if peak > 1e-9:
        signal = signal / peak * amplitude

    samples = (signal * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(samples.tobytes())


def synthesize_espeak(phoneme: str, path: Path,
                      voice: str, pitch: int, speed: int) -> bool:
    cmd = ["espeak-ng", "-v", voice, "-p", str(pitch), "-s", str(speed),
           "-w", str(path), phoneme]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}")
        return False
    return True


# (primitive, key, method, ipa_gloss, voice_override_or_None)
# method is either "[[SAMPA]]" or "CLICK:type"
ENTRIES: list[tuple[str, str, str, str, str | None]] = [
    # D — Dimensionality
    ("D", "Ð_ß",         "[[w]]",        "/w/ labial-velar approximant",          None),
    ("D", "Ð_turnthree",    "[[3:]]",        "/ɜː/ open-mid central",                None),
    ("D", "Ð_invomega",     "[[U]]",         "/ʊ/ near-close back rounded",          None),
    ("D", "Ð_omega",        "[[Q]]",         "/ɒ/ open back rounded",                None),

    # T — Topology
    ("T", "Þ_nrleg",        "[[n.]]",        "/ɳ/ retroflex nasal",                  None),
    ("T", "Þ_invscr",       "[[r.]]",        "/ɻ/ retroflex approximant",            None),
    # bilabial click /ʘ/ — programmatically generated
    ("T", "Þ_bullseye",     "CLICK:bilabial","/ʘ/ bilabial click",                   None),
    ("T", "Þ_commatailz",   "[[z.]]",        "/ʐ/ retroflex sibilant",               None),
    ("T", "Þ_openo",        "[[O]]",         "/ɔ/ open-mid back rounded",            None),

    # R — Relational mode
    ("R", "Ř_subrightarrow","[[r]]",         "/r/ alveolar trill",                   None),
    ("R", "Ř_ctz",          "[[ts]]",        "/ts/ alveolar affricate",              None),
    ("R", "Ř_downstep",     "[[a2]]",        "/a/ falling tone",                     None),
    ("R", "Ř_lyoghlig",     "[[j]]",         "/j/ palatal approximant (yogh)",       None),

    # P — Parity / Symmetry
    ("P", "Φ_aolig",        "[[{]]",         "/æ/ near-open front unrounded",        None),
    ("P", "Φ_upsilon",      "[[U]]",         "/ʊ/ near-close back rounded",          None),
    # dental click /ǀ/ — programmatically generated
    ("P", "Φ_pipevar",      "CLICK:dental",  "/ǀ/ dental click",                     None),
    ("P", "Φ_subdoublearrow","[[@]]",        "/ə/ schwa",                            None),
    ("P", "Φ_doublebarpipe","[[? ts]]",      "/ʔts/ Frobenius glottal + affricate",  None),

    # F — Fidelity
    ("F", "ƒ_beltl",        "[[K]]",         "/ɬ/ voiceless lateral fricative",      None),
    ("F", "ƒ_dh",           "[[D]]",         "/ð/ voiced dental fricative",          None),
    ("F", "ƒ_hardsign",     "[[?]]",         "/ʔ/ glottal stop",                     None),

    # K — Kinetics
    # /ɣ/ voiced velar fricative — Spanish voice has [[Q]] = /ɣ/
    ("K", "Ç_frtailgamma",  "[[Q]]",         "/ɣ/ voiced velar fricative",           "es"),
    # /ɯ/ close back unrounded — Korean voice [[u-]] = /ɯ/
    ("K", "Ç_turnm",        "[[u-]]",        "/ɯ/ close back unrounded",             "ko"),
    ("K", "Ç_schwa",        "[[@]]",         "/ə/ mid central vowel",                None),
    ("K", "Ç_teshlig",      "[[tS]]",        "/tʃ/ palato-alveolar affricate",       None),
    ("K", "Ç_lambda",       "[[l]]",         "/l/ alveolar lateral approximant",     None),

    # G — Scope
    ("G", "Γ_β",         "[[B]]",         "/β/ voiced bilabial fricative",        None),
    # /ɣ/ — Spanish voice
    ("G", "Γ_γ",        "[[Q]]",         "/ɣ/ voiced velar fricative",           "es"),
    ("G", "Γ_revapostrophe","[[?]]",         "/ʔ/ glottal stop",                     None),

    # Gamma — Interaction grammar
    ("Gamma", "ɢ_corner",        "[[k]]", "/k/ velar stop",                      None),
    ("Gamma", "ɢ_spleftarrow",   "[[r r]]","/r r/ alternating rhotic",           None),
    ("Gamma", "ɢ_secstress",     "[[@]]", "/ə/ secondary stress schwa",          None),
    ("Gamma", "ɢ_doublevertline","[[a:]]","/aː/ open broadcast vowel",           None),

    # Phi — Criticality
    ("Phi", "φ̂_ž",        "[[j]]",   "/j/ palatalization",                  None),
    ("Phi", "φ̂_ctyogh",          "[[c]]",   "/c/ voiceless palatal stop",          None),
    ("Phi", "φ̂_Æ", "[[@]]",   "/ɞ/ close-mid central (approx /ə/)",  None),
    ("Phi", "φ̂_3",      "[[E]]",   "/ɛ/ open-mid front unrounded",        None),
    ("Phi", "φ̂_Ţ",          "[[a:]]",  "/aː/ open vowel (supercritical)",     None),

    # H — Temporal depth
    ("H", "Ħ_closeomega",      "[[o]]",       "/o/ close-mid back rounded",          None),
    ("H", "Ħ_toneletterstem",  "[[a]]",       "/a/ open front",                      None),
    ("H", "Ħ_turntwo",         "[[Z]]",       "/ʒ/ voiced palato-alveolar fricative",None),
    ("H", "Ħ_invscripta",      "[[A:]]",      "/ɑː/ open back unrounded",            None),

    # S — Stoichiometry
    # /ɧ/ Swedish sj-sound — Swedish voice [[sx]] ≈ /ɧ/
    ("S", "Σ_doublebaresh",    "[[sx]]",      "/ɧ/ sj-sound (Swedish voice)",        "sv"),
    ("S", "Σ_ctn",             "[[n]]",       "/n/ alveolar nasal",                  None),
    ("S", "Σ_ltailm",          "[[F]]",       "/ɱ/ labiodental nasal",               None),

    # Omega — Topological invariant
    ("Omega", "Ω_Å","[[e]]",   "/e/ close-mid front unrounded",       None),
    ("Omega", "Ω_crtwo",       "[[2]]",   "/ø/ close-mid front rounded",         None),
    ("Omega", "Ω_dzlig",       "[[dz]]",  "/dz/ voiced alveolar affricate",      None),
    ("Omega", "Ω_turna",       "[[6]]",   "/ɐ/ near-open central",               None),
]


def main():
    parser = argparse.ArgumentParser(
        description="Generate IPA phoneme audio for all 49 phonetic subscripts")
    parser.add_argument("--output-dir", type=Path, default=Path("vocal_sounds"))
    parser.add_argument("--voice",   default="en",  help="Default espeak-ng voice")
    parser.add_argument("--pitch",   type=int, default=55)
    parser.add_argument("--speed",   type=int, default=130)
    parser.add_argument("--force",   action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output_dir.exists() and not args.dry_run:
        for sub in args.output_dir.iterdir():
            if sub.is_dir():
                for f in sub.glob("*.wav"):
                    f.unlink()

    ok = fail = skip = 0
    for primitive, key, method, gloss, voice_override in ENTRIES:
        cat_dir = args.output_dir / primitive
        cat_dir.mkdir(parents=True, exist_ok=True)
        out = cat_dir / f"{key}.wav"

        if out.exists() and not args.force and not args.dry_run:
            print(f"  skip  {key}")
            skip += 1
            continue

        voice = voice_override or args.voice
        tag   = f"[{voice}]" if voice_override else "    "
        print(f"  gen  {tag} {key!s:35s}  {method!s:20s}  {gloss}")

        if args.dry_run:
            ok += 1
            continue

        if method.startswith("CLICK:"):
            click_type = method[len("CLICK:"):]
            try:
                generate_click(out, click_type)
                ok += 1
            except Exception as exc:
                print(f"  ERROR generating click: {exc}")
                fail += 1
        else:
            if synthesize_espeak(method, out, voice, args.pitch, args.speed):
                ok += 1
            else:
                fail += 1

    print(f"\n{ok}/{len(ENTRIES)} generated, {skip} skipped, {fail} failed")
    if not args.dry_run:
        print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
