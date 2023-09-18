from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def main():
    # Create tables in the database
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    main()
