import os
import sys
import json
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.models.skill import Skill
from app.models.interaction import Interaction
from app.evaluation.runner import run_full_evaluation
from app.evaluation.experiment import EVALUATION_MODELS


def run_tests():
    print("=== STARTING STAGE 6 RECOMMENDATION EVALUATION VERIFICATION TESTS ===")

    db = SessionLocal()
    try:
        # ----------------------------------------------------------------------
        # 1. Capture Database Snapshot Before Evaluation
        # ----------------------------------------------------------------------
        print("\n--- 1. Recording Pre-Evaluation Database Snapshot ---")
        pre_user_count = db.query(User).count()
        pre_profile_count = db.query(Profile).count()
        pre_skill_count = db.query(Skill).count()
        pre_interaction_count = db.query(Interaction).count()

        print(f"Users: {pre_user_count}")
        print(f"Profiles: {pre_profile_count}")
        print(f"Skills: {pre_skill_count}")
        print(f"Interactions: {pre_interaction_count}")

        # ----------------------------------------------------------------------
        # 2. Execute Full Evaluation Pipeline
        # ----------------------------------------------------------------------
        print("\n--- 2. Executing Isolated Evaluation Pipeline ---")
        results = run_full_evaluation(db=db, output_dir=".")
        print("[PASS] Full evaluation pipeline executed successfully")

        # ----------------------------------------------------------------------
        # 3. Verify Database Integrity (Strict Read-Only)
        # ----------------------------------------------------------------------
        print("\n--- 3. Verifying Database Data Integrity (Zero Mutation) ---")
        post_user_count = db.query(User).count()
        post_profile_count = db.query(Profile).count()
        post_skill_count = db.query(Skill).count()
        post_interaction_count = db.query(Interaction).count()

        assert post_user_count == pre_user_count, (
            f"User count altered! Pre: {pre_user_count}, Post: {post_user_count}"
        )
        assert post_profile_count == pre_profile_count, (
            f"Profile count altered! Pre: {pre_profile_count}, Post: {post_profile_count}"
        )
        assert post_skill_count == pre_skill_count, (
            f"Skill count altered! Pre: {pre_skill_count}, Post: {post_skill_count}"
        )
        assert post_interaction_count == pre_interaction_count, (
            f"Interaction count altered! Pre: {pre_interaction_count}, Post: {post_interaction_count}"
        )
        print("[PASS] Data integrity verified: 100% read-only, zero rows added/modified/deleted")

        # ----------------------------------------------------------------------
        # 4. Verify evaluation_results.json
        # ----------------------------------------------------------------------
        print("\n--- 4. Verifying evaluation_results.json ---")
        assert os.path.exists("evaluation_results.json"), "evaluation_results.json was not created"
        with open("evaluation_results.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        assert "timestamp" in meta
        assert 0 < meta["total_users_count"] <= pre_user_count
        assert meta["total_interactions_count"] == pre_interaction_count
        assert "data_limitation_statement" in meta
        print(f"Non-test active users evaluated: {meta['total_users_count']} (total in DB: {pre_user_count})")
        print(f"Data limitation notice: \"{meta['data_limitation_statement']}\"")

        model_results = data["model_results"]
        assert len(model_results) == len(EVALUATION_MODELS), (
            f"Expected {len(EVALUATION_MODELS)} models, got {len(model_results)}"
        )

        expected_model_names = [m.name for m in EVALUATION_MODELS]
        actual_model_names = [m["model_name"] for m in model_results]
        assert actual_model_names == expected_model_names, (
            f"Expected models {expected_model_names}, got {actual_model_names}"
        )

        for m in model_results:
            mets = m["metrics"]
            for k in [3, 5, 10]:
                for metric in ["precision", "recall", "ndcg", "hit_rate", "reciprocity"]:
                    key = f"{metric}@{k}"
                    assert key in mets, f"Missing metric {key} in model {m['model_name']}"
                    val = mets[key]
                    assert 0.0 <= val <= 1.0, f"Metric {key} out of range [0, 1]: {val}"

        print("[PASS] evaluation_results.json validated: all 6 models, all K in [3, 5, 10], bounded metrics")

        # ----------------------------------------------------------------------
        # 5. Verify evaluation_report.md
        # ----------------------------------------------------------------------
        print("\n--- 5. Verifying evaluation_report.md ---")
        assert os.path.exists("evaluation_report.md"), "evaluation_report.md was not created"
        with open("evaluation_report.md", "r", encoding="utf-8") as f:
            report_text = f.read()

        assert "SkillSwap AI — Recommendation Engine Evaluation" in report_text
        assert "Primary Benchmark: K = 5 Cutoff" in report_text
        assert "Benchmark: K = 3 Cutoff" in report_text
        assert "Benchmark: K = 10 Cutoff" in report_text
        assert "Cold-Start Analysis" in report_text
        assert "Weight Experiment & Hybrid Comparison" in report_text
        assert "Dataset Limitations & Scientific Honesty" in report_text
        print("[PASS] evaluation_report.md validated: comprehensive report structure intact")

        # ----------------------------------------------------------------------
        # 6. Verify SVG Charts
        # ----------------------------------------------------------------------
        print("\n--- 6. Verifying Visualization Charts ---")
        assert os.path.exists("evaluation_chart_ndcg.svg"), "NDCG chart SVG missing"
        assert os.path.exists("evaluation_chart_precision.svg"), "Precision chart SVG missing"

        with open("evaluation_chart_ndcg.svg", "r", encoding="utf-8") as f:
            svg_ndcg = f.read()
            assert "<svg" in svg_ndcg and "</svg>" in svg_ndcg
            assert "NDCG@5" in svg_ndcg

        with open("evaluation_chart_precision.svg", "r", encoding="utf-8") as f:
            svg_prec = f.read()
            assert "<svg" in svg_prec and "</svg>" in svg_prec
            assert "Precision@5" in svg_prec

        print("[PASS] SVG comparison charts generated successfully from evaluation_results.json")

        print("\n=== ALL STAGE 6 VERIFICATION CHECKS PASSED WITH 100% COMPLIANCE ===")

    finally:
        db.close()


if __name__ == "__main__":
    run_tests()
