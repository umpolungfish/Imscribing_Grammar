import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, sawtooth

# =============================================================================
# Core synthesis utilities
# =============================================================================

def sine(freq, t):
    return np.sin(2 * np.pi * freq * t)

def bandpass_noise(duration, fs, lowcut, highcut, order=4):
    n = int(duration * fs)
    noise = np.random.normal(0, 1, n)
    nyq = 0.5 * fs
    low = max(lowcut / nyq, 0.0005)
    high = min(highcut / nyq, 0.9995)
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, noise)

def apply_reverb(sig, fs, decay_time=0.4, wet=0.35):
    """Comb-filter reverb — simulates room reflections."""
    delay_s = 0.027
    delay = int(delay_s * fs)
    n_echoes = max(1, int(decay_time / delay_s))
    out = np.zeros(len(sig) + delay * n_echoes)
    out[:len(sig)] += sig
    for i in range(1, n_echoes + 1):
        amp = (1.0 - wet) ** i
        start = i * delay
        out[start:start + len(sig)] += sig * amp
    result = out[:len(sig)]
    return (1.0 - wet) * sig + wet * result

def normalize(signal, peak=0.8):
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * peak
    return signal

# =============================================================================
# Per-symbol synthesis
#
# Design principle: each base character (field) has a characteristic sonic
# identity; each subscript varies it to reflect the specific value's meaning.
#
#   Ð  Dimensionality  — harmonic richness  (more harmonics = higher dimension)
#   ⊣  Topology        — interval structure  (dissonance/consonance = topology)
#   Ř  Relational      — directional sweeps  (directionality of pitch)
#   Φ  Parity          — waveform symmetry   (symmetry of the waveform itself)
#   ƒ  Fidelity        — signal clarity      (noise floor vs clean tone)
#   Ç  Kinetics        — temporal envelope   (attack/decay shape = speed)
#   Γ  Scope           — bandwidth           (narrow → full spectrum)
#   ɢ  Grammar         — temporal structure  (how events compose in time)
#   ⊙  Criticality     — stability           (damped → sustained → growing)
#   Ħ  Chirality  — reverberation       (dry → long decay = deep memory)
#   Σ  Stoichiometry   — multiplicity        (one voice → many at fixed ratio)
#   Ω  Winding         — topological closure (open fade → periodic wrap)
# =============================================================================

