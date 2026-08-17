import os
import time

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    raise ValueError(
        "Missing POSTGRES_USER, POSTGRES_PASSWORD, or POSTGRES_DB environment variable"
    )

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host="postgis-db",
    port=5432,
    database=POSTGRES_DB,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def init_db(max_retries: int = 10, retry_delay: int = 2):
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                print("Database connection test:", result.scalar())

            Base.metadata.create_all(bind=engine)

            print("Database initialized successfully")
            return True

        except Exception as e:
            print(
                f"Database error "
                f"(attempt {attempt + 1}/{max_retries}): {e}"
            )

            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
