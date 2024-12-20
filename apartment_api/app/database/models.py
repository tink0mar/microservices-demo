from sqlmodel import SQLModel, Field
from pydantic import BaseModel
import uuid

# SQLModel for database
class Apartment(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(..., unique=True)
    address: str
    noiselevel: float
    floor: int


# Pydantic model for validation (similar to SQLModel but without `table=True`)
class ApartmentIn(BaseModel):
    name: str
    address: str
    noiselevel: float
    floor: int

class ApartmentOut(BaseModel):
    id: str 
    name: str
    address: str
    noiselevel: float
    floor: int
