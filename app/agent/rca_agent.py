from app.tools.documents import search_documents
from app.tools.maintenance import get_maintenance
from app.tools.timeseries import get_timeseries


def run_rca(event: dict) -> dict:
    """
    RCA Copilot Agent（最小実装）
    - データ取得
    - 仮説生成（ルールベース）
    - 根拠付きブリーフ生成
    """

    asset_id = event["asset_id"]

    # --- 1. Context収集（ダミー） ---
    ts = get_timeseries(asset_id)
    maint = get_maintenance(asset_id)
    docs = search_documents(asset_id)

    # --- 2. 仮説生成（テンプレ） ---
    hypotheses = [
        {
            "hypothesis": "Recent maintenance caused sensor misalignment",
            "confidence": 0.68,
            "supporting_evidence": [
                f"Recent maintenance found: {maint['latest']}",
                "Vibration increased after maintenance",
            ],
            "counter_evidence": ["Similar maintenance did not always cause issues"],
            "missing_evidence": ["Post-maintenance calibration record"],
            "next_checks": [
                "Recalibrate vibration sensor",
                "Compare with adjacent tool sensors",
            ],
        },
        {
            "hypothesis": "Vacuum leak caused pressure anomaly",
            "confidence": 0.52,
            "supporting_evidence": ["Pressure drift detected in time-series"],
            "counter_evidence": ["No leak alarm triggered"],
            "missing_evidence": ["Leak check result"],
            "next_checks": ["Run leak check", "Inspect vacuum seals"],
        },
    ]

    # --- 3. 意思決定ブリーフ ---
    return {
        "ranked_hypotheses": hypotheses,
        "overall_uncertainty": "Medium",
        "policy": {"auto_stop": False, "human_in_the_loop": True},
    }
