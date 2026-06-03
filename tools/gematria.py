#!/usr/bin/env python3
"""
IG Gematria Engine — True numerical gematria over the 12-dimensional vector space
of the Imscribing Grammar catalog.

Operations:
  - Vector addition/subtraction equations: find A, B s.t. A ± B = C
  - Spectral decomposition: PCA eigenvalues, principal components
  - Symmetry group: permutations of primitives that preserve catalog structure
  - Clustering: k-means, hierarchical over the vector ensemble
  - Gematria sums: sequences of entries whose sum lands on another entry
  - Primitive-value pattern mining: frequent itemsets of glyph co-occurrences
"""
import sys, json, math, os
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set
from itertools import combinations, product

import numpy as np

# Import our encoding engine
sys.path.insert(0, str(Path(__file__).resolve().parent))
from numerical_encode import (
    PRIMITIVES, PRIM_CARDINALITIES, GLYPH_ORDINALS, ORDINAL_GLYPHS,
    IG_TO_SHAVIAN, is_valid_entry, resolve_all,
    encode_ordinal, encode_zero_centered, encode_normalized,
    encode_integer_compact, encode_crystal_address,
    vec_add, vec_sub, vec_hadamard, vec_dot, vec_norm, vec_cosine,
    vec_l1, vec_l2, vec_mean, vec_to_closest_glyph, encode_catalog,
    vector_to_tuple_str,
)

# ── Paths ───────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def load_catalog() -> List[Dict]:
    """Load the full IG catalog (as dicts with primitive keys)."""
    try:
        from imscrbgrmr.registry import load_catalog_dicts
        return load_catalog_dicts()
    except ImportError:
        # Try loading from the catalog JSON directly
        cat_path = PROJECT_ROOT / '.imscrbgrmr_catalog.json'
        if cat_path.exists():
            with open(cat_path) as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and '_imscriptions' in data:
                return list(data['_imscriptions'].values())
        print("WARNING: Could not load catalog", file=sys.stderr)
        return []

# ── Gematria Index ───────────────────────────────────────────────

