import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def init_engine():
    """
    Creates resilient database engine:
    Tries configured MySQL first; falls back gracefully to SQLite in local dev if credentials are not yet configured.
    """
    try:
        mysql_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20
        )
        with mysql_engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info(f"Connected to MySQL on {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
        return mysql_engine
    except Exception as e:
        logger.warning(f"MySQL unavailable ({e}). Falling back to local SQLite database.")
        sqlite_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        os.makedirs(sqlite_dir, exist_ok=True)
        sqlite_path = os.path.join(sqlite_dir, "doc_to_db.sqlite")
        sqlite_engine = create_engine(
            f"sqlite:///{sqlite_path}",
            connect_args={"check_same_thread": False}
        )
        return sqlite_engine

engine = init_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_tables():
    """Ensures all ORM tables exist."""
    import app.models  # load models
    Base.metadata.create_all(bind=engine)

create_db_tables()

def get_db():
    """FastAPI Dependency for database sessions with safe auto-close."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import text

def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"DB check notice: {e}")
        return False
