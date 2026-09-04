from fastapi import FastAPI, HTTPException, Request, Depends
from kafka import KafkaProducer
import uuid, os, json, schemas
from dotenv import load_dotenv
load_dotenv()
producer = KafkaProducer(bootstrap_servers=os.getenv("BOOTSTRAP_SERVER"), value_serializer=lambda x: json.dumps(x).encode("utf-8"))
app = FastAPI()

@app.get("/")
def healt():
    return {"status": "Running"]

@app.post("/ingest")
def ingess(payl: schemas.IngestSchema):
    entity, event, payload = payl.entity, payl.event, payl.payload
    event_id = str(uuid.uuid4())
    value = {"event_id": event_id, "entity": entity, "event": event, "payload": payload}
    producer.send("ingestion-topic", key=event_id.encode(), value=value)
    producer.flush()
    return {"status": "Queued", "event_id": event_id}

