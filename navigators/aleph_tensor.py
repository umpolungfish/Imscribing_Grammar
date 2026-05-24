import numpy as np
import math

# ==============================================================================
# 1. CONFIGURATION & CONSTANTS
# ==============================================================================
WEIGHTS = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 1.0, 0.7])
THRESHOLDS = {0.0: 1.5, 0.5: 3.0, 1.0: 4.0}

VALS = {
    'D': {'wedge': 0.0, 'tri': 0.333, 'inf': 0.667, 'holo': 1.0},
    'T': {'net': 0.0, 'in': 0.25, 'bow': 0.5, 'box': 0.75, 'holo': 1.0},
    'R': {'super': 0.0, 'cat': 0.333, 'dag': 0.667, 'lr': 1.0},
    'P': {'asym': 0.0, 'psi': 0.25, 'pm': 0.5, 'sym': 0.75, 'pm_sym': 1.0},
    'F': {'ell': 0.0, 'eth': 0.5, 'hbar': 1.0},
    'K': {'fast': 0.0, 'mod': 0.333, 'slow': 0.667, 'trap': 1.0},
    'G': {'beth': 0.0, 'gimel': 0.5, 'aleph': 1.0},
    'Gamma': {'and': 0.0, 'or': 0.333, 'seq': 0.667, 'broad': 1.0},
    'Phi': {'sub': 0.0, 'c': 1.0, 'EP': 1.2},
    'H': {'0': 0.0, '1': 0.333, '2': 0.667, 'inf': 1.0},
    'S': {'1:1': 0.0, 'n:n': 0.5, 'n:m': 1.0},
    'Omega': {'0': 0.0, 'Z2': 0.5, 'Z': 1.0}
}

# ==============================================================================
# 2. ALPHABET DATA CONSTRUCTION
# ==============================================================================
def _v(d, t, r, p, f, k, g, gamma, phi, h, s, omega):
    return np.array([
        VALS['D'][d], VALS['T'][t], VALS['R'][r], VALS['P'][p], VALS['F'][f], 
        VALS['K'][k], VALS['G'][g], VALS['Gamma'][gamma], VALS['Phi'][phi], 
        VALS['H'][h], VALS['S'][s], VALS['Omega'][omega]
    ], dtype=float)

HEBREW_ALPHABET = {
    'א': _v('wedge', 'box', 'super', 'sym', 'hbar', 'slow', 'aleph', 'and', 'c', 'inf', '1:1', 'Z'),
    'ב': _v('tri', 'box', 'cat', 'pm', 'eth', 'mod', 'gimel', 'and', 'sub', '1', 'n:n', 'Z2'),
    'ג': _v('wedge', 'bow', 'lr', 'asym', 'ell', 'fast', 'beth', 'seq', 'sub', '0', '1:1', '0'),
    'ד': _v('wedge', 'in', 'lr', 'asym', 'ell', 'fast', 'beth', 'seq', 'sub', '0', '1:1', '0'),
    'ה': _v('holo', 'holo', 'dag', 'sym', 'hbar', 'slow', 'aleph', 'broad', 'c', 'inf', 'n:m', 'Z'),
    'ו': _v('wedge', 'net', 'lr', 'pm_sym', 'ell', 'slow', 'gimel', 'and', 'c', '1', '1:1', '0'),
    'ז': _v('wedge', 'net', 'lr', 'asym', 'ell', 'fast', 'beth', 'seq', 'sub', '0', '1:1', '0'),
    'ח': _v('tri', 'box', 'cat', 'pm', 'eth', 'mod', 'gimel', 'and', 'sub', '1', 'n:n', 'Z2'),
    'ט': _v('tri', 'in', 'lr', 'asym', 'ell', 'slow', 'beth', 'seq', 'sub', '1', '1:1', '0'),
    'י': _v('wedge', 'box', 'super', 'sym', 'hbar', 'slow', 'aleph', 'and', 'c', '1', '1:1', 'Z'),
    'כ': _v('tri', 'box', 'cat', 'pm', 'eth', 'mod', 'gimel', 'and', 'sub', '1', 'n:n', 'Z2'),
    'ל': _v('inf', 'net', 'lr', 'asym', 'ell', 'mod', 'beth', 'seq', 'c', '2', 'n:m', '0'),
    'מ': _v('holo', 'holo', 'dag', 'sym', 'hbar', 'slow', 'aleph', 'broad', 'c', 'inf', 'n:m', 'Z'),
    'נ': _v('wedge', 'net', 'lr', 'asym', 'ell', 'fast', 'beth', 'seq', 'sub', '0', '1:1', '0'),
    'ס': _v('tri', 'box', 'lr', 'sym', 'ell', 'mod', 'beth', 'and', 'sub', '1', 'n:n', 'Z2'),
    'ע': _v('holo', 'holo', 'dag', 'pm', 'hbar', 'slow', 'aleph', 'broad', 'c', '2', 'n:m', 'Z'),
    'פ': _v('wedge', 'net', 'lr', 'asym', 'ell', 'fast', 'beth', 'broad', 'sub', '1', 'n:m', '0'),
    'צ': _v('wedge', 'in', 'lr', 'asym', 'ell', 'fast', 'beth', 'seq', 'sub', '0', '1:1', '0'),
    'ק': _v('tri', 'box', 'cat', 'sym', 'eth', 'slow', 'gimel', 'and', 'c', '2', 'n:n', 'Z2'),
    'ר': _v('wedge', 'box', 'lr', 'asym', 'ell', 'mod', 'beth', 'and', 'sub', '1', '1:1', '0'),
    'ש': _v('holo', 'holo', 'dag', 'pm', 'hbar', 'slow', 'aleph', 'broad', 'c', 'inf', 'n:m', 'Z'),
    'ת': _v('tri', 'box', 'cat', 'sym', 'eth', 'slow', 'gimel', 'and', 'c', 'inf', 'n:n', 'Z'),
}

