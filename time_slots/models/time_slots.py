from sqlmodel import SQLModel, Field


class TimeSlots(SQLModel, table=True):
    slot_id: int = Field(nullable=False, primary_key=True)
    is_reserved: bool = Field(default=False)
    service_id: int = Field(nullable=False)
    salon_id: int = Field(nullable=False)
    date: str = Field(nullable=False)
    start_time: str = Field(nullable=False)
    end_time: str = Field(nullable=False)
    master: str = Field(default="")
