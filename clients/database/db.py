from sqlalchemy.exc import OperationalError
from sqlmodel import create_engine, SQLModel, Session
import os
import time
from typing import Annotated
from fastapi import Depends

DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)


def wait_for_db():
    retries = 5
    while retries:
        try:
            SQLModel.metadata.create_all(engine)
            print('created db:' + str(SQLModel.metadata.tables.keys()))
            return
        except OperationalError:
            retries -= 1
            time.sleep(5)
    raise Exception("Failed to connect to database after multiple attempts")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