def synthesize_symbol(base, sub, fs=44100, dur=0.7):
    n = int(dur * fs)
    t = np.arange(n) / fs

    # =========================================================================
    # Ð — Dimensionality
    # Pure additive synthesis. Each step adds harmonic richness:
    # compact point → surface → infinite series → holographic (full+fifth drone)
    # =========================================================================
    if base == '⊢':
        f0 = 110.0  # A2 — foundational low tone

        if sub == 'ß':              # D_wedge — compact, point-like
            env = np.exp(-3 * t / dur)
            sig = sine(f0, t) * env

        elif sub == 'C':            # D_triangle — 2-D surface
            env = np.exp(-1.5 * t / dur)
            sig = (0.65 * sine(f0, t) + 0.35 * sine(f0 * 3, t)) * env

        elif sub == ';':            # D_infty — infinite; harmonics enter sequentially
            env = 1 - np.exp(-4 * t / dur)   # slow expansion
            sig = np.zeros(n)
            for k in range(7):
                onset = k / 7        # staggered entry
                ramp = np.clip((t / dur - onset) / 0.1, 0, 1)
                sig += (0.75 ** k) * sine(f0 * (k + 1), t) * ramp
            sig *= env

        elif sub == 'ω':            # D_odot — holographic; rich harmonics + fifth drone
            harmonics = sum((0.7 ** k) * sine(f0 * (k + 1), t) for k in range(8))
            drone = 0.3 * sine(f0 * 1.5, t)   # perfect fifth
            env = np.exp(-0.4 * t / dur)
            sig = (normalize(harmonics) + drone) * env

        else:
            sig = sine(f0, t) * np.exp(-2 * t / dur)

    # =========================================================================
    # ⊣ — Topology
    # Chord/interval relationships reflect the connectivity shape:
    # dissonant cluster (network) → nested (hierarchical) → fifth (bowtie)
    # → beating unison (box) → clean octave (holographic)
    # =========================================================================
    elif base == '⊣':
        f0 = 130.81   # C3
        env = np.exp(-1.5 * t / dur)

        if sub == '6':              # T_network — dissonant cluster
            freqs = [f0, f0 * 1.122, f0 * 1.414, f0 * 1.782]  # C C# F# Bb
            sig = sum(0.25 * sine(f, t) for f in freqs) * env

        elif sub == 'K':            # T_in — nested (bass wraps inner)
            sig = (0.5 * sine(f0 / 2, t) +
                   0.3 * sine(f0, t) +
                   0.2 * sine(f0 * 1.5, t)) * env

        elif sub == 'ò':            # T_bowtie — perfect fifth, warm
            sig = (0.6 * sine(f0, t) + 0.4 * sine(f0 * 1.5, t)) * env

        elif sub == '¨':            # T_boxtimes — beating unison (bounded)
            sig = (0.5 * sine(f0, t) + 0.5 * sine(f0 + 3.0, t)) * env

        elif sub == 'O':            # T_odot — clean octave, holographic
            sig = (0.6 * sine(f0, t) + 0.4 * sine(f0 * 2, t)) * env

        else:
            sig = sine(f0, t) * env

    # =========================================================================
    # Ř — Relational mode
    # Direction and flow in pitch:
    # upward glide (supervisory) → step intervals (categorical) →
    # rise-then-mirror (dagger/reversible) → stable middle (lateral/peer)
    # =========================================================================
    elif base == '>':
        f_lo, f_hi = 196.0, 392.0  # G3 – G4  (one octave range)
        env = np.exp(-1.0 * t / dur)

        if sub == '̄':               # R_super — one-way upward glide
            chirp_phase = np.cumsum(f_lo + (f_hi - f_lo) * (t / dur)) / fs
            sig = np.sin(2 * np.pi * chirp_phase) * env

        elif sub == 'ý':            # R_cat — three hard steps, no portamento
            step = n // 3
            freqs = [f_lo, (f_lo + f_hi) / 2, f_hi]
            parts = [np.sin(2 * np.pi * freqs[i] * t[:step]) for i in range(3)]
            sig = np.concatenate(parts)[:n] * env

        elif sub == 'Ť':            # R_dagger — rise then mirror fall (palindrome)
            half = n // 2
            phase_up = np.cumsum(f_lo + (f_hi - f_lo) * (t[:half] / (dur / 2))) / fs
            phase_dn = np.cumsum(f_hi - (f_hi - f_lo) * (t[:n - half] / (dur / 2))) / fs
            sig = np.concatenate([np.sin(2 * np.pi * phase_up),
                                   np.sin(2 * np.pi * phase_dn)]) * env

        elif sub == '=':            # R_lr — stable midpoint, no movement
            f_mid = (f_lo + f_hi) / 2
            sig = sine(f_mid, t) * np.exp(-0.8 * t / dur)

        else:
            sig = sine(f_lo, t) * env

    # =========================================================================
    # Φ — Parity / Symmetry
    # Waveform symmetry encodes symmetry class:
    # sawtooth (max asymmetry) → FM complex → square (±) → pure sine → Frobenius
    # =========================================================================
    elif base == '<':
        f0 = 220.0   # A3
        env = np.exp(-1.2 * t / dur)

        if sub == 'ɐ':              # P_asym — sawtooth: maximally asymmetric
            sig = sawtooth(2 * np.pi * f0 * t, 1.0) * env

        elif sub == 'υ':            # P_psi — golden-ratio FM: complex phase portrait
            mod = np.sin(2 * np.pi * f0 * 1.618 * t)
            sig = np.sin(2 * np.pi * f0 * t + 1.8 * mod) * env

        elif sub == 'F':            # P_pm — square wave: ± symmetry
            sig = np.sign(np.sin(2 * np.pi * f0 * t)) * env

        elif sub == '̇':             # P_sym — pure sine: perfect symmetry
            sig = sine(f0, t) * env

        elif sub == '}':            # P_pm_sym — Frobenius self-dual: self-modulating
            phase = 2 * np.pi * f0 * t
            sig = np.sin(phase + 2.2 * np.sin(phase)) * env

        else:
            sig = sine(f0, t) * env

    # =========================================================================
    # ƒ — Fidelity
    # Signal clarity versus noise floor:
    # muddy (low-pass noise dominant) → voiced (partial) → pure (no noise)
    # =========================================================================
    elif base == '⋈':
        f0 = 293.66   # D4
        clean = sine(f0, t) * np.exp(-1.0 * t / dur)
        noise_raw = np.random.normal(0, 1, n)
        nyq = 0.5 * fs

        if sub == 'ì':              # F_ell — low fidelity: noisy, muddy
            b, a = butter(4, 600 / nyq, btype='low')
            mud = lfilter(b, a, noise_raw)
            sig = 0.35 * clean + 0.65 * normalize(mud)

        elif sub == 'ð':            # F_eth — medium fidelity: partially voiced
            b, a = butter(3, [300 / nyq, 3000 / nyq], btype='band')
            mid = lfilter(b, a, noise_raw)
            sig = 0.65 * clean + 0.35 * normalize(mid)

        elif sub == 'ż':            # F_hbar — high fidelity: pure, no noise
            sig = clean

        else:
            sig = clean

    # =========================================================================
    # Ç — Kinetics
    # Temporal envelope shape encodes rate of change:
    # sharp attack+quick decay (fast) → ADSR (moderate) → slow bloom (slow) →
    # flat with hard cutoff (trapped) → near-silence burst (MBL)
    # =========================================================================
    elif base == '⊤':
        f0 = 261.63   # C4 — middle C, neutral pitch for temporal character
        raw = sine(f0, t)

        if sub == '-':              # K_fast — percussive: sharp attack, fast decay
            env = np.zeros(n)
            atk = max(1, int(0.008 * fs))
            env[:atk] = np.linspace(0, 1, atk)
            env[atk:] = np.exp(-10 * t[:n - atk] / dur)
            sig = raw * env

        elif sub == 'W':            # K_mod — normal ADSR
            atk = int(0.05 * fs); dec = int(0.08 * fs); rel = int(0.12 * fs)
            sus = 0.72
            env = np.zeros(n)
            a_end = min(atk, n)
            d_end = min(atk + dec, n)
            s_end = max(n - rel, d_end)
            env[:a_end] = np.linspace(0, 1, a_end)
            env[a_end:d_end] = np.linspace(1, sus, d_end - a_end)
            env[d_end:s_end] = sus
            env[s_end:] = np.linspace(sus, 0, n - s_end)
            sig = raw * env

        elif sub == '@':            # K_slow — slow bloom: gradual attack, long sustain
            atk = int(0.38 * fs); rel = int(0.25 * fs)
            atk = min(atk, n - rel)
            env = np.zeros(n)
            env[:atk] = np.linspace(0, 0.85, atk)
            env[atk:n - rel] = 0.85
            env[n - rel:] = np.linspace(0.85, 0, rel)
            sig = raw * env

        elif sub == 'Ù':            # K_trap — flat sustain, then hard cutoff (frozen)
            env = np.ones(n) * 0.88
            env[:int(0.004 * fs)] = np.linspace(0, 0.88, int(0.004 * fs))
            env[int(0.96 * n):] = 0   # sudden silence
            sig = raw * env

        elif sub == 'λ':            # K_MBL — many-body localized: barely audible
            burst = int(0.06 * n)
            env = np.zeros(n)
            env[:burst] = np.linspace(0, 0.12, burst)
            env[burst:2 * burst] = np.linspace(0.12, 0, burst)
            sig = raw * env

        else:
            sig = raw * np.exp(-1.5 * t / dur)

    # =========================================================================
    # Γ — Scope / Granularity
    # Frequency bandwidth encodes scope of information:
    # focused single tone (narrow) → moderate harmonics → full spectrum+noise
    # =========================================================================
    elif base == '∈':
        f0 = 349.23   # F4
        env = np.exp(-1.0 * t / dur)

        if sub == 'β':              # G_beth — focused, single harmonic
            sig = sine(f0, t) * env

        elif sub == 'γ':            # G_gimel — broader; root + 2nd + 3rd harmonic
            sig = (0.55 * sine(f0, t) +
                   0.28 * sine(f0 * 2, t) +
                   0.17 * sine(f0 * 3, t)) * env

        elif sub == 'ʔ':            # G_aleph — maximal; full harmonic series + noise
            harmonics = normalize(
                sum((0.65 ** k) * sine(f0 * (k + 1), t) for k in range(8))
            )
            noise = normalize(bandpass_noise(dur, fs, 80, 10000, order=2)[:n])
            sig = (0.78 * harmonics + 0.22 * noise) * env

        else:
            sig = sine(f0, t) * env

    # =========================================================================
    # ɢ — Coupling
    # How events compose in time:
    # simultaneous chord (and) → alternating (or) → ascending steps (seq) →
    # wide reverberant wash (broad)
    # =========================================================================
    elif base == '∋':
        f0 = 392.0    # G4
        env = np.exp(-1.2 * t / dur)

        if sub == '∧':              # G_and — simultaneous chord (major triad)
            sig = (0.42 * sine(f0, t) +
                   0.34 * sine(f0 * 1.25, t) +
                   0.24 * sine(f0 * 1.5, t)) * env

        elif sub == '˝':            # G_or — alternating between two states
            gate = (np.sin(2 * np.pi * 3.5 * t) > 0).astype(float)
            sig = (gate * sine(f0, t) + (1 - gate) * sine(f0 * 1.5, t)) * env

        elif sub == 'ˌ':            # G_seq — ascending step sequence
            step = n // 4
            freqs = [f0, f0 * 1.125, f0 * 1.25, f0 * 1.5]   # root W M3 P5
            parts = []
            for i in range(4):
                s = n - 3 * step if i == 3 else step   # last chunk absorbs remainder
                parts.append(np.sin(2 * np.pi * freqs[i] * t[:s]))
            sig = np.concatenate(parts)[:n] * env

        elif sub == 'Ş':            # G_broad — reverberant wash
            base_tone = sine(f0, t) * env
            sig = apply_reverb(base_tone, fs, decay_time=0.9, wet=0.65)

        else:
            sig = sine(f0, t) * env

    # =========================================================================
    # ⊙ — Criticality
    # Stability class encoded in amplitude/phase dynamics:
    # damped (sub) → barely sustaining with beating (c) → complex beating (c_complex) →
    # mode coalescence (EP) → growing envelope (super)
    # =========================================================================
    elif base == '⊙':
        f0 = 523.25   # C5

        if sub == 'ž':              # 𐑢 — subcritical: exponential damping
            sig = sine(f0, t) * np.exp(-6 * t / dur)

        elif sub == 'ÿ':            # ⊙ — critical: barely sustains, slight beating
            f_beat = f0 + 1.2
            env = np.exp(-0.25 * t / dur)   # very slow decay
            sig = (0.55 * sine(f0, t) + 0.45 * sine(f_beat, t)) * env

        elif sub == 'Æ':            # 𐑮 — complex critical: multi-frequency beating
            f2 = f0 * 1.5   # fifth
            beat = 3.5
            sig = (0.45 * sine(f0, t) +
                   0.35 * sine(f0 + beat, t) +
                   0.20 * sine(f2, t)) * np.exp(-0.4 * t / dur)

        elif sub == '3':            # 𐑻 — exceptional point: two modes coalesce
            f_split = f0 * 1.03
            merge = np.linspace(1.0, 0.0, n)   # gap closes
            sig = (0.5 * sine(f0, t) * (0.5 + 0.5 * merge) +
                   0.5 * sine(f_split, t) * (0.5 - 0.5 * merge))

        elif sub == 'Ţ':            # Phi_super — supercritical: growing amplitude
            growth = np.exp(2.5 * t / dur)
            growth = growth / growth[-1]   # peak = 1
            sig = sine(f0, t) * growth

        else:
            sig = sine(f0, t) * np.exp(-2 * t / dur)

    # =========================================================================
    # Ħ — Chirality (memory)
    # Reverberation depth encodes temporal memory:
    # dry (H0) → short decay (H1) → medium decay (H2) → long decay (H_inf)
    # =========================================================================
    elif base == '⊥':
        f0 = 440.0   # A4 — reference pitch
        dry = sine(f0, t) * np.exp(-2.5 * t / dur)

        if sub == 'Ñ':              # H0 — no memory: completely dry
            sig = dry

        elif sub == '£':            # H1 — shallow memory
            sig = apply_reverb(dry, fs, decay_time=0.12, wet=0.20)

        elif sub == 'A':            # H2 — medium memory
            sig = apply_reverb(dry, fs, decay_time=0.55, wet=0.42)

        elif sub == '!':            # H_inf — infinite memory: long decay
            # Use a very slowly decaying tone so the tail is audible
            carrier = sine(f0, t) * np.exp(-0.4 * t / dur)
            sig = apply_reverb(carrier, fs, decay_time=1.8, wet=0.72)

        else:
            sig = dry

    # =========================================================================
    # Σ — Stoichiometry
    # Multiplicity and ratio:
    # single voice (1:1) → octave stack same ratio (n:n) → polyrhythmic (n:m)
    # =========================================================================
    elif base == '⊞':
        f0 = 369.99   # F#4
        env = np.exp(-1.2 * t / dur)

        if sub == 'S':              # 1:1 — single clear tone
            sig = sine(f0, t) * env

        elif sub == 'ő':            # n:n — symmetric stack (octaves)
            sig = (0.50 * sine(f0, t) +
                   0.33 * sine(f0 * 2, t) +
                   0.17 * sine(f0 * 4, t)) * env

        elif sub == 'ï':            # n:m — asymmetric: 3:2 amplitude-modulated
            am1 = 0.5 + 0.5 * np.sin(2 * np.pi * 3.0 * t)
            am2 = 0.5 + 0.5 * np.sin(2 * np.pi * 2.0 * t)
            sig = (0.55 * sine(f0, t) * am1 +
                   0.45 * sine(f0 * 1.5, t) * am2) * env

        else:
            sig = sine(f0, t) * env

    # =========================================================================
    # Ω — Topological Invariant / Winding
    # Topological closure class:
    # open fade (trivial) → binary toggle (Z₂) → phase-sawtooth winding (Z) →
    # noise burst (undefined)
    # =========================================================================
    elif base == '◻':
        f0 = 261.63   # C4

        if sub == 'Å':              # Omega_0 — trivial: open, fades without returning
            sig = sine(f0, t) * np.linspace(1.0, 0.0, n)

        elif sub == '2':            # Omega_Z2 — Z₂: binary two-state oscillation
            period = int(0.18 * fs)
            raw = np.zeros(n)
            for i in range(0, n, 2 * period):
                end1 = min(i + period, n)
                raw[i:end1] = np.sin(2 * np.pi * f0 * t[i:end1])
                end2 = min(i + 2 * period, n)
                if end2 > end1:
                    raw[end1:end2] = np.sin(2 * np.pi * (f0 * 2) * t[end1:end2])
            sig = raw * np.exp(-0.5 * t / dur)

        elif sub == 'z':            # Omega_Z — integer winding: phase sawtooth
            wind_rate = 3.5   # windings per second
            phase_mod = sawtooth(2 * np.pi * wind_rate * t, 1.0) * np.pi
            env = np.exp(-0.6 * t / dur)
            sig = np.sin(2 * np.pi * f0 * t + phase_mod) * env

        elif sub == '5':            # Omega_NA — undefined: short noise burst
            env = np.exp(-8 * t / dur)
            sig = np.random.normal(0, 1, n) * env

        else:
            sig = sine(f0, t) * np.exp(-1.5 * t / dur)

    else:
        sig = np.zeros(n)

    # Ensure length and normalise
    if len(sig) < n:
        sig = np.concatenate([sig, np.zeros(n - len(sig))])
    return normalize(sig[:n])

