import re
from typing import Iterable, Sequence, Optional, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def normalize_skill_name(name: str) -> str:
    """
    Safely normalizes skill names for consistent vocabulary indexing:
    - Trims leading and trailing whitespace.
    - Converts to lowercase.
    - Collapses consecutive whitespace (e.g., spaces, tabs) to a single space.
    - Preserves distinct tokens (e.g., 'React' != 'React.js').
    """
    if not name or not isinstance(name, str):
        return ""
    # Strip whitespace, collapse multiple spaces, and lowercase
    cleaned = re.sub(r"\s+", " ", name.strip())
    return cleaned.lower()


def build_skill_vector(
    skills: Iterable[str],
    vocabulary: Sequence[str]
) -> np.ndarray:
    """
    Constructs a binary indicator vector (1.0 or 0.0) over the given normalized vocabulary.
    
    :param skills: Collection of skill names to encode
    :param vocabulary: Ordered sequence of unique normalized vocabulary skills
    :return: 1D NumPy array of length len(vocabulary)
    """
    if not vocabulary:
        return np.zeros(0, dtype=np.float64)

    norm_skills = {normalize_skill_name(s) for s in skills if normalize_skill_name(s)}
    vector = np.zeros(len(vocabulary), dtype=np.float64)
    
    for idx, vocab_skill in enumerate(vocabulary):
        if vocab_skill in norm_skills:
            vector[idx] = 1.0
            
    return vector


def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Computes cosine similarity between two 1D vectors using scikit-learn.
    
    Safely handles zero vectors without causing ZeroDivisionError, NaN, or exceptions:
    - If either vector has length 0, returns 0.0.
    - If either vector has norm 0.0 (contains no skills), returns 0.0.
    - Guarantees return value is normalized in the range [0.0, 1.0].
    
    :param vec_a: 1D NumPy array
    :param vec_b: 1D NumPy array
    :return: float in [0.0, 1.0]
    """
    if vec_a is None or vec_b is None:
        return 0.0

    vec_a = np.asarray(vec_a, dtype=np.float64)
    vec_b = np.asarray(vec_b, dtype=np.float64)

    if vec_a.size == 0 or vec_b.size == 0 or vec_a.shape != vec_b.shape:
        return 0.0

    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    # Zero vector handling: return 0.0 rather than causing division by zero or NaN
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    # Reshape vectors to 2D matrices (1, n_features) for sklearn cosine_similarity
    raw_sim = cosine_similarity(vec_a.reshape(1, -1), vec_b.reshape(1, -1))[0][0]

    # Handle numerical floating point imprecision and clamp to [0.0, 1.0]
    normalized_score = float(np.clip(raw_sim, 0.0, 1.0))
    return normalized_score


def calculate_directional_score(
    source_skills: Iterable[str],
    target_skills: Iterable[str],
    vocabulary: Optional[Sequence[str]] = None
) -> float:
    """
    Calculates directional cosine similarity:
    e.g., A_wants vs B_offers, or A_offers vs B_wants.
    
    :param source_skills: Skills from the requesting perspective (e.g., A_wants)
    :param target_skills: Skills from the providing perspective (e.g., B_offers)
    :param vocabulary: Optional shared vocabulary. If omitted, built dynamically from both sets.
    :return: float in [0.0, 1.0]
    """
    norm_source = [normalize_skill_name(s) for s in source_skills if normalize_skill_name(s)]
    norm_target = [normalize_skill_name(s) for s in target_skills if normalize_skill_name(s)]

    # If either side has no valid skills, directional score is safely 0.0
    if not norm_source or not norm_target:
        return 0.0

    if vocabulary is None:
        # Construct shared vocabulary dynamically from the combined unique normalized skills
        shared_vocab = sorted(list(set(norm_source) | set(norm_target)))
    else:
        # Use provided normalized vocabulary
        shared_vocab = [normalize_skill_name(v) for v in vocabulary if normalize_skill_name(v)]
        # If vocabulary doesn't cover all skills in source/target, augment with union to avoid missing dimensions
        missing = (set(norm_source) | set(norm_target)) - set(shared_vocab)
        if missing:
            shared_vocab = sorted(list(set(shared_vocab) | missing))

    if not shared_vocab:
        return 0.0

    vec_source = build_skill_vector(norm_source, shared_vocab)
    vec_target = build_skill_vector(norm_target, shared_vocab)

    return compute_cosine_similarity(vec_source, vec_target)