class GematriaIndex:
    """
    Pre-built index for fast gematria lookup.
    Maps each integer-compact vector → list of entry names.
    """

    def __init__(self, entries: List[Dict], scheme: str = 'ordinal'):
        self.entries = entries
        self.scheme = scheme
        self.vectors, self.names, self.valid_entries = encode_catalog(entries, scheme)
        self.n = len(self.vectors)

        # Build forward index: vector tuple → names
        self.vec_to_names: Dict[Tuple, List[str]] = defaultdict(list)
        self.name_to_vec: Dict[str, List[float]] = {}
        self.name_to_entry: Dict[str, Dict] = {}

        for v, name, entry in zip(self.vectors, self.names, self.valid_entries):
            key = tuple(round(x, 6) for x in v)
            self.vec_to_names[key].append(name)
            self.name_to_vec[name] = v
            self.name_to_entry[name] = entry

        # Integer-compact for exact matching
        self.int_vectors = []
        self.int_to_names: Dict[Tuple[int, ...], List[str]] = defaultdict(list)
        for entry in self.valid_entries:
            iv = encode_integer_compact(entry)
            self.int_vectors.append(iv)
            self.int_to_names[tuple(iv)].append(entry.get('name', 'unknown'))

        # NumPy matrix for fast ops
        self.matrix = np.array(self.vectors, dtype=np.float64)

        print(f"GematriaIndex: {self.n} valid entries, {len(self.vec_to_names)} unique vectors, "
              f"{len(self.int_to_names)} unique int-vectors")

    def find_additive_equations(self, max_results: int = 200) -> List[Dict]:
        """
        GEMATRIA CORE: Find all A + B = C equations in the catalog.

        For integer-compact vectors (0..card-1), look for triples where
        A_vec + B_vec = C_vec (element-wise integer addition).
        """
        results = []
        # Build lookup of int vectors → names for all entries
        int_vecs = self.int_vectors
        int_names = [e.get('name', '?') for e in self.valid_entries]
        n = len(int_vecs)

        # For efficiency, iterate pairs and check if sum exists in the catalog
        checked = set()
        for i in range(n):
            a_vec = int_vecs[i]
            for j in range(i, n):
                b_vec = int_vecs[j]
                # Sum
                sum_vec = tuple(a_vec[k] + b_vec[k] for k in range(12))
                if sum_vec in self.int_to_names:
                    for c_name in self.int_to_names[sum_vec]:
                        if c_name != int_names[i] and c_name != int_names[j]:
                            key = (int_names[i], int_names[j], c_name)
                            if key not in checked:
                                checked.add(key)
                                results.append({
                                    'a': int_names[i], 'b': int_names[j],
                                    'c': c_name, 'type': 'A+B=C',
                                    'a_vec': list(a_vec), 'b_vec': list(b_vec), 'c_vec': list(sum_vec),
                                })

                # Difference (A - B = C → A = B + C)
                diff_vec = tuple(a_vec[k] - b_vec[k] for k in range(12))
                if all(d >= 0 for d in diff_vec) and diff_vec in self.int_to_names:
                    for c_name in self.int_to_names[diff_vec]:
                        if c_name != int_names[i] and c_name != int_names[j]:
                            key = (int_names[i], int_names[j], c_name)
                            if key not in checked:
                                checked.add(key)
                                results.append({
                                    'a': int_names[i], 'b': int_names[j],
                                    'c': c_name, 'type': 'A-B=C',
                                    'a_vec': list(a_vec), 'b_vec': list(b_vec), 'c_vec': list(diff_vec),
                                })

                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break
        return results

    def find_integer_span(self) -> Dict:
        """
        What integer vectors are reachable by linear combinations of catalog entries?
        Compute the Z-module spanned by the integer vectors.
        """
        mat = np.array(self.int_vectors, dtype=np.int64)
        # Rank of the integer matrix
        from numpy.linalg import matrix_rank
        rank = matrix_rank(mat.astype(np.float64))
        # Bounding box
        mins = mat.min(axis=0)
        maxs = mat.max(axis=0)
        # Convex hull volume estimate
        spans = maxs - mins + 1
        total_cells = np.prod(spans)

        # How many distinct integer vectors exist vs how many are occupied?
        occupied = len(self.int_to_names)

        return {
            'rank': int(rank),
            'occupied_int_vectors': occupied,
            'bounding_box_volume': int(total_cells),
            'coverage_ratio': occupied / total_cells if total_cells > 0 else 0,
            'min_bounds': [int(x) for x in mins],
            'max_bounds': [int(x) for x in maxs],
            'spans': [int(x) for x in spans],
        }

    def spectral_analysis(self) -> Dict:
        """
        PCA / eigendecomposition of the vector ensemble.
        Reveals which primitive combinations carry the most variance.
        """
        # Center the data
        mean_vec = self.matrix.mean(axis=0)
        centered = self.matrix - mean_vec

        # Covariance matrix (12×12)
        cov = np.cov(centered.T)

        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        # Sort descending
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Variance explained
        total_var = eigenvalues.sum()
        explained = [(ev / total_var) for ev in eigenvalues]

        # Principal component loadings
        pc_loadings = []
        for i in range(min(6, len(eigenvalues))):
            loadings = eigenvectors[:, i]
            # Which primitives dominate this PC?
            top_prims = sorted(zip(PRIMITIVES, abs(loadings)), key=lambda x: -x[1])
            pc_loadings.append({
                'pc': i + 1,
                'eigenvalue': float(eigenvalues[i]),
                'variance_explained': float(explained[i]),
                'cumulative': float(sum(explained[:i+1])),
                'top_primitives': [(p, float(v)) for p, v in top_prims[:4]],
                'full_loadings': {PRIMITIVES[j]: float(loadings[j]) for j in range(12)},
            })

        # Condition number
        cond = eigenvalues[0] / eigenvalues[-1] if eigenvalues[-1] > 0 else float('inf')

        return {
            'eigenvalues': [float(x) for x in eigenvalues],
            'variance_explained': [float(x) for x in explained],
            'cumulative_variance': [float(sum(explained[:i+1])) for i in range(len(explained))],
            'condition_number': float(cond),
            'principal_components': pc_loadings,
            'mean_vector': [float(x) for x in mean_vec],
            'covariance_matrix': [[float(x) for x in row] for row in cov],
        }

    def primitive_correlations(self) -> Dict:
        """Pearson correlation matrix between all 12 primitives."""
        corr = np.corrcoef(self.matrix.T)
        # Find strongest and weakest pairs
        pairs = []
        for i in range(12):
            for j in range(i+1, 12):
                pairs.append({
                    'a': PRIMITIVES[i], 'b': PRIMITIVES[j],
                    'correlation': float(corr[i, j]),
                    'abs_corr': abs(float(corr[i, j])),
                })
        pairs.sort(key=lambda x: -x['abs_corr'])

        return {
            'correlation_matrix': [[float(x) for x in row] for row in corr],
            'strongest_pairs': pairs[:10],
            'weakest_pairs': pairs[-10:],
            'primitive_against_all': {
                PRIMITIVES[i]: {
                    PRIMITIVES[j]: float(corr[i, j]) for j in range(12) if j != i
                } for i in range(12)
            },
        }

    def gematria_word_search(self, word_length: int = 3, max_results: int = 100) -> List[Dict]:
        """
        Find sequences of `word_length` entries whose vector sum equals another entry.
        This is TRUE GEMATRIA — "words" that "spell" structural types.
        """
        results = []
        int_vecs = self.int_vectors
        int_names = [e.get('name', '?') for e in self.valid_entries]
        n = len(int_vecs)

        # For longer words, use meet-in-the-middle
        if word_length == 2:
            return self.find_additive_equations(max_results)

        elif word_length == 3:
            # Precompute all pairwise sums
            pair_sums: Dict[Tuple, List[Tuple[int, int]]] = defaultdict(list)
            for i in range(n):
                for j in range(i, n):
                    s = tuple(int_vecs[i][k] + int_vecs[j][k] for k in range(12))
                    pair_sums[s].append((i, j))

            # For each entry C, find pairs (A,B) and singles D such that A+B+D = C
            # i.e., A+B = C-D
            for d_idx in range(n):
                d_vec = int_vecs[d_idx]
                for c_idx in range(n):
                    if c_idx == d_idx:
                        continue
                    target = tuple(int_vecs[c_idx][k] - d_vec[k] for k in range(12))
                    if all(t >= 0 for t in target) and target in pair_sums:
                        for (a_idx, b_idx) in pair_sums[target]:
                            names = sorted([int_names[a_idx], int_names[b_idx], int_names[d_idx]])
                            c_name = int_names[c_idx]
                            if c_name not in names:
                                results.append({
                                    'word': names,
                                    'target': c_name,
                                    'type': 'A+B+D=C',
                                })
                                if len(results) >= max_results:
                                    return results

        elif word_length == 4:
            # Meet-in-the-middle: precompute all 2-sums
            pair_sums: Dict[Tuple, List[Tuple[int, int]]] = defaultdict(list)
            for i in range(n):
                for j in range(i, n):
                    s = tuple(int_vecs[i][k] + int_vecs[j][k] for k in range(12))
                    pair_sums[s].append((i, j))

            for c_idx in range(n):
                c_vec = int_vecs[c_idx]
                # Find all pairs of pairs that sum to c_vec
                pair_keys = list(pair_sums.keys())
                for pk1 in pair_keys:
                    target = tuple(c_vec[k] - pk1[k] for k in range(12))
                    if all(t >= 0 for t in target) and target in pair_sums:
                        for (a, b) in pair_sums[pk1]:
                            for (d, e) in pair_sums[target]:
                                names = sorted([int_names[a], int_names[b], int_names[d], int_names[e]])
                                if int_names[c_idx] not in names:
                                    results.append({
                                        'word': names,
                                        'target': int_names[c_idx],
                                        'type': 'A+B+D+E=C',
                                    })
                                    if len(results) >= max_results:
                                        return results

        return results

    def vector_symmetries(self) -> List[Dict]:
        """
        Find entries that are near-symmetric under primitive permutation.
        E.g., swapping Ð and Þ yields another valid entry.
        """
        results = []
        # Test all 2-cycle swaps of primitives
        for p1_idx in range(12):
            for p2_idx in range(p1_idx + 1, 12):
                # Only swap if cardinalities match
                if PRIM_CARDINALITIES[PRIMITIVES[p1_idx]] != PRIM_CARDINALITIES[PRIMITIVES[p2_idx]]:
                    continue
                p1, p2 = PRIMITIVES[p1_idx], PRIMITIVES[p2_idx]
                swapped_entries = 0
                examples = []
                for entry in self.valid_entries:
                    orig = resolve_all(entry)
                    if orig[p1] == orig[p2]:
                        continue
                    # Swap
                    swapped = dict(orig)
                    swapped[p1], swapped[p2] = swapped[p2], swapped[p1]
                    # Check if swapped tuple exists in catalog
                    sv = tuple(GLYPH_ORDINALS[PRIMITIVES[k]].get(swapped[PRIMITIVES[k]], 0) - 1 for k in range(12))
                    if sv in self.int_to_names:
                        swapped_entries += 1
                        if len(examples) < 3:
                            examples.append({
                                'original': entry.get('name', '?'),
                                'swapped': self.int_to_names[sv][0],
                            })
                if swapped_entries > 0:
                    results.append({
                        'swap': f'{p1}↔{p2}',
                        'count': swapped_entries,
                        'fraction': swapped_entries / self.n,
                        'examples': examples,
                    })
        results.sort(key=lambda x: -x['count'])
        return results

    def cluster_analysis(self, n_clusters: int = 10) -> Dict:
        """K-means clustering of the vector ensemble."""
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(self.matrix)

        # Analyze each cluster
        clusters = defaultdict(list)
        for i, (name, label) in enumerate(zip(self.names, labels)):
            clusters[int(label)].append(name)

        cluster_info = []
        for label in sorted(clusters.keys()):
            names_in = clusters[label]
            vecs_in = np.array([self.name_to_vec[n] for n in names_in if n in self.name_to_vec])
            centroid = vecs_in.mean(axis=0) if len(vecs_in) > 0 else np.zeros(12)
            cluster_info.append({
                'id': label,
                'size': len(names_in),
                'centroid': [float(x) for x in centroid],
                'centroid_tuple': vector_to_tuple_str(list(centroid), self.scheme),
                'sample_names': names_in[:8],
            })

        # Silhouette score
        try:
            from sklearn.metrics import silhouette_score
            sil = silhouette_score(self.matrix, labels)
        except Exception:
            sil = -1.0

        # PCA for 2D projection
        pca = PCA(n_components=2)
        proj = pca.fit_transform(self.matrix)

        return {
            'n_clusters': n_clusters,
            'silhouette_score': float(sil),
            'clusters': cluster_info,
            'pca_2d': [[float(x) for x in row] for row in proj],
            'labels': [int(l) for l in labels],
        }

    def gematria_sum_table(self, entries_of_interest: List[str]) -> Dict:
        """
        Compute ALL pairwise vector sums for a set of entries and see
        what they map to. This is the classic gematria "addition table."
        """
        names = entries_of_interest
        n = len(names)
        table = []
        for i in range(n):
            row = []
            for j in range(n):
                if names[i] in self.name_to_vec and names[j] in self.name_to_vec:
                    sum_vec = vec_add(self.name_to_vec[names[i]], self.name_to_vec[names[j]])
                    # Snap to nearest entry
                    snapped = vec_to_closest_glyph(sum_vec, self.scheme)
                    # Check if snapped exists
                    sv = tuple(GLYPH_ORDINALS[p].get(snapped[p], 0) - 1 for p in PRIMITIVES)
                    match = self.int_to_names.get(sv, [None])[0]
                    row.append({
                        'sum_vector': [round(x, 2) for x in sum_vec],
                        'snapped_tuple': vector_to_tuple_str(sum_vec, self.scheme),
                        'match': match,
                    })
                else:
                    row.append(None)
            table.append({'a': names[i], 'row': row})
        return {'table': table, 'names': names}

    def nearest_to_point(self, point: List[float], k: int = 10) -> List[Dict]:
        """Find k nearest catalog entries to an arbitrary vector point."""
        point_arr = np.array(point)
        dists = np.linalg.norm(self.matrix - point_arr, axis=1)
        idx = np.argsort(dists)[:k]
        results = []
        for i in idx:
            results.append({
                'name': self.names[i],
                'distance': float(dists[i]),
                'vector': [float(x) for x in self.vectors[i]],
                'tuple': vector_to_tuple_str(self.vectors[i], self.scheme),
            })
        return results

    def vector_centroid_of_set(self, entry_names: List[str]) -> Dict:
        """Compute the centroid vector of a set of entries, and what it snaps to."""
        vecs = []
        for name in entry_names:
            if name in self.name_to_vec:
                vecs.append(self.name_to_vec[name])
        if not vecs:
            return {'error': 'No valid entries found'}
        centroid = vec_mean(vecs)
        snapped = vec_to_closest_glyph(centroid, self.scheme)
        sv = tuple(GLYPH_ORDINALS[p].get(snapped[p], 0) - 1 for p in PRIMITIVES)
        match = self.int_to_names.get(sv, [None])[0]
        return {
            'input_names': entry_names,
            'input_count': len(vecs),
            'centroid': [round(x, 4) for x in centroid],
            'snapped_tuple': vector_to_tuple_str(centroid, self.scheme),
            'nearest_catalog_entry': match,
        }

    def hadamard_inverse(self, entry_name: str) -> Dict:
        """
        Find the "Hadamard inverse" — the entry whose Hadamard product with
        the given entry yields the all-ones vector (or closest to it).
        """
        if entry_name not in self.name_to_vec:
            return {'error': f'{entry_name} not found'}
        v = np.array(self.name_to_vec[entry_name])
        target = np.ones(12)
        # Ideal inverse: 1/v_i
        ideal = np.where(v != 0, target / v, 0)
        return self.nearest_to_point(list(ideal), k=5)


