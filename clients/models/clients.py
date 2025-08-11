from sqlmodel import Field, SQLModel


class Clients(SQLModel, table=True):
    id: int = Field(nullable=False, primary_key=True)
    surname: str = Field(nullable=False)
    name: str = Field(nullable=False)
    patronymic: str = Field(default="")
    gender: str = Field(default="")
    age: int = Field(default=0)
    phone: str = Field(nullable=False)
    total_expenses: float = Field(default=0)
    discount: float = Field(default=0)
