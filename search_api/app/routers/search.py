from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from database.database import router_db_session  # SQLModel session dependency
from database.models import Booking, Apartment  # SQLModel models

router = APIRouter()

SessionDep = Annotated[Session, Depends(router_db_session)]


@router.get("/search")
def search_apartments(session: SessionDep, from_date: str = Query(...), to_date: str = Query(...), ):
    """
    Search for available apartments within a date range.
    """
    try:
        # Search for bookings in the date range
        statement = select(Booking, Apartment).join(Apartment, Booking.apartment_id == Apartment.id).where(
            Booking.start_date >= from_date,
            Booking.end_date <= to_date
        )
        result = session.exec(statement).all()

        return [ 
            {
                "booking_id": booking.id,
                "start_date": booking.start_date,
                "end_date": booking.end_date,
                "guest": booking.guest,
                "apartment": {
                    "id": apartment.id,
                    "name": apartment.name,
                    "address": apartment.address,
                    "noiselevel": apartment.noiselevel,
                    "floor": apartment.floor
                }
            }
            for booking, apartment in result
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
