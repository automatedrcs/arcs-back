from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from database.database import get_db
from database.schema import AvailabilityCreate, AvailabilityUpdate, Availability
from database.models import Availability as AvailabilityModel

# ------------------------- CRUD Operations -------------------------

def get_availabilities(
    db: Session,
    person_id: UUID,
    availability_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> Union[AvailabilityModel, List[AvailabilityModel]]:
    query = db.query(AvailabilityModel)
    query = query.filter(AvailabilityModel.person_id == person_id)

    if availability_id:
        return query.filter(AvailabilityModel.id == availability_id).first()

    if person_id:
        query = query.filter(AvailabilityModel.person_id == person_id)

    return query.offset(skip).limit(limit).all()

def create_availability(db: Session, availability: AvailabilityCreate) -> AvailabilityModel:
    db_availability = AvailabilityModel(**availability.dict())
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

def update_availability(db: Session, availability_id: UUID, availability: AvailabilityUpdate) -> Optional[AvailabilityModel]:
    db_availability = db.query(AvailabilityModel).filter(AvailabilityModel.id == availability_id).first()
    if db_availability:
        for key, value in availability.dict().items():
            setattr(db_availability, key, value)
        db.commit()
        db.refresh(db_availability)
    return db_availability

def delete_availability(db: Session, availability_id: UUID) -> Optional[AvailabilityModel]:
    db_availability = db.query(AvailabilityModel).filter(AvailabilityModel.id == availability_id).first()
    if db_availability:
        db.delete(db_availability)
        db.commit()
    return db_availability

# ------------------------- FastAPI Router Endpoints -------------------------
availability_router = APIRouter()

@availability_router.post("/", response_model=Availability)
def create_new_availability(availability: AvailabilityCreate, db: Session = Depends(get_db)) -> AvailabilityModel:
    return create_availability(db, availability)

@availability_router.get("/person/{person_id}/availabilities", response_model=List[Availability])
def read_availabilities(
    person_id: UUID,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
) -> List[Availability]:
    return get_availabilities(db, person_id, skip=skip, limit=limit, person_id=person_id)

@availability_router.put("/{availability_id}", response_model=Availability)
def update_existing_availability(availability_id: UUID, availability: AvailabilityCreate, db: Session = Depends(get_db)):
    updated_availability = update_availability(db, availability_id, availability)
    if updated_availability is None:
        raise HTTPException(status_code=404, detail="Availability not found")
    return updated_availability

@availability_router.delete("/{availability_id}", response_model=Availability)
def delete_an_availability(availability_id: UUID, db: Session = Depends(get_db)):
    db_availability = delete_availability(db, availability_id)
    if db_availability is None:
        raise HTTPException(status_code=404, detail="Availability not found")
    return db_availability
