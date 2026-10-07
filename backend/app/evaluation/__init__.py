"""
SkillSwap AI Recommendation Evaluation Module (Stage 6)
Isolated experimental framework for comparing recommendation algorithms,
calculating ranking metrics, and evaluating hybrid weight configurations.
"""

from app.evaluation.relevance import (
    RelevanceCriterion,
    get_user_relevance_map,
    DEFAULT_POSITIVE_TYPES,
)
from app.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    ndcg_at_k,
    hit_rate_at_k,
    reciprocity_at_k,
    evaluate_ranking,
)
from app.evaluation.dataset import (
    EvaluationDataset,
    build_evaluation_dataset,
)
from app.evaluation.experiment import (
    ModelConfig,
    EVALUATION_MODELS,
    run_model_evaluation,
)

from app.evaluation.runner import run_full_evaluation

__all__ = [
    "RelevanceCriterion",
    "get_user_relevance_map",
    "DEFAULT_POSITIVE_TYPES",
    "precision_at_k",
    "recall_at_k",
    "ndcg_at_k",
    "hit_rate_at_k",
    "reciprocity_at_k",
    "evaluate_ranking",
    "EvaluationDataset",
    "build_evaluation_dataset",
    "ModelConfig",
    "EVALUATION_MODELS",
    "run_model_evaluation",
    "run_full_evaluation",
]
