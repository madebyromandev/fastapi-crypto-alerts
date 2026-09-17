import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


load_dotenv()


DATABASE_URL = URL.create(
    "postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)


engine = create_engine(DATABASE_URL)

from sqlalchemy.orm import sessionmaker


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False
)


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database();")
        )

        return result.scalar_one()


if __name__ == "__main__":
    print("Подключено к базе:", test_connection())

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()