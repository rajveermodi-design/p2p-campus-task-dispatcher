import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment credentials from local .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "campus_dispatcher")

# Construct MySQL connection URI using PyMySQL driver
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize database engine
# isolation_level="REPEATABLE READ" guarantees consistent snapshot isolation
# pool_pre_ping=True checks connection health before issuing queries
engine = create_engine(
    DATABASE_URL,
    isolation_level="REPEATABLE READ",
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)

# SessionLocal factory creates transactional sessions per API request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base model class
Base = declarative_base()

def get_db():
    """
    FastAPI dependency that yields a distinct database session per request
    and guarantees teardown/closure upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()