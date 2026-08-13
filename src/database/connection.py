from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

## 1) create the engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
)
    
## 2) Create session
SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)
    
## Base Class for all models
class Base(DeclarativeBase):
    pass

## function to create the tables
def create_tables():
    Base.metadata.create_all(engine)

def get_session():
    return SessionLocal()

    