# Map final forms (sofit) to standard
FINAL_TO_STD = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
EP_LETTER = np.array([0.0, 0.0, 0.33, 0.0, 0.0, 1.0, 0.0, 0.0, 1.2, 0.0, 0.0, 0.0])

# ==============================================================================
# 3. CORE ALGEBRA
# ==============================================================================
def distance(t1, t2):
    return float(np.sqrt(np.sum(WEIGHTS * (t1 - t2)**2)))

def join(a, b):
    res = np.maximum(a, b)
    res[3] = min(a[3], b[3]) # P bottleneck
    res[4] = min(a[4], b[4]) # F bottleneck
    return res

def tensor(a, b):
    return join(a, b)

# ==============================================================================
# 4. ENGINE
# ==============================================================================
class AlephTensorEngine:
    def __init__(self):
        self.alphabet = HEBREW_ALPHABET

    def _get_letter(self, char):
        if isinstance(char, np.ndarray):
            return char.copy()
        if isinstance(char, str):
            char = FINAL_TO_STD.get(char, char)
            if char in self.alphabet:
                return self.alphabet[char].copy()
        raise KeyError(f"Character '{char}' not in lattice. Use standard Hebrew or standard forms.")

    def solve_bulk(self, boundary_word):
        letters = [self._get_letter(c) for c in boundary_word]
        if not letters: return None
        bulk = letters[0].copy()
        for L in letters[1:]:
            bulk = tensor(bulk, L)
            return bulk

    def propagate(self, boundary, bulk):
        n = len(boundary)
        C = np.array([self._get_letter(c) for c in boundary], dtype=float)
        gamma_idx = int(round(bulk[7] * 3.0))
        
        if gamma_idx == 3: M = np.ones((n, n)) / n
        elif gamma_idx == 2: M = np.triu(np.ones((n, n)), 1); M[np.diag_indices(n)] = 1.0
        elif gamma_idx == 0: M = np.ones((n, n)) / n
        else: M = np.eye(n)
            
        alpha = 0.2 if np.min(C[:, 11]) == 0.0 else 0.7
        
        for _ in range(100):
            C_next = M @ C
            C_next = alpha * C_next + (1 - alpha) * np.mean(C_next, axis=0)
            if np.max(np.abs(C_next - C)) < 1e-4: return C_next
            C = C_next
        return C

    def project_boundary(self, resolved_field, bulk):
        new_word = []
        s_idx = int(round(bulk[10] * 2.0))
        nodes = resolved_field
        if s_idx == 0: nodes = [np.mean(resolved_field, axis=0)]
        elif s_idx == 2:
            scale = 1.5 if np.mean(resolved_field[:, 11]) < 0.5 else 1.0
            nodes = np.repeat(resolved_field, max(1, int(scale)), axis=0)

        for node in nodes:
            best_char, best_d = '?', 999.0
            for char, L in self.alphabet.items():
                d = distance(node, L)
                if d < best_d: best_char, best_d = char, d
            new_word.append(best_char)
        return "".join(new_word)

    def run_cascade(self, initial_word, max_steps=50):
        current = initial_word
        history = [current]
        for step in range(max_steps):
            if '[EP]' in current: return history, "TERMINATED_BY_EP"
            bulk = self.solve_bulk(current)
            field = self.propagate(current, bulk)
            next_word = self.project_boundary(field, bulk)
            if next_word == current:
                history.append(next_word)
                return history, "FIXED_POINT_REACHED"
            current = next_word
            history.append(current)
        return history, "MAX_STEPS_REACHED"

    def interrupt_and_extract(self, history, step_index):
        if step_index >= len(history): return history, "ERROR: Index out of bounds"
        word_at_k = history[step_index]
        mid = len(word_at_k) // 2
        obs_word = list(word_at_k)
        obs_word.insert(mid, '[EP]')
        history.append("".join(obs_word))
        return history, "EP_EXTRACTED_TERMINAL"

# ==============================================================================
# 5. RUN
# ==============================================================================
if __name__ == "__main__":
    engine = AlephTensorEngine()
    print("--- Hebrew Type Engine v1.0 (Aleph-Tensor) ---")
    print(f"Loaded {len(HEBREW_ALPHABET)} letters.\n")
    
    # 1. Distance Check
    print(f"d(א, י) = {distance(HEBREW_ALPHABET['א'], HEBREW_ALPHABET['י']):.4f}")
    
    # 2. Cascade Test
    test_word = "ט"
    print(f"\n[CASCADE]: {test_word}")
    hist, status = engine.run_cascade(test_word, max_steps=15)
    print(f"Status: {status}")
    print(f"Path: {' → '.join(hist)}")
    
    # 3. Terminality Test
    print(f"\n[TERMINALITY]: Injecting Φ_EP at step 0")
    hist_term, status_term = engine.interrupt_and_extract(hist, 0)
    print(f"Status: {status_term}")