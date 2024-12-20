from typing import Annotated
from fastapi import APIRouter, HTTPException, Body, Depends
from utils.check_availability import check_availability
from sqlmodel import Session, select
from database.database import router_get_db_session  # Dependency to get DB session
from database.models import Booking, Apartment, BookingIn, BookingUpdate  # SQLModel classes
from datetime import datetime
import pika
import json

router = APIRouter()

SessionDep = Annotated[Session, Depends(router_get_db_session)]

def publish_event(event_name, data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.exchange_declare(exchange='booking_events', exchange_type="fanout")
    message = json.dumps({"event": event_name, "data": data})
    channel.basic_publish(exchange="booking_events", routing_key="", body=message)
    connection.close()


@router.post("/", status_code=201)
def add_booking(booking: BookingIn, session: SessionDep):
    """Add a new booking"""
    # Check if the apartment exists
    apartment = session.get(Apartment, booking.apartment_id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")

    check_availability(booking.apartment_id, booking.start_date, booking.end_date, session)

    # Create new booking
    new_booking = Booking(
        apartment_id=booking.apartment_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        guest=booking.guest
    )
    session.add(new_booking)
    session.commit()
    session.refresh(new_booking)

    publish_event("booking_added", new_booking.dict())

    return {"id": new_booking.id}

@router.delete("/{booking_id}", status_code=200)
def cancel_booking(booking_id: str, session: SessionDep):
    """Cancel a booking by ID"""
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    session.delete(booking)
    session.commit()

    publish_event("booking_removed", {"id": booking_id})

    return 


@router.patch("/{booking_id}", status_code=200)
def change_booking(booking_id: str, booking: BookingUpdate, session: SessionDep):
    """Change booking details"""
    booking_db = session.get(Booking, booking_id)
    if not booking_db:
        raise HTTPException(status_code=404, detail="Booking not found")

    start_date = booking.start_date
    end_date = booking.end_date

    if start_date is None:
        start_date = booking_db.start_date

    if end_date is None:
        end_date = booking_db.end_date
    
    check_availability(booking_db.apartment_id, start_date, end_date, session, booking_id)

    booking_data = booking.model_dump(exclude_unset=True)
    booking_db.sqlmodel_update(booking_data)        
    session.commit()
    session.refresh(booking_db)

    # Publish the update event
    publish_event("booking_changed", {"id": booking_id, "start_date": booking_db.start_date, "end_date": booking_db.end_date})

    return booking_db

@router.get("/", response_model=list[Booking])
def list_bookings(session: SessionDep):
    """List all bookings"""
    bookings = session.exec(select(Booking)).all()
    return bookings