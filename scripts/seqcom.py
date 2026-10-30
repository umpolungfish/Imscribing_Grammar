import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, sawtooth

# =============================================================================
# Helper functions for synthesis
# =============================================================================

def bandpass_noise(duration, fs, lowcut, highcut, order=4):
    """Generate white noise filtered with a bandpass filter."""
    n_samples = int(duration * fs)
    noise = np.random.normal(0, 1, n_samples)
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, noise)

def formant_filter(signal, fs, formant_freq, bandwidth=100):
    """Apply a simple second‑order resonator to simulate a formant."""
    nyq = 0.5 * fs
    low = (formant_freq - bandwidth) / nyq
    high = (formant_freq + bandwidth) / nyq
    low = max(low, 0.01)
    high = min(high, 0.99)
    b, a = butter(2, [low, high], btype='band')
    return lfilter(b, a, signal)

def voice_source(duration, fs, f0, breathy=0.0, creaky=False):
    """
    Generate a pitched source (sawtooth) plus optional aspiration noise.
    `breathy` controls the noise mix (0 = pure tone, 1 = all noise).
    If `creaky` is True, the fundamental frequency is very low and irregular.
    """
    n_samples = int(duration * fs)
    t = np.arange(n_samples) / fs

    if creaky:
        # irregular pulse train with jitter
        f0_irregular = f0 + 10 * np.sin(2 * np.pi * 7 * t)   # slow modulation
        phase = np.cumsum(f0_irregular) / fs
        pulse = (1.0 - (phase % 1.0) * 2)                    # sawtooth-like
        # make it very soft and crackly
        harmonic = 0.3 * pulse * np.exp(-2 * t)              # fade quickly
    else:
        harmonic = sawtooth(2 * np.pi * f0 * t, 0.5)

    # breathy mix: add noise
    noise = np.random.normal(0, 1, n_samples)
    mix = (1 - breathy) * harmonic + breathy * noise
    return mix

def apply_formants(signal, fs, formants, bandwidths=None):
    """Pass the signal through parallel formant filters and sum."""
    if bandwidths is None:
        bandwidths = [150, 200, 300]   # default bandwidths
    filtered = np.zeros_like(signal)
    for f, bw in zip(formants, bandwidths):
        filtered += formant_filter(signal, fs, f, bw)
    return filtered

def trill_source(duration, fs, f0=120, trill_rate=30, breathiness=0.5):
    """Alveolar trill: voice with amplitude modulation + noise."""
    n_samples = int(duration * fs)
    t = np.arange(n_samples) / fs
    # carrier: voiced
    carrier = sawtooth(2 * np.pi * f0 * t, 0.5)
    # amplitude modulation (tongue contacts)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * trill_rate * t)
    # add breathiness
    noise = np.random.normal(0, 1, n_samples)
    mixed = am * ((1 - breathiness) * carrier + breathiness * noise)
    return mixed

def normalize(signal, peak=0.8):
    """Normalize to avoid clipping."""
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * peak
    return signal

# =============================================================================
# Synthesis parameters
# =============================================================================
fs = 44100                    # sample rate
dur = 0.6                     # default duration for each sound (seconds)
gap = np.zeros(int(0.1 * fs)) # silence between sounds

# =============================================================================
# 1. ⊙  (Phi‑hat with y‑diaeresis)
# =============================================================================
# Voiceless bilabial fricative shaped by [ʉ] (centralized rounded close vowel)
noise = bandpass_noise(dur, fs, 200, 1500, order=4)
# [ʉ] formants F1~300, F2~1100
fmt = apply_formants(noise, fs, [300, 1100, 2400], [100, 150, 300])
snd1 = normalize(fmt)

# =============================================================================
# 2. 𐑗  (Big Phi with turned‑a)
# =============================================================================
noise = bandpass_noise(dur, fs, 200, 1500, order=4)
# [ɐ] near‑open central vowel: F1~650, F2~1300
fmt = apply_formants(noise, fs, [650, 1300, 2500], [150, 200, 300])
snd2 = normalize(fmt)

# =============================================================================
# 3. 𐑷  (Omega with Angstrom)
# =============================================================================
# Deep back rounded vowel [ɒ]: use voiced source
source = voice_source(dur, fs, f0=110, breathy=0.2)
# Very low, hollow formants: F1~500, F2~800
fmt = apply_formants(source, fs, [500, 800, 2200], [100, 150, 200])
snd3 = normalize(fmt)

# =============================================================================
# 4. 𐑛  (Eth with Eszett)
# =============================================================================
# simultaneous voiced dental fricative [ð] and sibilant [s]
# use a mixture: voiced source + noise, then filter with both dental and sibilant formants
t = np.arange(int(dur * fs)) / fs
voice = sawtooth(2 * np.pi * 120 * t, 0.5)
noise = np.random.normal(0, 1, int(dur * fs))
mix = 0.6 * voice + 0.6 * noise
# dental [ð]: diffuse energy around 1500‑3000 Hz
dental = formant_filter(mix, fs, 2000, 800)
# sibilant [s]: high peak around 5000‑8000 Hz
sibilant = bandpass_noise(dur, fs, 4000, 8000, order=4) * 0.5
combined = 0.7 * dental + 0.3 * sibilant
snd4 = normalize(combined)

