from sqlmodel import SQLModel, Field
import uuid

class Apartment(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(..., unique=True)
    address: str
    noiselevel: float
    floor: int

class BookingBase(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    

class Booking(BookingBase, table=True):
    apartment_id: str = Field(foreign_key="apartment.id")
    start_date: str  
    end_date: str    
    guest: str


class BookingUpdate(BookingBase):
    start_date: str | None = None
    end_date: str | None = None  