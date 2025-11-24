# Market-Risk Agentic RAG Service

This repository contains a minimal, runnable example of an **agentic RAG** (Retrieval-Augmented Generation)
service for a market-risk microservice. It ingests `MarketRiskSnapshot` messages from Kafka, indexes them into
a FAISS vector store, and uses LangGraph to orchestrate retrieval + an LLM (Hugging Face Llama or HF Inference)
to produce `aiSummary`, `aiSentiment`, and `aiConfidenceScore`. Enriched messages are emitted to a Kafka topic
(`market-risk-enriched`).

**Contents**
- `src/` — Python source code:
  - `models.py` — Pydantic model for the incoming snapshot
  - `consumer.py` — Kafka consumer that indexes incoming snapshots
  - `vectors.py` — FAISS-based indexer and retriever
  - `llm.py` — LLM wrapper (supports HF Inference API or local transformers)
  - `graph.py` — LangGraph workflow orchestrating retrieval and LLM calls
  - `producer.py` — Producer to emit enriched messages
- `Dockerfile` — container image for the service
- `docker-compose.yml` — quick-compose with Zookeeper & Kafka (Bitnami)
- `requirements.txt` — Python dependencies
- `start.sh` — entrypoint script

## Quickstart (local, development)

> This setup is for development and demonstration only.

1. Build the service image:
```bash
docker-compose build
```

2. Start services (Kafka + app):
```bash
docker-compose up
```

3. Configure environment variables:
- `HF_API_TOKEN` — (optional) Hugging Face token if using HF Inference API
- `HF_MODEL` — default `meta-llama/Llama-2-7b-chat` (change to smaller model for CPU)
- `KAFKA_BOOTSTRAP` — default `kafka:9092` (set if using remote Kafka)

4. Send test messages to topic `market-risk-snapshots` (JSON). The consumer will index documents and also demonstrate a sample graph invocation.

## Notes & Security
- **Do not** send sensitive position-level data to hosted inference endpoints unless you have contractual and compliance coverage.
- For production, replace FAISS (single-node) with Milvus/Chroma/Pinecone for scaling and metadata filtering.
- Add authentication, TLS, monitoring, and proper error handling before production use.

## Files
See `src/` for implementation details.

