from fastapi import Request, FastAPI, HTTPException, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from database import Reports, sessionLocal
from sqlalchemy.sql import text
import minio,time, os, json, jwt
from dotenv import load_dotenv
load_dotenv()
minio_client = minio.Minio(os.getenv("MINIO_URL"), access_key=os.getenv("MINIO_ACCESS"), secret_key=os.getenv("MINIO_SECRET"), secure=False)
bucket ="audit-reports"
app=FastAPI()
def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()
EXCLUDED_PATHS = ["/", "/docs", "/openapi.json", "/dbcheck"]
@app.middleware("http")
async def middle(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        resp = await call_next(request)
        return resp
    token = request.cookies.get("session_token")
    if not token:
        return JSONResponse(status_code=401,content={"message": "not authorized"})
    payl = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    request.state.username, request.state.user_id, request.state.email = payl.get("sub"), payl.get("user_id"), payl.get("email")
    start = time.time()
    respo = await call_next(request)
    proc = time.time() - start
    return respo

@app.get("/")
def hel():
    return {"status": "Running"}

@app.get("/dbcheck")
def dbc(db:Session=Depends(get_db)):
    db_status = "up"
    try:
        db.execute(text('SELECT 1'))
    except Exception:
        db_status = "down"
    return {"db_status": db_status}

@app.get("/reports")
def get_rep(db:Session=Depends(get_db)):
    reports = db.query(Reports).all()
    res = []
    for report in reports:
        url = minio_client.presigned_get_object(bucket_name=bucket, object_name=report.filename, expires=timedelta(hours=24)
        res.append({"filename": report.filename, "timestamp": report.timestamp, "url": url})
    return {"results": res}