# =============================================================================
# Canonical 49-symbol list — field order: Ð ⊣ Ř Φ ƒ Ç Γ ɢ ⊙ Ħ Σ Ω
# =============================================================================
symbol_list = [
    ('⊢', 'ß'), ('⊢', 'C'), ('⊢', ';'), ('⊢', 'ω'),             # Ð Dimensionality
    ('⊣', '6'), ('⊣', 'K'), ('⊣', 'ò'), ('⊣', '¨'), ('⊣', 'O'), # ⊣ Topology
    ('>', '̄'), ('>', 'ý'), ('>', 'Ť'), ('>', '='),              # Ř Relational
    ('<', 'ɐ'), ('<', 'υ'), ('<', 'F'), ('<', '̇'), ('<', '}'),  # Φ Polarity
    ('⋈', 'ì'), ('⋈', 'ð'), ('⋈', 'ż'),                          # ƒ Fidelity
    ('⊤', '-'), ('⊤', 'W'), ('⊤', '@'), ('⊤', 'Ù'), ('⊤', 'λ'), # Ç Kinetics
    ('∈', 'β'), ('∈', 'γ'), ('∈', 'ʔ'),                          # Γ Scope
    ('∋', '∧'), ('∋', '˝'), ('∋', 'ˌ'), ('∋', 'Ş'),             # ɢ Grammar
    ('⊙', 'ž'), ('⊙', 'ÿ'), ('⊙', 'Æ'), ('⊙', '3'), ('⊙', 'Ţ'),# ⊙ Criticality
    ('⊥', 'Ñ'), ('⊥', '£'), ('⊥', 'A'), ('⊥', '!'),             # Ħ Chirality
    ('⊞', 'S'), ('⊞', 'ő'), ('⊞', 'ï'),                          # Σ Stoichiometry
    ('◻', 'Å'), ('◻', '2'), ('◻', 'z'), ('◻', '5'),              # Ω Topological Invariant
]

