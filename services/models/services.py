from sqlmodel import Field, SQLModel, Column
from typing import List
from sqlalchemy.types import JSON


class Services(SQLModel, table=True):
    id: int = Field(nullable=False, primary_key=True)
    title: str = Field(nullable=False)
    price: float = Field(nullable=False)
