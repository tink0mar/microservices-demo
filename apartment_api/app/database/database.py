from sqlmodel import create_engine, SQLModel, Session
from .models import Apartment  # Import the SQLModel for Apartment
from contextlib import contextmanager

DATABASE_URL = "sqlite:///./database/apartments.db"  # Your database URL
engine = create_engine(DATABASE_URL, echo=True)

# Initialize the database by creating tables
def init_db():
    SQLModel.metadata.create_all(bind=engine)  # Creates all tables from SQLModel definitions

# Dependency to provide a session to FastAPI routes

def get_db_session():
    session = Session(engine)
    try:
        yield session  # Makes session available to FastAPI routes
    finally:
        session.close()  # Ensure session is closed after handling the request

