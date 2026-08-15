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
    echo=False,
)
    
## 2) Create session
SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)
    
## Base Class for all models
class Base(DeclarativeBase):
    pass

## function to create the tables
def create_tables():
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(engine)

def get_session():
    return SessionLocal()

    