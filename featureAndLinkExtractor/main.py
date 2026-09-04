import os, json, uuid
from dotenv import load_dotenv
load_dotenv()
from kafka import KafkaConsumer, KafkaProducer
producer =KafkaProducer(bootstrap_servers=os.getenv("BOOTSTRAP_SERVER"), value_serializer=lambda x: json.dumps(x).encode("utf-8"))

consumer = KafkaConsumer("ingestion-topic", bootstrap_servers=os.getenv("BOOTSTRAP_SERVER"), value_deserializer=lambda c: json.loads(c.decode()), group_id="rag-stuff", auto_offset_reset="earliest")
for msg in consumer:
    data = msg.value
    entity, event, payload = data["entity"], data["event"], data["payload"]
    #TODO: Vector search and matching code
    res = None
    val = {"event_id": data["event_id"], "entity": entity, "event": event, "payload": payload, "result": res}
    producer.send("feature-topic", key=str(uuid.uuid4()), value=val)
    producer.flush()