# =============================================================================
# 5. 𐑡  (Thorn with subscript 6)
# =============================================================================
# voiceless th [θ] + high squeaky tone
noise = bandpass_noise(dur, fs, 1400, 3000, order=4) * 1.2
# rising high tone: sine sweep from 2 kHz to 4 kHz
t = np.arange(int(dur * fs)) / fs
freq = 2000 + 2000 * (t / dur)   # linear rise
tone = 0.3 * np.sin(2 * np.pi * freq * t) * np.linspace(1, 0.5, len(t))
snd5 = normalize(noise + tone)

# =============================================================================
# 6. 𐑩  (R‑caron with macron)
# =============================================================================
# breathy voiced trill, gradually becoming more breathy
t_full = np.arange(int(1.0 * fs)) / fs
n_full = len(t_full)
trill = trill_source(1.0, fs, f0=120, trill_rate=28, breathiness=0.3)
# formants for schwa [ə]: F1~500, F2~1500
fmt = apply_formants(trill, fs, [500, 1500, 2500])
# gradual increase of breathiness: second half mixes in more noise
noise_tail = bandpass_noise(1.0, fs, 500, 4000) * 0.4
envelope = np.concatenate([np.ones(int(0.3*fs)), np.linspace(1, 0.7, n_full - int(0.3*fs))])
snd6 = normalize(fmt * envelope + noise_tail * (1 - envelope))

# =============================================================================
# 7. f_ì  (italic f with i‑grave)
# =============================================================================
# [f] with [i] tongue position, falling pitch
noise = bandpass_noise(dur, fs, 1500, 3000, order=4)  # [f] with high formant
# falling tone: sine from 300 Hz to 150 Hz
t = np.arange(int(dur * fs)) / fs
freq = 300 - 150 * (t / dur)
tone = 0.2 * np.sin(2 * np.pi * freq * t)
snd7 = normalize(noise * 0.7 + tone)

# =============================================================================
# 8. ⊤^Ù  (C‑cedilla with U‑grave)
# =============================================================================
# [s] with [u] rounding (very low second formant), falling pitch
noise = bandpass_noise(dur, fs, 500, 1500, order=4)   # low‑frequency hiss
t = np.arange(int(dur * fs)) / fs
freq = 250 - 100 * (t / dur)                          # falling low tone
tone = 0.2 * np.sin(2 * np.pi * freq * t)
snd8 = normalize(noise + tone)

# =============================================================================
# 9. 𐑚  (Gamma with Beta)
# =============================================================================
# simultaneous voiced velar fricative [ɣ] + voiced bilabial fricative [β]
source = voice_source(dur, fs, 120, breathy=0.5)
# [ɣ] has energy around 1000‑2000 Hz, [β] low around 200‑600 Hz
velar = formant_filter(source, fs, 1500, 500)
bilabial = formant_filter(source, fs, 400, 200)
snd9 = normalize(0.6 * velar + 0.6 * bilabial)

# =============================================================================
# 10. ∋^  (small capital G with hat)
# =============================================================================
# uvular plosive [∋] with creaky voice
closure = np.zeros(int(0.15 * fs))              # silent closure
burst_noise = bandpass_noise(0.02, fs, 800, 2000, order=4)  # short noise burst
burst = np.concatenate([burst_noise, np.zeros(int(0.05 * fs))])
# creaky vowel
creak = voice_source(0.6, fs, f0=50, creaky=True) * 0.4
fmt_creak = apply_formants(creak, fs, [700, 1200, 2500])  # [ɑ]‑like
snd10 = normalize(np.concatenate([closure, burst, fmt_creak]))

# =============================================================================
# 11. 𐑓  (H‑bar with N‑tilde)
# =============================================================================
# voiceless pharyngeal fricative [ħ] + nasal palatal [ɲ] -> breathy nasalised vowel
# voice with nasal formant (low) + pharyngeal noise
voice_nas = voice_source(dur, fs, 130, breathy=0.7)
# nasal murmur: single low formant, plus anti‑formant (simulated by a notch)
fmt_nas = formant_filter(voice_nas, fs, 350, 80)      # nasal pole
# add harsh pharyngeal noise
noise_ph = bandpass_noise(dur, fs, 600, 1800, order=4) * 0.4
snd11 = normalize(fmt_nas * 0.7 + noise_ph)

# =============================================================================
# 12. 𐑙  (Sigma with S)
# =============================================================================
# geminate long [sː]
long_s = bandpass_noise(1.2, fs, 4500, 10000, order=4)
snd12 = normalize(long_s)

# =============================================================================
# Concatenate the whole sequence with gaps
# =============================================================================
sequence = np.concatenate([
    snd1, gap, snd2, gap, snd3, gap, snd4, gap,
    snd5, gap, snd6, gap, snd7, gap, snd8, gap,
    snd9, gap, snd10, gap, snd11, gap, snd12
])
# Final normalisation
sequence = normalize(sequence, peak=0.9)

# =============================================================================
# Save to WAV file
# =============================================================================
wavfile.write('combined_sequence.wav', fs, (sequence * 32767).astype(np.int16))
print("Audio saved as 'combined_sequence.wav'")