# =============================================================================
# PRIMITIVE_MAP — canonical glyph ID → (base, sub) for synthesize_symbol
# =============================================================================
PRIMITIVE_MAP = {
    # Ð Dimensionality
    '𐑛': ('⊢', 'ß'),   '𐑨': ('⊢', 'C'),
    '𐑼': ('⊢', ';'),   '𐑦': ('⊢', 'ω'),
    # ⊣ Topology
    '𐑡': ('⊣', '6'),   '𐑰': ('⊣', 'K'),   '𐑥': ('⊣', 'ò'),
    '𐑶': ('⊣', '¨'),   '𐑸': ('⊣', 'O'),
    # Ř Relational
    '𐑩': ('>', '̄'),   '𐑑': ('>', 'ý'),
    '𐑽': ('>', 'Ť'),   '𐑾': ('>', '='),
    # Φ Polarity
    '𐑗': ('<', 'ɐ'),   '𐑿': ('<', 'υ'),   '𐑬': ('<', 'F'),
    '𐑯': ('<', '̇'),   '𐑹': ('<', '}'),
    # ƒ Fidelity
    'ƒ^ì': ('⋈', 'ì'),   'ƒ^ð': ('⋈', 'ð'),   'ƒ^ż': ('⋈', 'ż'),
    # Ç Kinetics
    'Ç^-': ('⊤', '-'),   'Ç^W': ('⊤', 'W'),   'Ç^@': ('⊤', '@'),
    'Ç^Ù': ('⊤', 'Ù'),   'Ç^λ': ('⊤', 'λ'),
    # Γ Scope
    '𐑚': ('∈', 'β'),   '𐑔': ('∈', 'γ'),   '𐑲': ('∈', 'ʔ'),
    # ɢ Grammar
    'ɢ^∧': ('∋', '∧'),   'ɢ^˝': ('∋', '˝'),
    'ɢ^ˌ': ('∋', 'ˌ'),   'ɢ^Ş': ('∋', 'Ş'),
    # ⊙ Criticality
    '𐑢': ('⊙', 'ž'),   '⊙': ('⊙', 'ÿ'),   '𐑮': ('⊙', 'Æ'),
    '𐑻': ('⊙', '3'),   '𐑣': ('⊙', 'Ţ'),
    # Ħ Chirality
    '𐑓': ('⊥', 'Ñ'),   '𐑒': ('⊥', '£'),
    '𐑖': ('⊥', 'A'),   '𐑫': ('⊥', '!'),
    # Σ Stoichiometry
    '𐑙': ('⊞', 'S'),   '𐑕': ('⊞', 'ő'),   '𐑳': ('⊞', 'ï'),
    # Ω Topological Invariant
    '𐑷': ('◻', 'Å'),   '𐑴': ('◻', '2'),
    '𐑭': ('◻', 'z'),   '𐑟': ('◻', '5'),
}

