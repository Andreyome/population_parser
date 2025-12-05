import time
from database.database import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


def wait_for_db(retries=10, delay=3):
    engine = create_engine(DATABASE_URL)
    for i in range(retries):
        try:
            with engine.connect() as conn:
                return True
        except OperationalError:
            print(f"Database not ready, waiting...")
            time.sleep(delay)
    raise Exception("Database not ready after waiting.")
