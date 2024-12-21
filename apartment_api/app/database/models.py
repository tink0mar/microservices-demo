from sqlmodel import SQLModel, Field
from pydantic import BaseModel
import uuid


class ApartmentBase(SQLModel):
    name: str = Field(..., unique=True)
    address: str
    noiselevel: float
    floor: int


class Apartment(ApartmentBase, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )


# Pydantic model for validation (similar to SQLModel but without `table=True`)
class ApartmentCreate(ApartmentBase):
    pass
