import pandas as pd


def get_timeseries(asset_id: str) -> pd.DataFrame:
    """
    時系列データ取得（ダミー）
    """
    return pd.DataFrame(
        {
            "timestamp": ["t-3", "t-2", "t-1"],
            "vibration": [0.2, 0.3, 0.8],
            "pressure": [1.0, 1.1, 1.5],
        }
    )
