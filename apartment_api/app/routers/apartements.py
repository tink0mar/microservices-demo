from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database.models import Apartment, ApartmentIn, ApartmentOut
from database.database import get_db_session  # Dependency to get DB session
import pika
import json

SessionDep = Annotated[Session, Depends(get_db_session)]

router = APIRouter()


def publish_event(event_name, data):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()
    channel.exchange_declare(
        exchange="apartment_events", exchange_type="fanout"
    )
    message = json.dumps({"event": event_name, "data": data})
    channel.basic_publish(
        exchange="apartment_events", routing_key="", body=message
    )
    connection.close()


@router.post("/", status_code=201)
def add_apartment(apartment: ApartmentIn, session: SessionDep):
    """Add a new apartment"""
    apartments = session.exec(
        select(Apartment).where(Apartment.name == apartment.name)
    ).all()

    if len(apartments):
        raise HTTPException(status_code=403, detail="Object already exists")

    new_apartment = Apartment.model_validate(
        apartment
    )  # Convert Pydantic model to SQLModel
    session.add(new_apartment)
    session.commit()
    session.refresh(new_apartment)
    publish_event("apartment_added", new_apartment.dict())
    return new_apartment


@router.get("/", response_model=list[ApartmentOut])
def list_apartments(session: SessionDep):
    """List all apartments"""
    apartments = session.exec(select(Apartment)).all()
    return apartments


@router.delete("/{apartment_id}", response_model=ApartmentOut)
def remove_apartment(apartment_id: str, session: SessionDep):
    """Remove an apartment by ID"""
    apartment = session.get(Apartment, apartment_id)
    if apartment is None:
        raise HTTPException(status_code=404, detail="Apartment not found")
    session.delete(apartment)
    session.commit()
    publish_event("apartment_removed", {"id": apartment_id})
    return