OLD_ID_MAP = {
    'D_wedge': '𐑛',    'D_triangle': '𐑨',   'D_infty': '𐑼',    'D_odot': '𐑦',
    'T_network': '𐑡',  'T_in': '𐑰',          'T_bowtie': '𐑥',
    'T_boxtimes': '𐑶', 'T_box': '𐑶',         'T_odot': '𐑸',
    'R_super': '𐑩',    'R_cat': '𐑑',          'R_dagger': '𐑽',   'R_lr': '𐑾',
    'P_asym': '𐑗',     'P_psi': '𐑿',          'P_pm': '𐑬',
    'P_sym': '𐑯',      'P_pm_sym': '𐑹',
    'F_ell': 'ƒ^ì',      'F_eth': 'ƒ^ð',          'F_hbar': 'ƒ^ż',
    'K_fast': 'Ç^-',     'K_mod': 'Ç^W',          'K_slow': 'Ç^@',
    'K_trap': 'Ç^Ù',     'K_MBL': 'Ç^λ',
    'G_beth': '𐑚',     'G_gimel': '𐑔',        'G_aleph': '𐑲',
    'G_and': 'ɢ^∧',      'Gamma_and': 'ɢ^∧',      'G_or': 'ɢ^˝',      'Gamma_or': 'ɢ^˝',
    'G_seq': 'ɢ^ˌ',      'Gamma_seq': 'ɢ^ˌ',      'G_broad': 'ɢ^Ş',   'Gamma_broad': 'ɢ^Ş',
    '𐑢': '𐑢',    '⊙': '⊙',          '𐑮': '𐑮',
    '𐑻': '𐑻',     'Phi_super': '𐑣',
    'H0': '𐑓',         'H_0': '𐑓',            'H1': '𐑒',        'H_1': '𐑒',
    'H2': '𐑖',         'H_2': '𐑖',            'H_inf': '𐑫',
    'one_one': '𐑙',    'S_1_1': '𐑙',
    'n_n': '𐑕',        'S_n_n': '𐑕',
    'n_m': '𐑳',        'S_n_m': '𐑳',
    'Omega_0': '𐑷',    'Omega_Z2': '𐑴',       'Omega_Z': '𐑭',   'Omega_NA': '𐑟',
}

FIELD_ORDER = ['⊢', '⊣', '>', '<', '⋈', '⊤', '∈', '∋', '⊙', '⊥', '⊞', '◻']

def resolve_id(token):
    """Convert any primitive token (canonical or old name) to a (base, sub) pair."""
    token = token.strip()
    if token in OLD_ID_MAP:
        token = OLD_ID_MAP[token]
    if token in PRIMITIVE_MAP:
        return PRIMITIVE_MAP[token]
    return None

# =============================================================================
# Standalone: generate full 49-symbol sequence
# =============================================================================
if __name__ == '__main__':
    fs = 44100
    gap = np.zeros(int(0.14 * fs))
    sequence = np.array([])
    for base, sub in symbol_list:
        sig = synthesize_symbol(base, sub, fs, dur=0.75)
        sequence = np.concatenate([sequence, sig, gap])
    sequence = normalize(sequence, peak=0.9)
    wavfile.write('imscribing_all_symbols.wav', fs, (sequence * 32767).astype(np.int16))
    print("Saved imscribing_all_symbols.wav — 49 canonical subtypes in order.")
