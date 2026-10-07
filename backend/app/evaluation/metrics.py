import math
from typing import List, Set, Dict, Any, Optional


def precision_at_k(
    recommended_ids: List[Any],
    relevant_ids: Set[Any],
    k: int = 5,
) -> float:
    """
    Computes Precision@K:
    
        Precision@K = |recommended[:K] ∩ relevant| / K
        
    Handles cases where fewer than K candidates are available safely
    by dividing by K (standard IR definition).
    Returns 0.0 if K <= 0 or recommended_ids is empty.
    Bounded in [0.0, 1.0].
    """
    if k <= 0 or not recommended_ids:
        return 0.0

    top_k = recommended_ids[:k]
    hits = sum(1 for item in top_k if item in relevant_ids)
    return float(hits) / float(k)


def recall_at_k(
    recommended_ids: List[Any],
    relevant_ids: Set[Any],
    k: int = 5,
) -> float:
    """
    Computes Recall@K:
    
        Recall@K = |recommended[:K] ∩ relevant| / |relevant|
        
    If total relevant items == 0:
        Returns 0.0 safely without ZeroDivisionError.
    Bounded in [0.0, 1.0].
    """
    if k <= 0 or not recommended_ids or not relevant_ids:
        return 0.0

    top_k = recommended_ids[:k]
    hits = sum(1 for item in top_k if item in relevant_ids)
    return float(hits) / float(len(relevant_ids))


def ndcg_at_k(
    recommended_ids: List[Any],
    relevance_grades: Dict[Any, float],
    k: int = 5,
) -> float:
    """
    Computes Normalized Discounted Cumulative Gain (NDCG@K):
    
        DCG@K  = sum_{i=1}^{min(K, |rec|)}  grade_i / log2(i + 1)
        IDCG@K = sum_{i=1}^{min(K, |ideal|)} ideal_grade_i / log2(i + 1)
        NDCG@K = DCG@K / IDCG@K (or 0.0 if IDCG == 0.0)
        
    Uses base-2 logarithm discounting.
    Guarantees mathematically bounded in [0.0, 1.0].
    """
    if k <= 0 or not recommended_ids or not relevance_grades:
        return 0.0

    top_k = recommended_ids[:k]

    # Calculate DCG@K
    dcg = 0.0
    for idx, item in enumerate(top_k):
        grade = relevance_grades.get(item, 0.0)
        if grade > 0.0:
            dcg += grade / math.log2(idx + 2)  # idx 0 -> log2(2) = 1.0

    # Calculate Ideal DCG@K (best possible ordering of all available relevant items)
    ideal_grades = sorted(
        [g for g in relevance_grades.values() if g > 0.0],
        reverse=True
    )[:k]

    if not ideal_grades:
        return 0.0

    idcg = sum(g / math.log2(idx + 2) for idx, g in enumerate(ideal_grades))

    if idcg <= 0.0:
        return 0.0

    ndcg = dcg / idcg
    return float(max(0.0, min(1.0, ndcg)))


def hit_rate_at_k(
    recommended_ids: List[Any],
    relevant_ids: Set[Any],
    k: int = 5,
) -> float:
    """
    Computes individual HitRate@K:
    
        HitRate@K = 1.0 if |recommended[:K] ∩ relevant| > 0 else 0.0
        
    When averaged across a cohort of evaluated users, yields cohort HitRate@K.
    """
    if k <= 0 or not recommended_ids or not relevant_ids:
        return 0.0

    top_k = recommended_ids[:k]
    return 1.0 if any(item in relevant_ids for item in top_k) else 0.0


def check_reciprocal_overlap(
    user_wants: Set[str],
    user_offers: Set[str],
    cand_wants: Set[str],
    cand_offers: Set[str],
) -> bool:
    """
    Determines if User A and Candidate B have two-way skill exchange overlap:
    
        A wants a skill B offers (A_wants ∩ B_offers != ∅)
        AND
        A offers a skill B wants (A_offers ∩ B_wants != ∅)
    """
    # Normalize skill names for comparison (case-insensitive, trimmed)
    norm_u_wants = {s.strip().lower() for s in user_wants if s}
    norm_u_offers = {s.strip().lower() for s in user_offers if s}
    norm_c_wants = {s.strip().lower() for s in cand_wants if s}
    norm_c_offers = {s.strip().lower() for s in cand_offers if s}

    has_forward = bool(norm_u_wants & norm_c_offers)
    has_reverse = bool(norm_u_offers & norm_c_wants)

    return has_forward and has_reverse


def reciprocity_at_k(
    candidate_skills_list: List[Dict[str, Set[str]]],
    user_wants: Set[str],
    user_offers: Set[str],
    k: int = 5,
) -> float:
    """
    Computes Reciprocity@K:
    
    Measures the proportion of top-K recommended candidates who possess
    two-way skill exchange compatibility with the authenticated student:
    
        Reciprocity@K = count(reciprocal candidates in top K) / min(K, len(candidates))
        
    If no candidates are available, returns 0.0.
    Bounded strictly in [0.0, 1.0].
    """
    if k <= 0 or not candidate_skills_list:
        return 0.0

    top_k = candidate_skills_list[:k]
    reciprocal_count = 0

    for cand in top_k:
        c_wants = cand.get("skills_wanted", set())
        c_offers = cand.get("skills_offered", set())
        if check_reciprocal_overlap(user_wants, user_offers, c_wants, c_offers):
            reciprocal_count += 1

    denominator = float(min(k, len(candidate_skills_list)))
    return float(reciprocal_count) / denominator if denominator > 0 else 0.0


def evaluate_ranking(
    recommended_ids: List[Any],
    relevant_ids: Set[Any],
    relevance_grades: Dict[Any, float],
    candidate_skills_list: List[Dict[str, Set[str]]],
    user_wants: Set[str],
    user_offers: Set[str],
    k_values: List[int] = [3, 5, 10],
) -> Dict[str, float]:
    """
    Computes complete suite of evaluation metrics across specified K cutoffs:
    Precision@K, Recall@K, NDCG@K, HitRate@K, and Reciprocity@K.
    """
    results: Dict[str, float] = {}

    for k in k_values:
        results[f"precision@{k}"] = precision_at_k(recommended_ids, relevant_ids, k=k)
        results[f"recall@{k}"] = recall_at_k(recommended_ids, relevant_ids, k=k)
        results[f"ndcg@{k}"] = ndcg_at_k(recommended_ids, relevance_grades, k=k)
        results[f"hit_rate@{k}"] = hit_rate_at_k(recommended_ids, relevant_ids, k=k)
        results[f"reciprocity@{k}"] = reciprocity_at_k(candidate_skills_list, user_wants, user_offers, k=k)

    return results
