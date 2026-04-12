import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/talent_db")
print(f"Connecting to: {url}")

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();"))
        print(f"Connected to: {result.fetchone()[0]}")
except Exception as e:
    print(f"Connection failed: {e}")
