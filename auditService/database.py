from sqlalchemy import create_engine,Float, JSON,  Column,Boolean, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class Audit(Base):
    __tablename__ = "audit"
    id = Column(Integer, index=True, autoincrement=True, primary_key=True)
    event_id = Column(String, unique=True)
    entity = Column(String)
    event = Column(String)
    payload = Column(JSON)
    action= Column(String)
    pred = Column(Float)
    res = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, unique=True)
    name = Column(String)
    email = Column(String)
    username = Column(String)
    password = Column(String)
    isactive= Column(Boolean, default=False)
    created_at= Column(DateTime, default=datetime.utcnow)
