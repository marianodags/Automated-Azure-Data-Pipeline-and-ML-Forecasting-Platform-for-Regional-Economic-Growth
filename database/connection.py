import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to SQLite for local development/testing, but support Azure SQL DB connection string
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./regional_economy.db")

# For SQLite, enable check_same_thread=False for multi-threaded API requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for API or scripts to yield DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database if they don't exist."""
    import database.models  # Import models to ensure they register with Base metadata
    Base.metadata.create_all(bind=engine)
