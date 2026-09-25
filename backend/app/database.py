from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL


# SQLite requires this setting for FastAPI's local development workflow
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


# Create database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for all database models
Base = declarative_base()


# Dependency for getting a database session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()