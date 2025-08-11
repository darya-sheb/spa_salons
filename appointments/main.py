from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from database.db import wait_for_db, SessionDep
from models.appointments import Appointments
import requests

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    print("startup")
    wait_for_db()


@app.post("/appointments/add")
async def add_appointment(slot_id: int, client_id: int, is_prepayment: bool, session: SessionDep):
    exist_id = session.get(Appointments, slot_id)
    if exist_id:
        raise HTTPException(status_code=400, detail="Appointment already exists")

    is_reserved = requests.get(f"http://time_slots-service:8003/time_slots/reservation/check/{slot_id}")
    if not is_reserved.ok:
        raise HTTPException(status_code=404, detail="Slot is not exist now")

    if bool(is_reserved.json()):
        raise HTTPException(status_code=404, detail="Sorry, this slot is already reserved")

    service_info = requests.get(f"http://time_slots-service:8003/time_slots/service_info/{slot_id}")
    price = service_info.json()["price"]
    new_appointment = Appointments(slot_id=slot_id, client_id=client_id, price=price, is_paid=is_prepayment)
    if is_prepayment:
        requests.post(f"http://clients-service:8001/clients/expenses/change/{client_id}?service_price={price}")
        requests.post(f"http://clients-service:8001/clients/discount/change/{client_id}?service_price={price}")
        salon_id = int(requests.get(f"http://time_slots-service:8003/time_slots/salon_id/{slot_id}").content)
        requests.post(f"http://salons-service:8000/salons/revenue/update/{salon_id}?service_price={price}")
    session.add(new_appointment)
    session.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(new_appointment))


@app.post("/appointments/make_payment/{id}")
async def make_payment(slot_id: int, session: SessionDep):
    slot = session.get(Appointments, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    client_id = slot.client_id
    price = slot.price
    requests.post(f"http://clients-service:8001/clients/expenses/change/{client_id}?service_price={price}")
    requests.post(f"http://clients-service:8001/clients/discount/change/{client_id}?service_price={price}")
    salon_id = int(requests.get(f"http://time_slots-service:8003/time_slots/salon_id/{slot_id}").content)
    requests.post(f"http://salons-service:8000/salons/revenue/update/{salon_id}?service_price={price}")
    slot.is_paid = True
    session.add(slot)
    session.commit()
    session.refresh(slot)
    return JSONResponse(status_code=status.HTTP_200_OK, content="Payment is done")


@app.delete("/appointments/delete")
async def delete_appointment(slot_id: int, session: SessionDep):
    slot = session.get(Appointments, slot_id)
    if not slot:
        return "Slot already is not exists"
    requests.post(f"http://time_slots-service:8003/time_slots/reservation/{slot_id}?reserve={False}")
    session.delete(slot)
    session.commit()
    return f"appointment with id {slot_id} deleted"


@app.get("/appointments/info/{slot_id}")
async def get_appointment_info(slot_id: int, session: SessionDep):
    response = session.get(Appointments, slot_id)
    if not response:
        raise HTTPException(status_code=404, detail="Slot not found")
    return response
