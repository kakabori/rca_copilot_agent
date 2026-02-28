from datetime import datetime, timedelta

import pandas as pd

from app.agent.rca_agent import generate_initial_hypotheses


def make_dummy_context() -> dict:
    start = datetime.now()
    return {
        "timeseries": pd.DataFrame(
            {
                "timestamp": [start + timedelta(seconds=i) for i in range(3)],
                "vibration": [0.2, 0.3, 0.8],
                "pressure": [1.0, 1.1, 1.5],
            }
        ),
        "maintenance": {
            "latest": "MaintenanceRecord#3421 (2 days ago)",
            "history": ["#3401", "#3388"],
        },
        "documents": [
            "Past incident: vibration spike after sensor replacement",
            "Procedure: sensor calibration steps",
        ],
    }


def test_generate_initial_hypotheses():
    event = {
        "asset_id": "ETCHER_01",
        "timestamp": "2024-06-01T12:00:00Z",
        "anomaly_score": 0.92,
        "top_features": ["vibration", "pressure"],
    }
    context = make_dummy_context()

    hypotheses = generate_initial_hypotheses(event, context)

    ids = {h["id"] for h in hypotheses}
    assert "hypothesis_maintenance_misalignment" in ids
    assert "hypothesis_vacuum_leak" in ids


def test_hypotheses_have_required_fields():
    event = {
        "asset_id": "ETCHER_01",
        "timestamp": "2024-06-01T12:00:00Z",
        "anomaly_score": 0.92,
        "top_features": ["vibration", "pressure"],
    }
    context = make_dummy_context()

    hypotheses = generate_initial_hypotheses(event, context)

    required_keys = {
        "id",
        "hypothesis",
        "confidence",
        "supporting_evidence",
        "counter_evidence",
        "missing_evidence",
        "next_checks",
    }

    for h in hypotheses:
        assert required_keys.issubset(h.keys())
        assert 0.0 <= h["confidence"] <= 1.0


if __name__ == "__main__":
    test_generate_initial_hypotheses()