# ── Main ─────────────────────────────────────────────────────────

def run_full_gematria(output_dir: str = None):
    """Run the complete gematria analysis pipeline and save results."""
    if output_dir is None:
        output_dir = str(Path(__file__).resolve().parent.parent / 'gematria_output')
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 80)
    print("IG GEMATRIA — Full Vector Analysis")
    print("=" * 80)

    # Load
    entries = load_catalog()
    print(f"\n[1] Loaded {len(entries)} entries from catalog")

    # Build index
    idx = GematriaIndex(entries, scheme='ordinal')
    print(f"    Valid: {idx.n}, Unique integer vectors: {len(idx.int_to_names)}")

    # ── Spectral analysis ──
    print("\n[2] Spectral analysis (PCA)...")
    spectral = idx.spectral_analysis()
    with open(f'{output_dir}/spectral.json', 'w') as f:
        json.dump(spectral, f, indent=2)
    print(f"    Top 3 eigenvalues: {spectral['eigenvalues'][:3]}")
    print(f"    Cumulative variance (3 PCs): {spectral['cumulative_variance'][2]:.3f}")
    print(f"    Condition number: {spectral['condition_number']:.1f}")

    # ── Correlations ──
    print("\n[3] Primitive correlations...")
    corr = idx.primitive_correlations()
    with open(f'{output_dir}/correlations.json', 'w') as f:
        json.dump(corr, f, indent=2)
    for pair in corr['strongest_pairs'][:5]:
        print(f"    {pair['a']}↔{pair['b']}: {pair['correlation']:+.3f}")

    # ── Additive equations ──
    print("\n[4] Additive equations (A+B=C)...")
    equations = idx.find_additive_equations(max_results=500)
    with open(f'{output_dir}/additive_equations.json', 'w') as f:
        json.dump(equations, f, indent=2, default=str)
    print(f"    Found {len(equations)} equations")
    for eq in equations[:5]:
        print(f"    {eq['a']} + {eq['b']} = {eq['c']}")

    # ── Integer span ──
    print("\n[5] Integer span...")
    span = idx.find_integer_span()
    with open(f'{output_dir}/integer_span.json', 'w') as f:
        json.dump(span, f, indent=2)
    print(f"    Rank: {span['rank']}/12")
    print(f"    Coverage: {span['coverage_ratio']:.6f} ({span['occupied_int_vectors']}/{span['bounding_box_volume']})")

    # ── Symmetries ──
    print("\n[6] Vector symmetries (primitive swaps)...")
    syms = idx.vector_symmetries()
    with open(f'{output_dir}/symmetries.json', 'w') as f:
        json.dump(syms, f, indent=2)
    for s in syms[:5]:
        print(f"    {s['swap']}: {s['count']} entries swapped ({s['fraction']:.3%})")

    # ── Gematria words (length 3) ──
    print("\n[7] Gematria words (3-entry sums)...")
    words = idx.gematria_word_search(word_length=3, max_results=100)
    with open(f'{output_dir}/gematria_words.json', 'w') as f:
        json.dump(words, f, indent=2)
    print(f"    Found {len(words)} 3-word equations")
    for w in words[:5]:
        print(f"    {' + '.join(w['word'])} = {w['target']}")

    # ── Clustering ──
    print("\n[8] Cluster analysis...")
    clusters = idx.cluster_analysis(n_clusters=10)
    with open(f'{output_dir}/clusters.json', 'w') as f:
        json.dump(clusters, f, indent=2)
    print(f"    Silhouette: {clusters['silhouette_score']:.3f}")
    for c in clusters['clusters'][:5]:
        print(f"    Cluster {c['id']}: {c['size']} entries, centroid ≈ {c['centroid_tuple'][:60]}...")

    print(f"\n{'=' * 80}")
    print(f"Gematria complete. Results in: {output_dir}/")
    print(f"{'=' * 80}")

    return idx


if __name__ == '__main__':
    run_full_gematria()
