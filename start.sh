#!/usr/bin/env bash
# Entrypoint for the container: starts the app (demo API + consumer)
export PYTHONPATH=/app/src
uvicorn src.consumer:app --host 0.0.0.0 --port 8000 &

# also run the consumer loop in background (simple demo)
python -u -m src.consumer
