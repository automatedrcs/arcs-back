
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from config import DATABASE_URL
import logging
from sqlalchemy import inspect

logging.basicConfig(level=logging.INFO)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def main():
    # Create tables in the database
    logging.info("Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    logging.info("Tables created.")
    
def check_tables():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    for table in Base.metadata.sorted_tables:
        if table.name not in table_names:
            print(f"Table {table.name} does not exist!")
        else:
            print(f"Table {table.name} exists.")

if __name__ == "__main__":
    main()
    check_tables()