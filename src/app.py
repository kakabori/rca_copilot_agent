# app.py
from fastapi import FastAPI
from agent import run_rca_agent

app = FastAPI()

@app.post("/rca")
def rca_endpoint(event: dict):
    result = run_rca_agent(event)
    return result
