from fastapi import FastAPI, HTTPException, status, Query
from database.db import wait_for_db, SessionDep
from models.salons import Salons
from fastapi.responses import JSONResponse

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    print("startup")
    wait_for_db()


@app.post("/salons/create")
async def create_salon(salon_id: int, salon_address: str, session: SessionDep):
    exist_id = session.get(Salons, salon_id)
    if exist_id:
        raise HTTPException(status_code=400, detail="Salon already exists")
    new_salon = Salons(id=salon_id, address=salon_address)
    session.add(new_salon)
    session.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=f"salon with id {salon_id} created")


@app.get("/salons/rating/{id}")
async def show_rating(salon_id: int, session: SessionDep):
    salon = session.get(Salons, salon_id)
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")
    return {"rating": salon.rating, "feedback count": salon.feedback_count}


@app.post("/salons/rating/update/{id}")
async def add_feedback(salon_id: int, mark: int, session: SessionDep):
    salon = session.get(Salons, salon_id)
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")
    salon.feedback_total += mark
    salon.feedback_count += 1
    salon.rating = salon.feedback_total / salon.feedback_count
    session.add(salon)
    session.commit()
    session.refresh(salon)
    return f"New rating for salon with id {salon_id}: {salon.rating}"


@app.delete("/salons/delete")
async def delete_salon(salon_id: int, session: SessionDep):
    salon = session.get(Salons, salon_id)
    if not salon:
        return "Salon already deleted"
    session.delete(salon)
    session.commit()
    return f"Salon with id {salon_id} deleted"


@app.get("/salons/revenue/{id}")
async def show_revenue(salon_id: int, session: SessionDep):
    salon = session.get(Salons, salon_id)
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")
    return {"total revenue": salon.revenue}


@app.post("/salons/revenue/update/{salon_id}")
async def update_revenue(salon_id: int, service_price: float, session: SessionDep):
    salon = session.get(Salons, salon_id)
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")
    salon.revenue += service_price
    session.add(salon)
    session.commit()
    session.refresh(salon)
    return {"new revenue": salon.revenue}
