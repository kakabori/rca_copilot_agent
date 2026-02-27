# agent.py
from tools import (
    get_recent_timeseries,
    get_maintenance_history,
    search_documents
)

def run_rca_agent(event: dict):
    asset_id = event["asset_id"]

    # 1. 仮説生成（超シンプル）
    hypotheses = [
        "Side effect of recent maintenance",
        "Sensor misalignment or degradation",
        "Vacuum leak or pump degradation"
    ]

    results = []

    for h in hypotheses:
        evidence = collect_evidence(asset_id, h)
        evaluated = evaluate_hypothesis(h, evidence)
        results.append(evaluated)

    # 信頼度順に並べる
    ranked = sorted(results, key=lambda x: x["confidence"], reverse=True)

    return {
        "asset_id": asset_id,
        "ranked_hypotheses": ranked,
        "overall_uncertainty": "Medium",
        "policy": {
            "auto_stop": False,
            "human_in_the_loop": True
        }
    }


def collect_evidence(asset_id, hypothesis):
    return {
        "timeseries": get_recent_timeseries(asset_id),
        "maintenance": get_maintenance_history(asset_id),
        "documents": search_documents(hypothesis)
    }


def evaluate_hypothesis(hypothesis, evidence):
    support = []
    counter = []
    missing = []

    # 雑でもOK：重要なのは「構造」
    if "maintenance" in hypothesis.lower() and evidence["maintenance"]:
        support.append("Recent maintenance found")
    else:
        counter.append("No clear maintenance correlation")

    if not evidence["documents"]:
        missing.append("Relevant incident report not found")

    confidence = 0.6 if support else 0.4

    return {
        "hypothesis": hypothesis,
        "confidence": confidence,
        "supporting_evidence": support,
        "counter_evidence": counter,
        "missing_evidence": missing,
        "next_checks": suggest_next_checks(hypothesis)
    }


def suggest_next_checks(hypothesis):
    if "maintenance" in hypothesis.lower():
        return ["Check maintenance notes", "Verify sensor calibration"]
    if "vacuum" in hypothesis.lower():
        return ["Run leak check", "Compare pump baseline"]
    return ["Inspect sensor signals"]