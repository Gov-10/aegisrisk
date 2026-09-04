import uuid, os, json
from kafka import KafkaConsumer, KafkaProducer
from dotenv import load_dotenv
load_dotenv()
consumer = KafkaConsumer("ingestion-topic", bootstrap_servers=os.getenv("BOOTSTRAP_SERVER"), auto_offset_reset= "earliest", value_deserializer= lambda x: json.loads(x.decode()), group_id="pred-stuff")
producer = KafkaProducer(bootstrap_servers=os.getenv("BOOTSTRAP_SERVER"), value_serializer= lambda c: json.dumps(c.encode("utf-8")))
for msg in consumer:
    data = msg.value
    entity, event, payload= data["entity"], data["event"], data["payload"]
    #TODO: ml model and prediction
    pred = 0 #for now
    val = {"event_id": data["event_id"], "entity": entity, "event": event, "payload": payload, "pred": pred}
    producer.send("pred-topic", key=str(uuid.uuid4()), value=val)
    producer.flush()
