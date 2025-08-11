from fastapi import FastAPI, HTTPException, status
from database.db import wait_for_db, SessionDep
from models.clients import Clients
from sqlmodel import select
from fastapi.responses import JSONResponse

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    print("startup")
    wait_for_db()


@app.post("/clients/add")
async def add_client(client_id: int, name: str, surname: str,
                     patronymic: str, gender: str, age: int, phone: str, session: SessionDep):
    exist_id = session.get(Clients, client_id)
    if exist_id:
        raise HTTPException(status_code=400, detail="Client already exists")
    new_client = Clients(id=client_id, name=name, surname=surname, patronymic=patronymic,
                         gender=gender, age=age, phone=phone)
    session.add(new_client)
    session.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=f"client with id {client_id} added")


@app.get("/clients/info")
async def get_client(session: SessionDep, client_id: int | None = None, surname: str | None = None, name: str = None):
    if client_id is not None:
        client = session.exec(select(Clients).where(Clients.id == client_id)).first()
    elif surname is not None and name is not None:
        client = session.exec(select(Clients).where(
            Clients.surname == surname and Clients.name == name)).first()
    else:
        raise HTTPException(status_code=400, detail="No client id or surname provided")

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if client_id is not None and client.id != client_id:
        raise HTTPException(status_code=404, detail="Incorrect data")
    if surname is not None and client.surname != surname:
        raise HTTPException(status_code=404, detail="Incorrect data")
    if name is not None and client.name != name:
        raise HTTPException(status_code=404, detail="Incorrect data")
    return client


@app.post("/clients/expenses/change/{client_id}")
async def change_expenses(client_id: int, service_price: int, session: SessionDep):
    client = session.get(Clients, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    new_expenses = client.total_expenses + service_price
    client.total_expenses = new_expenses
    session.add(client)
    session.commit()
    session.refresh(client)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=f"client's {client.id} expenses changed to {new_expenses}")


@app.post("/clients/discount/change/{client_id}")
async def change_discounts(client_id: int, service_price: int, session: SessionDep):
    client = session.get(Clients, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    new_expenses = client.total_expenses + service_price
    new_disc = None
    if new_expenses > 20_000:
        new_disc = 0.1
    elif new_expenses > 50_000:
        new_disc = 0.15
    elif new_expenses > 500_000:
        new_disc = 0.3
    if new_disc is not None:
        client.discount = new_disc
        session.add(client)
        session.commit()
        session.refresh(client)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=f"client's {client.id} discount has been changed to {new_disc}")
