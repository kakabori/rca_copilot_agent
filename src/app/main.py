from fastapi import FastAPI
from pydantic import BaseModel

from app.agent.rca_agent import run_rca

app = FastAPI(title="RCA Copilot Agent")


class RCARequest(BaseModel):
    asset_id: str
    timestamp: str
    anomaly_score: float
    top_features: list[str]


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/rca")
def rca(req: RCARequest):
    """
    異常イベントを受け取り、RCA意思決定ブリーフを返す
    """
    return run_rca(req.model_dump())
