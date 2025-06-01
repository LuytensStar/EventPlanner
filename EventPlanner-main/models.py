import os
from sqlalchemy import Column, String, Integer, create_engine, DateTime, ForeignKey, Float, Table
from sqlalchemy import Enum as SQLEnum
import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from dotenv import load_dotenv
load_dotenv()
DB_URL = os.getenv('DB_URL')
print(DB_URL)


Base = declarative_base()
engine = create_engine("sqlite:///./simple.db", connect_args={'check_same_thread': False})
Sessionlocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

favourites_table = Table(
    "favorites",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"),),
    Column("event_id", Integer, ForeignKey("events.id"))
)

class TicketStatuses(str, enum.Enum):
    bought = "bought"
    in_process = "in_process"
    returned = "returned"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    surname = Column(String)
    email = Column(String)
    password = Column(String, nullable=False)
    favorites = relationship("Event", secondary=favourites_table, back_populates="liked")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(DateTime)
    place = Column(String)
    description = Column(String(500))
    price = Column(Float)
    speaker_id = Column(ForeignKey("speakers.id"))
    liked = relationship("User", secondary=favourites_table, back_populates="favorites")

class Speaker(Base):
    __tablename__ = "speakers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String)
    description = Column(String)
    event_id = Column(ForeignKey("events.id"))


class Sponsor(Base):
    __tablename__ = "sponsors"
    id = Column(Integer, primary_key=True, index=True)
    firm_name = Column(String)
    contacts = Column(String)
    event_id = Column(ForeignKey("events.id"))


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(ForeignKey("events.id"))
    user_id = Column(ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(String(500))


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(ForeignKey("events.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    price = Column(Float)
    status = Column(SQLEnum(TicketStatuses), default=TicketStatuses.bought)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()