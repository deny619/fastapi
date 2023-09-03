from db import get_session
from schemas import Car, CarInput, CarOuput, Trip, TripInput


from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

router = APIRouter(prefix="/api/cars")

@router.get("/")
def get_cars(size: str|None = None, doors: int|None = None,
             session: Session = Depends(get_session)) -> list:
        query = select(Car)
        if size:
            query = query.where(Car.size == size)
        if doors:
            query = query.where(Car.doors >= doors)
        return session.exec(query).all()


@router.get("/{id}", response_model=CarOuput)
def car_by_id(id : int, session: Session = Depends(get_session)) -> CarOuput:
    car = session.get(Car, id)
    if car:
        return car
    else:
        raise HTTPException(status_code = 404, detail= f"No car id with id={id}.")


@router.post("/", response_model=Car)
def add_car(car_input: CarInput, session: Session = Depends(get_session)) -> Car:
        new_car = Car.from_orm(car_input)
        session.add(new_car)
        session.commit()
        session.refresh(new_car)
        return new_car


@router.delete("/{id}", status_code=204)
def remove_car(id: int, session: Session = Depends(get_session)) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@router.put("/{id}", response_model=Car)
def change_car(id: int, new_car: CarInput, session: Session = Depends(get_session) ) -> Car:
    car = session.get(Car,id)
    if car:
        car.size = new_car.size
        car.fuel = new_car.fuel
        car.doors = new_car.doors
        car.transmission = new_car.transmission
        session.commit()
        return car
    else:
        raise HTTPException(status_code=404, detail="No car with id={id}.")


@router.post("/{car_id}/trips", response_model=Trip)
def add_trip(car_id: int, trip_input:TripInput, session: Session = Depends(get_session)) -> Trip:
    car = session.get(Car, car_id)
    if car:
        new_trip= Trip.from_orm(trip_input, update={'car_id': car_id})
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip

    else:
        raise HTTPException(status_code=404, detail=f"No such car with id={id}.")