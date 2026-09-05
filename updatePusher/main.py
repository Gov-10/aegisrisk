import os, asyncio
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
consumer = AIOKafkaConsumer("action-topic", bootstrap_servers=os.getenv("BOOTSTRAP_SERVER"), group_id="pusher-stuff", auto_offset_reset="latest")
async def kafka_mess():
    await consumer.start()
    try:
        async for msg in consumer:
            yield {"event": "message", "data": msg.value.decode("utf-8")}
    finally:
        await consumer.stop()

@app.get("/stream")
async def mess_stre():
    return EventSourceResponse(kafka_mess())
