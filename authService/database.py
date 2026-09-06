from sqlalchemy import Column, create_engine, String, Integer, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
engine = create_engine(os.getenv("DATABASE_URL"))
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, unique=True)
    name = Column(String)
    email = Column(String)
    username= Column(String)
    password = Column(String)
    isactive =Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

