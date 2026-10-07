import uuid
import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.evaluation.dataset import EvaluationDataset
from app.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    ndcg_at_k,
    hit_rate_at_k,
    reciprocity_at_k,
)
from app.recommendation.hybrid import get_hybrid_recommendations
from app.recommendation.collaborative import get_collaborative_recommendations

logger = logging.getLogger("skillswap.evaluation.experiment")


@dataclass
class ModelConfig:
    name: str
    description: str
    content_weight: Optional[float] = None
    collaborative_weight: Optional[float] = None
    is_collaborative_only: bool = False


# Documented comparison suite required by Stage 6:
EVALUATION_MODELS: List[ModelConfig] = [
    ModelConfig(
        name="CONTENT_ONLY",
        description="Stage 5A pure reciprocal skill matching (100% content, 0% collaborative)",
        content_weight=1.0,
        collaborative_weight=0.0,
    ),
    ModelConfig(
        name="COLLABORATIVE_ONLY",
        description="Stage 5D pure user-user collaborative filtering based on interactions",
        is_collaborative_only=True,
    ),
    ModelConfig(
        name="HYBRID_80_20",
        description="Hybrid weighting: 80% content-based reciprocal, 20% collaborative",
        content_weight=0.80,
        collaborative_weight=0.20,
    ),
    ModelConfig(
        name="HYBRID_70_30",
        description="Production baseline hybrid: 70% content-based reciprocal, 30% collaborative",
        content_weight=0.70,
        collaborative_weight=0.30,
    ),
    ModelConfig(
        name="HYBRID_60_40",
        description="Hybrid weighting: 60% content-based reciprocal, 40% collaborative",
        content_weight=0.60,
        collaborative_weight=0.40,
    ),
    ModelConfig(
        name="HYBRID_50_50",
        description="Balanced hybrid: 50% content-based reciprocal, 50% collaborative",
        content_weight=0.50,
        collaborative_weight=0.50,
    ),
]


def run_model_evaluation(
    model: ModelConfig,
    dataset: EvaluationDataset,
    db: Session,
    k_values: List[int] = [3, 5, 10],
    evaluate_user_ids: Optional[List[uuid.UUID]] = None,
) -> Dict[str, Any]:
    """
    Evaluates a specific model configuration across target users in the dataset.
    
    Returns macro-averaged metrics:
    - Precision@K
    - Recall@K
    - NDCG@K
    - HitRate@K
    - Reciprocity@K
    for each K in k_values.
    """
    max_k = max(k_values)
    user_ids = evaluate_user_ids or dataset.evaluable_user_ids

    # Accumulators for macro-averaging
    metric_sums: Dict[str, float] = {
        f"{m}@{k}": 0.0
        for k in k_values
        for m in ["precision", "recall", "ndcg", "hit_rate", "reciprocity"]
    }

    evaluated_count = 0
    cold_start_served = 0

    for uid in user_ids:
        user_prof = dataset.users.get(uid)
        if not user_prof:
            continue

        relevant_ids = user_prof.relevant_candidate_ids
        relevance_grades = user_prof.relevance_grades
        user_wants = user_prof.skills_wanted
        user_offers = user_prof.skills_offered

        # Retrieve model recommendations
        if model.is_collaborative_only:
            recs = get_collaborative_recommendations(user_id=uid, db=db, limit=max_k)
            rec_ids = [r.candidate_id for r in recs]
            cand_skills_list = [
                {
                    "skills_wanted": set(r.skills_wanted or []),
                    "skills_offered": set(r.skills_offered or []),
                }
                for r in recs
            ]
        else:
            cw = 0.70 if model.content_weight is None else model.content_weight
            collab_w = 0.30 if model.collaborative_weight is None else model.collaborative_weight
            recs = get_hybrid_recommendations(
                user_id=uid,
                db=db,
                limit=max_k,
                content_weight=cw,
                collaborative_weight=collab_w,
            )
            rec_ids = [r.candidate_id for r in recs]
            cand_skills_list = [
                {
                    "skills_wanted": set(r.skills_wanted or []),
                    "skills_offered": set(r.skills_offered or []),
                }
                for r in recs
            ]

        if len(rec_ids) > 0 and user_prof.is_cold_start:
            cold_start_served += 1

        # Calculate metrics for each cutoff K
        for k in k_values:
            metric_sums[f"precision@{k}"] += precision_at_k(rec_ids, relevant_ids, k=k)
            metric_sums[f"recall@{k}"] += recall_at_k(rec_ids, relevant_ids, k=k)
            metric_sums[f"ndcg@{k}"] += ndcg_at_k(rec_ids, relevance_grades, k=k)
            metric_sums[f"hit_rate@{k}"] += hit_rate_at_k(rec_ids, relevant_ids, k=k)
            metric_sums[f"reciprocity@{k}"] += reciprocity_at_k(
                cand_skills_list, user_wants, user_offers, k=k
            )

        evaluated_count += 1

    # Macro-average across evaluated users
    macro_metrics: Dict[str, float] = {}
    denominator = float(evaluated_count) if evaluated_count > 0 else 1.0

    for metric_name, total_val in metric_sums.items():
        macro_metrics[metric_name] = round(total_val / denominator, 4)

    return {
        "model_name": model.name,
        "description": model.description,
        "content_weight": model.content_weight,
        "collaborative_weight": model.collaborative_weight,
        "evaluated_users_count": evaluated_count,
        "cold_start_served_count": cold_start_served,
        "metrics": macro_metrics,
    }
