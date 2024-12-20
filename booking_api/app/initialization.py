import requests
from database.database import consumer_db_session  # SQLModel session dependency
from database.models import Apartment, Booking  # SQLModel models
from sqlmodel import Session

def update_apartments_table(session: Session):
    """
    Fetch apartment data from the given endpoint and update the apartments table.
    """
    try:
        # Fetch apartment data
        response = requests.get("http://localhost:8001/apartments/")
        response.raise_for_status()

        apartment_list = response.json()

        for apartment in apartment_list:
            existing_apartment = session.get(Apartment, apartment['id'])
            if not existing_apartment:
                apartment_db = Apartment(**apartment)
                session.add(apartment_db)
        
        session.commit()
        print("Apartment table updated successfully.", flush=True)

    except requests.RequestException as e:
        print(f"Error fetching apartments: {e}", flush=True)
    except Exception as e:
        print(f"Database error: {e}", flush=True)

def initialize_data():
    """
    Initialize apartments and bookings data.
    """
    # Use the SQLModel session dependency for interacting with the database
    with consumer_db_session() as session:
        update_apartments_table(session)
        