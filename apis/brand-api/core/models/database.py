import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

print(os.environ["RUN_ENV"])

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres/brand_db"

if os.environ["RUN_ENV"] == "local":
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/brand_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
