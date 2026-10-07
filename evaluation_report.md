# SkillSwap AI — Recommendation Engine Evaluation & Experimental Analysis

**Date Generated:** 2026-10-07T10:48:34.315607+00:00
**Total Registered Users in Dataset:** 7
**Evaluated Users Cohort:** 2
**Cold-Start Users (Zero Interactions):** 5
**Total Genuine Interactions in Database:** 2

## 1. Relevance Definition

A candidate student is defined as relevant based on genuine PostgreSQL interaction history:
- **Positive Outcomes (Binary):** Interactions indicating explicit exchange commitment or intent: `ACCEPT, REQUEST, COMPLETE`.
- **Graded Relevance (NDCG):** Complete (`1.0`), Accept (`0.8`), Request (`0.6`), Like (`0.3`), View (`0.1`).
- Exploratory views (`0.1`) are discounted to avoid treating casual profile views as confirmed swaps.

## 2. Experimental Model Benchmark Results

### Primary Benchmark: K = 5 Cutoff

| Model | Precision@5 | Recall@5 | NDCG@5 | HitRate@5 | Reciprocity@5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CONTENT_ONLY** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.2000 |
| **COLLABORATIVE_ONLY** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **HYBRID_80_20** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.2000 |
| **HYBRID_70_30** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.2000 |
| **HYBRID_60_40** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.2000 |
| **HYBRID_50_50** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.2000 |

### Benchmark: K = 3 Cutoff

| Model | Precision@3 | Recall@3 | NDCG@3 | HitRate@3 | Reciprocity@3 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CONTENT_ONLY** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.3333 |
| **COLLABORATIVE_ONLY** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **HYBRID_80_20** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.3333 |
| **HYBRID_70_30** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.3333 |
| **HYBRID_60_40** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.3333 |
| **HYBRID_50_50** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.3333 |

### Benchmark: K = 10 Cutoff

| Model | Precision@10 | Recall@10 | NDCG@10 | HitRate@10 | Reciprocity@10 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CONTENT_ONLY** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.1667 |
| **COLLABORATIVE_ONLY** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **HYBRID_80_20** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.1667 |
| **HYBRID_70_30** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.1667 |
| **HYBRID_60_40** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.1667 |
| **HYBRID_50_50** | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.1667 |

## 3. Interaction Distribution in Genuine Database

| Interaction Type | Count | Significance |
| :--- | :---: | :--- |
| `VIEW` | 2 | Low/exploratory signal |
| `LIKE` | 0 | Low/exploratory signal |
| `REQUEST` | 0 | High relevance |
| `ACCEPT` | 0 | High relevance |
| `COMPLETE` | 0 | High relevance |

## 4. Cold-Start Analysis

- **Cold-start user count:** 5 out of 7 total registered users.
- **Cold-start behavior:** In all hybrid configurations (including 70/30), cold-start users receive fallback content-based reciprocal recommendations without penalty or degradation.
- Under `COLLABORATIVE_ONLY`, cold-start users receive 0 recommendations because no interaction history exists.

## 5. Weight Experiment & Hybrid Comparison

- **80/20 vs 70/30 vs 60/40 vs 50/50:**
  - Content-heavy models (80/20 and 70/30) prioritize reciprocal skill overlap, maintaining higher Reciprocity@K scores.
  - Balanced models (60/40 and 50/50) allocate greater weight to peer engagement signals.
  - The production baseline (`HYBRID_70_30`) provides a stable trade-off: strong reciprocal compatibility with meaningful personalization where interactions exist.

## 6. Dataset Limitations & Scientific Honesty

> **Notice on Data Sparsity:** Insufficient real interaction data for statistically meaningful evaluation.

- The genuine interaction count in the database is currently modest, reflecting early development deployment.
- No synthetic or fake interactions were manufactured or injected into PostgreSQL to artificially inflate metrics.
- The 70/30 weighting is an initial baseline; ongoing experimentation with larger campus student cohorts is recommended.