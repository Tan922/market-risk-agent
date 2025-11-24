import os
import asyncio
import json
from fastapi import FastAPI
from pydantic import parse_obj_as
from aiokafka import AIOKafkaConsumer
from models import MarketRiskSnapshot
from vectors import FaissStore
from graph import build_graph
from llm import call_hf_inference
from producer import emit_enriched

app = FastAPI()
BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9093")
TOPIC_IN = os.environ.get("KAFKA_INPUT_TOPIC", "market-risk-snapshots")
TOPIC_ENRICH = os.environ.get("KAFKA_ENRICH_TOPIC", "market-risk-enriched")

@app.on_event("startup")
async def startup_event():
    # Start consumer in background
    asyncio.create_task(consumer_loop())

@app.get("/health")
async def health():
    return {"status": "ok"}

async def consumer_loop():
    consumer = AIOKafkaConsumer(
        TOPIC_IN,
        bootstrap_servers=BOOTSTRAP,
        group_id="market-risk-rag-group",
        enable_auto_commit=True
    )
    await consumer.start()
    store = FaissStore()
    try:
        async for msg in consumer:
            try:
                payload = json.loads(msg.value.decode("utf-8"))
                snap = parse_obj_as(MarketRiskSnapshot, payload)
                # Build doc text
                doc_text = f"Symbol: {snap.symbol}\nTimestamp: {snap.timestamp}\nPrice: {snap.price} Volume: {snap.volume}\nRiskScore: {snap.riskScore}"
                doc_id = f"{snap.symbol}:{snap.timestamp}"
                store.add(doc_id, doc_text, snap.dict())
                print(f"Indexed {doc_id}")

                # Example: invoke graph to enrich with a canned query for demo
                graph = build_graph()
                state_input = {"messages": [{"role": "user", "content": f"Summarize recent risk for {snap.symbol} and explain elevated VaR."}]}
                # inject retriever and llm into state after compile (LangGraph state usage simplified)
                compiled = graph.invoke(state_input, context={"retriever": store, "llm": call_hf_inference})
                # compiled result may vary - for demo we read aiSummary if present
                ai_summary = compiled.get("aiSummary", "n/a")
                ai_sentiment = compiled.get("aiSentiment", "neutral")
                ai_conf = compiled.get("aiConfidenceScore", 0.0)
                # Emit enriched message
                enriched = snap.dict()
                enriched.update({"aiSummary": ai_summary, "aiSentiment": ai_sentiment, "aiConfidenceScore": ai_conf})
                emit_enriched(TOPIC_ENRICH, enriched)
            except Exception as e:
                print("Error processing message:", e)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    # Allow running consumer as module: python -m src.consumer
    import asyncio
    asyncio.run(consumer_loop())
