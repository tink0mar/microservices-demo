from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
import uuid


# SQLModel for database
class Apartment(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    name: str = Field(..., unique=True)
    address: str
    noiselevel: float
    floor: int
    bookings: list["Booking"] = Relationship(
        back_populates="apartment", cascade_delete=True
    )


class BookingBase(SQLModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )


class Booking(BookingBase, table=True):
    start_date: str
    end_date: str
    guest: str
    apartment_id: str = Field(foreign_key="apartment.id", ondelete="CASCADE")
    apartment: Apartment = Relationship(back_populates="bookings")


class BookingIn(BookingBase):
    apartment_id: str = Field(foreign_key="apartment.id")
    start_date: str
    end_date: str
    guest: str


class BookingUpdate(BookingBase):
    start_date: str | None = None
    end_date: str | None = None
