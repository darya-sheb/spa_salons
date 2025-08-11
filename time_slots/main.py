from fastapi import FastAPI, HTTPException, status
from database.db import wait_for_db, SessionDep
from sqlmodel import select
from models.time_slots import TimeSlots
import requests
from fastapi.responses import JSONResponse

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    print('startup')
    wait_for_db()


@app.post("/time_slots/add")
async def add_slot(slot_id: int, service_id: int, salon_id: int, date: str, start_time: str, end_time: str, master: str,
                   session: SessionDep):
    exist_id = session.get(TimeSlots, slot_id)
    if exist_id:
        raise HTTPException(status_code=400, detail="Time slot already exists")
    new_slot = TimeSlots(slot_id=slot_id, salon_id=salon_id, service_id=service_id, date=date, start_time=start_time,
                         end_time=end_time,
                         master=master)
    session.add(new_slot)
    session.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=f"slot with id {slot_id} added")


@app.post("/time_slots/change_master/{slot_id}")
async def change_master(slot_id: int, master: str, session: SessionDep):
    slot = session.get(TimeSlots, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    slot.master = master
    session.add(slot)
    session.commit()
    session.refresh(slot)
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"slot with id {slot_id} changed")


@app.delete("/time_slots/delete")
async def delete_slot(slot_id: int, session: SessionDep):
    slot = session.get(TimeSlots, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot is already deleted")
    session.delete(slot)
    session.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"slot with id {slot_id} deleted")


@app.post("/time_slots/change_time/{id}")
async def change_time(session: SessionDep, slot_id: int, date: str | None = None, start_time: str | None = None,
                      end_time: str | None = None):
    slot = session.get(TimeSlots, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    if date is None and start_time is None and end_time is None:
        raise HTTPException(status_code=404, detail="No date or time")

    if date is not None:
        slot.date = date
    if start_time is not None:
        slot.start_time = start_time
    if end_time is not None:
        slot.end_time = end_time
    session.add(slot)
    session.commit()
    session.refresh(slot)
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"slot with id {slot_id} changed")


@app.get("/time_slots/service/{id}")
async def get_slots_for_service(service_id: int, session: SessionDep):
    response = session.exec(select(TimeSlots).where(TimeSlots.service_id == service_id)).all()
    if not response:
        raise HTTPException(status_code=404, detail="There are not any slots for this service now")
    return response


@app.post("/time_slots/reservation/{slot_id}")
async def reservation_slot(slot_id: int, reserve: bool, session: SessionDep):
    slot = session.get(TimeSlots, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    slot.is_reserved = reserve
    session.add(slot)
    session.commit()
    session.refresh(slot)
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"slot with id {slot_id} reserved")


@app.get("/time_slots/reservation/check/{slot_id}")
async def check_reservation(slot_id: int, session: SessionDep):
    slot = session.get(TimeSlots, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot.is_reserved


@app.get("/time_slots/service_info/{slot_id}")
async def get_info_about_service(slot_id: int, session: SessionDep):
    slot = session.get(TimeSlots, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    service_id = slot.service_id
    service_info = requests.get(f"http://services-service:8002/services/info/{service_id}")
    return service_info.json()


@app.get("/time_slots/salon_id/{slot_id}")
async def get_salon_id(slot_id: int, session: SessionDep):
    slot = session.get(TimeSlots, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot.salon_id
