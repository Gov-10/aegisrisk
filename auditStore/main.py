import os, json, uuid
from kafka import KafkaConsumer
from dotenv import load_dotenv
load_dotenv()
from database import Audit, sessionLocal
consumer = KafkaConsumer("action-topic", bootstrap_servers=os.getenv("BOOTSTRAP_SERVER"), value_deserializer= lambda x: json.loads(x.decode()), auto_offset_reset= "earliest", group_id="audit-stuff")
db=sessionLocal()
for msg in consumer:
    data = msg.value
    event_id, entity, event, payload, action, pred, res= data["event_id"], data["entity"], data["event"], data["payload"], data["action"], data["pred"], data["res"]
    timestamp = payload.get("timestamp")
    db_note = Audit(event_id=event_id, entity=entity, event=event, payload=payload, action=action, pred=pred, res=res, timestamp=timestamp)
    db.add(db_note)
    try:
        db.commit()
    except Exception:
        db.rollback()
    db.refresh(db_note)


