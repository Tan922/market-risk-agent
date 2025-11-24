import os
import json
from confluent_kafka import Producer

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9093")
p = Producer({"bootstrap.servers": BOOTSTRAP})

def emit_enriched(topic: str, payload: dict):
    p.produce(topic, json.dumps(payload).encode("utf-8"))
    p.flush()
