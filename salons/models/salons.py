from sqlmodel import Field, SQLModel


class Salons(SQLModel, table=True):
    id: int = Field(primary_key=True)
    address: str = Field(nullable=False)
    revenue: float = Field(default=0)
    rating: float | None = Field(default=None)
    feedback_count: int = Field(default=0)
    feedback_total: int = Field(default=0)
