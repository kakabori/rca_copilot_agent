from app.tools.documents import search_documents
from app.tools.maintenance import get_maintenance
from app.tools.timeseries import get_timeseries


def collect_context(event: dict) -> dict:
    """
    Evidence Collector / Context & Data Access Layer のフロント関数
    """
    asset_id = event["asset_id"]

    ts = get_timeseries(asset_id)
    maint = get_maintenance(asset_id)
    docs = search_documents(asset_id)

    context = {
        "timeseries": ts,
        "maintenance": maint,
        "documents": docs,
    }
    return context


def generate_initial_hypotheses(event: dict, context: dict) -> list[dict]:
    """
    Hypothesis Generator
    - event + context を見て、いくつかの仮説を生成する
    - データに基づいた複数の初期仮説のリストを返す
    - まだ厳密な評価はせず、それっぽい候補を広めに出す
    """

    # ルールの一覧を定義
    rules = [
        rule_recent_maintenance_misalignment,
        rule_vacuum_leak_pressure_anomaly,
    ]

    hypotheses: list[dict] = []

    for rule in rules:
        hypothesis = rule(event, context)
        if hypothesis is not None:
            hypotheses.append(hypothesis)

    return hypotheses


def rule_recent_maintenance_misalignment(event: dict, context: dict) -> dict | None:
    """
    ルール例: 最近の保全がセンサーのずれを引き起こした可能性
    - 保全履歴に最近の作業がある
    - 時系列データに保全後の振動増加が見られる
    """
    maint = context.get("maintenance", {})
    docs = context.get("documents", [])
    ts = context.get("timeseries", None)

    latest_maint = maint.get("latest", "")

    # 条件1: 直近メンテナンスが存在しない場合はこの仮説を出さない
    if not latest_maint:
        return None

    # 条件2: ドキュメントに「sensor」や「calibration」が含まれているものがあるか
    doc_hits = [d for d in docs if "sensor" in d.lower() or "calibraition" in d.lower()]

    # 条件3: 振動が増えている判定
    vibration_trend = "unknown"
    if ts is not None:
        vib_values = ts["vibration"]
        if vib_values.iloc[-1] > vib_values.iloc[0]:
            vibration_trend = "increasing"

    # 初期 confidence を 0.5 として、条件ごとに加点/減点
    confidence = 0.5
    if doc_hits:
        confidence += 0.1
    if vibration_trend == "increasing":
        confidence += 0.1

    confidence = min(confidence, 0.9)  # 上限を設定

    # Hypothesis オブジェクトを構築
    hypothesis = {
        "id": "hypothesis_maintenance_misalignment",
        "hypothesis": "Recent maintenance caused sensor misalignment",
        "confidence": confidence,
        "supporting_evidence": [f"Recent maintenance found: {latest_maint}"]
        + [f"Related document: {d}" for d in doc_hits]
        + (
            ["Vibration is increasing in recent time-series"]
            if vibration_trend == "increasing"
            else []
        ),
        "counter_evidence": ["Similar maintenance did not always cause issues"],
        "missing_evidence": ["Post-maintenance calibration record"],
        "next_checks": [
            "Recalibrate vibration sensor",
            "Compare with adjacent tool sensors",
        ],
    }

    return hypothesis


def rule_vacuum_leak_pressure_anomaly(event: dict, context: dict) -> dict | None:
    """
    ルール例: 真空漏れが圧力異常を引き起こしている可能性
    - 時系列データに圧力のドリフトが見られる
    - ドキュメントに過去の類似事例がある
    """

    ts = context.get("timeseries", None)
    docs = context.get("documents", [])
    top_features = event.get("top_features", [])

    # 条件1: top_features に pressure が含まれていなければ、この仮説は出さない
    if "pressure" not in [f.lower() for f in top_features]:
        return None

    # 条件2: pressure drift 判定
    pressure_drift = False
    if ts is not None:
        p_values = ts["pressure"]
        if p_values.iloc[-1] - p_values.iloc[0] > 0.3:
            pressure_drift = True

    # 条件3: ドキュメントに leak / vaccum などがあればヒントとして追加
    doc_hits = [d for d in docs if "leak" in d.lower() or "vacuum" in d.lower()]

    # いずれの条件も満たさない場合は仮説を出さない
    if not pressure_drift and not doc_hits:
        # pressure が top_features に入っているだけでは弱すぎると判断
        return None

    base_confidence = 0.4
    if pressure_drift:
        base_confidence += 0.2
    if doc_hits:
        base_confidence += 0.1

    confidence = min(base_confidence, 0.9)

    hypothesis = {
        "id": "hypothesis_vacuum_leak",
        "hypothesis": "Vacuum leak caused pressure anomaly",
        "confidence": confidence,
        "supporting_evidence": []
        + (["Pressure drift detected in time-series"] if pressure_drift else [])
        + [f"Related document: {d}" for d in doc_hits],
        "counter_evidence": ["No leak alarm triggered"],
        "missing_evidence": ["Leak check result"],
        "next_checks": ["Run leak check", "Inspect vacuum seals"],
    }

    return hypothesis


def evaluate_hypotheses(
    hypotheses: list[dict], context: dict, event: dict
) -> list[dict]:
    """
    Hypothesis Evaluator
    - 各仮説の confidence / evidence を見直す
    - 将来的には timestamp, anomaly_score, top_fetures を使って調整
    """
    # 後で TDD で「anomaly_score > 0.9 のときは confidence を少し上げる」などを追加可能
    return hypotheses


def build_decision_brief(hypotheses: list[dict], context: dict, event: dict) -> dict:
    """
    Decision Brief Builder
    - ranked_hypotheses の並べ替え
    - overall_uncertainty の計算
    - agent_policy / context_snapshot などの付加情報生成
    """

    # 1. ranked_hypotheses の並べ替え
    ranked = sorted(hypotheses, key=lambda x: x.get("confidence", 0.0), reverse=True)

    # 2. overall_uncertainty の計算（ダミー）
    overlall_uncertainty = "Medium"

    # 3. policy
    policy = {
        "auto_stop": False,
        "human_in_the_loop": True,
    }

    # (将来) どのデータを見たかの snapshot を載せる
    # context_snapshot = {
    #     "timeseries_window": {
    #         "start": "...",
    #         "end": "...",
    #         "used_signals": ["vibration", "pressure"],
    #     },
    #     "used_documents": [
    #         "incident_report_20225-01-05.md",
    #         "sensor_calibration_guide.md",
    #     ],
    #     "used_maintenance_records": ["#3421"],
    # }

    return {
        "ranked_hypotheses": ranked,
        "overall_uncertainty": overlall_uncertainty,
        "policy": policy,
        # "context_snapshot": context_snapshot,
        # "trace_id": "abc123",  # 将来はリクエストごとに生成する
    }


def run_rca(event: dict) -> dict:
    """
    RCA Copilot Agent (オーケストレーター)
    1. Context収集
    2. 仮説生成
    3. 仮説評価
    4. 意思決定ブリーフ構築
    """

    # --- 1. Context収集 (ダミー) ---
    context = collect_context(event)

    # --- 2. 仮説生成 (Hypothesis Generator) ---
    raw_hypotheses = generate_initial_hypotheses(event, context)

    # --- 3. 仮説評価 (Hypothesis Evaluator) ---
    evaluated_hypotheses = evaluate_hypotheses(raw_hypotheses, context, event)

    # --- 4. 意思決定ブリーフ構築 (Decision Brief Builder) ---
    decision_brief = build_decision_brief(evaluated_hypotheses, context, event)

    return decision_brief
