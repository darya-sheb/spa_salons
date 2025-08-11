from sqlmodel import SQLModel, Field


class Appointments(SQLModel, table=True):
    slot_id: int = Field(primary_key=True)
    client_id: int = Field(nullable=False)
    price: float = Field(nullable=False)
    is_paid: bool = Field(default=False)
