from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.sql import text
from database import Audit, sessionLocal, Users
import time,  os, json, jwt
from sqlalchemy.orm import Session
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

EXCLUDED_PATHS= ["/", "/docs", "/openapi.json", "/dbcheck"]
@app.middleware("http")
async def middle(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        resp = await call_next(request)
        return resp
    auth = request.cookies.get("session_token")
    if not auth:
        return JSONResponse(status_code=401, content={"message": "missing auth"})
    payl = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    user_id, username, email = payl.get("user_id"), payl.get("username"), payl.get("email")
    request.state.user_id, request.state.username, request.state.email = user_id, username, email
    start = time.time()
    respo = await call_next(request)
    proces = time.time() - start
    return respo

@app.get("/")
def healt():
    return {"status": "Running"}

@app.get("/dbcheck")
def dbc(db:Session=Depends(get_db)):
    db_status = "up"
    try:
        db.execute(text('SELECT 1'))
    except Exception as e:
        db_status = "down"
    return {"db_status": db_status}

@app.get("/history")
def hist(request: Request, db:Session=Depends(get_db)):
    user_id, username, email = request.state.user_id, request.state.username, request.state.email
    user = db.query(Users).filter(Users.user_id==user_id, Users.username==username, Users.email==email).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    result = []
    results = db.query(Audit).all()
    for res in results:
        result.append({"event_id": res.event_id, "entity": res.entity, "event": res.event, "payload": res.payload, "action": res.action, "pred": res.pred, "res": res.res, "timestamp": res.timestamp})
    return {"results": result}

