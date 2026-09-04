import os, json, uuid
from kafka import KafkaConsumer, KafkaProducer
from dotenv import load_dotenv
load_dotenv()
consumer= KafkaConsumer("feature-topic", "pred-topic", bootstrap_servers=os.getenv("BOOTSTRAP_SERVER"),auto_offset_reset="earliest",  value_deserializer=lambda x: json.loads(x.decode()), group_id="action-stuff")
producer = KafkaProducer(bootstrap_servers= os.getenv("BOOTSTRAP_SERVER"), value_serializer = lambda x: json.dumps(x).encode("utf-8"))
for msg in consumer:
    topic, data = msg.topic, msg.value
    if topic == "pred-topic":
        pred = data["pred"]
    if topic == "feature-topic":
        res = data["result"]
    event_id, entity, event, payload = data["event_id"], data["entity"], data["event"], data["payload"]
    #TODO: Categorization of actions based on pred score and res
    action = None #for now
    val = {"event_id": event_id, "entity": entity, "event": event, "payload": payload, "action": action, "pred": pred, "res": res}
    producer.send("action-topic", key=str(uuid.uuid4()), value=val)
    producer.flush()
