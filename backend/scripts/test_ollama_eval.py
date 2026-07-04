"""Quick Ollama + evaluation smoke test."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ai_evaluation_service import AIEvaluationService
from app.services.evaluation_service import evaluate_assessment_file
from app.services.ollama_client import OllamaClient


def main():
    client = OllamaClient()
    print("readiness:", client.readiness_message())
    print("models:", client.list_models())

    try:
        r = client.chat_json(
            "You return valid JSON only.",
            'Return exactly: {"test": true}',
            temperature=0.0,
        )
        print("chat_json ok:", r)
    except Exception as exc:
        print("chat_json FAILED:", exc)
        return 1

    assessments_dir = Path("assessments")
    files = [
        f
        for f in assessments_dir.rglob("*.json")
        if not f.name.endswith("_evaluation.json") and "adaptive" not in str(f)
    ]
    print("assessment files:", len(files))

    if not files:
        print("No assessment files to test.")
        return 0

    target = Path("assessments/1/ad34fd0a-50ac-4cff-b2d6-a380a2a7f082.json")
    if target.exists():
        print("AI evaluate (adaptive failed):", target)
    elif files:
        target = files[0]
        print("AI evaluate:", target)
    else:
        print("No assessment files to test.")
        return 0

    try:
        svc = AIEvaluationService()
        result = svc.evaluate_assessment(target)
        score = result.get("overall_analysis", {}).get("final_score_out_of_100")
        method = result.get("evaluation_method", "?")
        print("AI evaluation OK — score:", score, "method:", method)
    except Exception as exc:
        print("AI evaluation FAILED:", type(exc).__name__, exc)
        return 1

    failed = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("status") == "evaluation_failed":
            failed.append(f)

    print("evaluation_failed count:", len(failed))
    if failed:
        print("Re-evaluating:", failed[0])
        try:
            r = evaluate_assessment_file(failed[0])
            print("Re-eval score:", r.get("overall_analysis", {}).get("final_score_out_of_100"))
        except Exception as exc:
            print("Re-eval FAILED:", exc)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
