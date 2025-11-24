from typing import List

from fastapi import FastAPI, Query, Body
from agent import generate_insight, generate_insight_batch
from models import MarketRiskSnapshot,default_MarketRiskSnapshot

app = FastAPI(
    title="Market Risk AI Service",
    description="AI agent & RAG pipeline for Market-Risk system",
    version="1.0.0",

    # Custom Swagger paths
    docs_url="/swagger-ui",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/insights", summary="Generate AI-driven risk insights for a risk snapshot.")
async def insights(
    snapshot: MarketRiskSnapshot = Body(default_MarketRiskSnapshot, description="The request payload"),
    type: str = Query("general-summary", description="Type of insight")
):
    return generate_insight(snapshot, type)

@app.post("/insights-batch", summary="Generate AI-driven risk insights for a risk batch")
async def insight_batch(
    snapshot: List[MarketRiskSnapshot] = Body([default_MarketRiskSnapshot], description="The request payload"),
    type: str = Query("general-summary", description="Type of insight")
):
    return generate_insight_batch(snapshot, type)