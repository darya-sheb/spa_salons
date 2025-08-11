from fastapi import FastAPI, HTTPException, status
from database.db import wait_for_db, SessionDep
from models.services import Services
from fastapi.responses import JSONResponse

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    print("startup")
    wait_for_db()


@app.post("/services/add")
async def add_service(service_id: int, title: str, price: int, salons_id: list[int], session: SessionDep):
    exist_id = session.get(Services, service_id)
    if exist_id:
        raise HTTPException(status_code=400, detail="Service already exists")
    new_service = Services(id=service_id, title=title, price=price, salons_id=salons_id)
    session.add(new_service)
    session.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=f"service with id {new_service.id} added")


@app.get("/services/info/{service_id}")
async def get_info(service_id: int, session: SessionDep):
    service = session.get(Services, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@app.post("/services/price/change/{id}")
async def change_price(service_id: int, new_price: int, session: SessionDep):
    service = session.get(Services, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.price = new_price
    session.add(service)
    session.commit()
    session.refresh(service)
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"price of service with id {service.id} changed")


@app.delete("/services/delete/{id}")
async def delete_service(service_id: int, session: SessionDep):
    service = session.get(Services, service_id)
    if not service:
        return "Service already is not exist"
    session.delete(service)
    session.commit()
    return f"Service with id {service_id} deleted"
