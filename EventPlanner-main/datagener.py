import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Event  # Імпортуйте ваші моделі
from sqlalchemy.orm import Session

load_dotenv()
from datetime import datetime

DATABASE_URL = os.getenv("sqlite:///./simple.db")
engine = create_engine("sqlite:///./simple.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def generate_films(db: Session):
    films = [
        Event(name="Event 1", place="A", description="An action", date=datetime.strptime("2024-01-01", "%Y-%m-%d"),
              price=32),
        Event(name="Event 2", place="C", description="Exhibition ", date=datetime.strptime("2024-01-01", "%Y-%m-%d"),
              price=17.2),
        Event(name="Event 3", place="D", description="Dancing", date=datetime.strptime("2024-01-01", "%Y-%m-%d"),
              price=4.25),
        Event(name="Event 4", place="Sc", description="A IT enent", date=datetime.strptime("2024-01-01", "%Y-%m-%d"),
              price=100.0),
        Event(name="Event 5", place="Ho", description="A expo", date=datetime.strptime("2024-01-01", "%Y-%m-%d"),
              price=24.25)
    ]

    db.add_all(films)
    db.commit()
    for film in films:
        db.refresh(film)
    print("5 films have been added to the database.")


def main():
    db = SessionLocal()
    try:
        generate_films(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
