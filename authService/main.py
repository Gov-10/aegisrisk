from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from utils.otp_generator import gen_otp
from utils.email_sender import email_send
from sqlalchemy.sql import text
from argon2 import PasswordHasher
ph = PasswordHasher()
from argon2.exceptions import VerifyMismatchError
from database import sessionLocal, Users
from fastapi.responses import Response, JSONResponse
import os, json, jwt, schemas, hashlib
from dotenv import load_dotenv
from redis import Redis
load_dotenv()
redis_client = Redis(host=os.getenv("REDIS_HOST"), port= int(os.getenv("REDIS_PORT")), password= os.getenv("REDIS_PASSWORD"), decode_responses=True)
app = FastAPI()
def get_db():
    db  = sessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health():
    return {"status": "Running"}

@app.get("/dbcheck")
def dbch(db:Session=Depends(get_db)):
    db_status = "up"
    try:
        db.execute(text('SELECT 1'))
    except Exception:
        db_status = "down"
    return {"db_status": db_status}

@app.get("/redischeck")
def redis_ch():
    redis_status = "up"
    try:
        redis_client.ping()
    except Exception:
        redis_status = "down"
    return {"redis_status": redis_status}

@app.post("/create")
def crea(payload: schemas.RegisterSchema, db:Session=Depends(get_db)):
    name, email, username, password, user_id = payload.name, payload.email, payload.username, payload.password, payload.user_id
    db_note = Users(name=name, email=email, username=username, password=ph.hash(password), user_id=user_id)
    db.add(db_note)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="db error")
    db.refresh(db_note)
    verify_otp = gen_otp()
    hashed = hashlib.sha256(otp.encode()).hexdigest()
    redis_client.setex(f"verify_otp:{email}", 600, hashed)
    email_send(email, verify_otp)
    return {"message": "verify your email"}

@app.post("/verify")
def veri(payload:schemas.VerifySchema, db:Session=Depends(get_db)):
    email, verify_otp = payload.email, payload.verify_otp
    key = f"verify_otp:{email}"
    hashed=redis_client.get(key)
    if not hashed:
        raise HTTPException(status_code=404, detail="not found")
    input_hash=hashlib.sha256(verify_otp.encode()).hexdigest()
    if input_hash != stored:
        raise HTTPException(status_code=401, detail="otp does not match")
    user = db.query(Users).filter(Users.email==email).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    user.isactive = True
    db.add(user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"internal server error: {str(e)}")
    db.refresh(user)
    return {"message": "proceed to login"}

@app.post("/login")
def logi(payload: schemas.LoginSchema, response:Response, db:Session=Depends(get_db)):
    username, password = payload.username, payload.password
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    if user.isactive:
        passw = user.password
        try:
            ph.verify(passw, password)
            payl = {"iss": "aegis-auth", "user_id": user.user_id, "sub": username, "exp": datetime.utcnow()+timedelta(days=7), "email": user.email}
            token = jwt.encode(payl, os.getenv("JWT_SECRET"), algorithm="HS256")
            response.set_cookie(key="session_token", value=token, httponly=True, secure=True, samesite="lax",  max_age=604800)
            return {"message": "logged in"}
        except VerifyMismatchError:
            raise HTTPException(status_code=401, detail="passwords do not match")
    else:
        raise HTTPException(status_code=401, detail="please verify email")

@app.get("/logout")
def logo(request: Request, response: Response, db:Session=Depends(get_db)):
    session_token= request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detaail="you are not logged in")
    response.delete_cookie("session_token")
    return {"message": "logged out"}
