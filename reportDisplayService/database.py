from sqlalchemy import create_engine, Float, Column, Integer, DateTime, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class Reports(Base):
    __tablename__ = "reports"
    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    filename= Column(String, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

