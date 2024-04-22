import sys
sys.path.append("./")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend_configuration.configuration import Config

configuration = Config()

engine = create_engine(url=configuration.DATABASE_URL, 
                       connect_args={configuration.CONNECT_ARGS:False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()