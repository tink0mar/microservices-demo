from datetime import datetime
from sqlmodel import select
from fastapi import HTTPException
from database.models import Booking  # SQLModel Booking model

def check_availability(apartment_id: str, start_date: str, end_date: str, session, booking_id: str = None):
    """
    Check if an apartment is available between the specified dates.
    
    Validates the date format and ensures that there are no existing bookings
    that overlap with the provided date range.
    """
    try:
        # Validate date format and range
        _start_date = datetime.strptime(start_date, "%Y-%m-%d")
        _end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Ensure the start date is before the end date
        if _start_date >= _end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date.")
        
        # Ensure the start date is in the future
        if datetime.now() >= _start_date:
            raise HTTPException(status_code=400, detail="Start date must be after today.")
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use yyyy-MM-dd")

    # Check for overlapping bookings in the database

    if booking_id:
        statement = select(Booking).where(
            Booking.apartment_id == apartment_id,
            Booking.id != booking_id,
            (Booking.start_date < end_date) & (Booking.end_date > start_date)
        )
    else: 
        statement = select(Booking).where(
            Booking.apartment_id == apartment_id,
            (Booking.start_date < end_date) & (Booking.end_date > start_date)
        )

    existing_bookings = session.exec(statement).all()
    print(existing_bookings)
    if existing_bookings:
        raise HTTPException(status_code=400, detail="The apartment is already booked for the specified dates.")

    return True  # If no conflicts, return True to indicate availability
