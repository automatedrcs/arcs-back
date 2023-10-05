from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from database import database, models, schema

# ------------------------- CRUD Operations -------------------------

def get_availabilities(db: Session, person_id: UUID, availability_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[models.Availability]:
    query = db.query(models.Availability).filter(models.Availability.person_id == person_id)
    
    if availability_id:
        return [query.filter(models.Availability.id == availability_id).first()]

    return query.offset(skip).limit(limit).all()

def create_availability(db: Session, availability: schema.AvailabilityCreate) -> models.Availability:
    db_availability = models.Availability(**availability.dict())
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

def update_availability(db: Session, availability_id: UUID, availability: schema.AvailabilityUpdate) -> Optional[models.Availability]:
    db_availability = db.query(models.Availability).filter(models.Availability.id == availability_id).first()
    if db_availability:
        for key, value in availability.dict().items():
            setattr(db_availability, key, value)
        db.commit()
        db.refresh(db_availability)
    return db_availability

def delete_availability(db: Session, availability_id: UUID) -> Optional[models.Availability]:
    db_availability = db.query(models.Availability).filter(models.Availability.id == availability_id).first()
    if db_availability:
        db.delete(db_availability)
        db.commit()
    return db_availability

# ------------------------- FastAPI Router Endpoints -------------------------
availability_router = APIRouter()

@availability_router.post("", response_model=schema.Availability)
def create_new_availability(availability: schema.AvailabilityCreate, db: Session = Depends(database.get_db)):
    return create_availability(db, availability)

@availability_router.get("/person/{person_id}", response_model=List[schema.Availability])
def read_availabilities(person_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return get_availabilities(db, person_id, skip=skip, limit=limit)

@availability_router.put("/{availability_id}", response_model=schema.Availability)
def update_existing_availability(availability_id: UUID, availability: schema.AvailabilityUpdate, db: Session = Depends(database.get_db)):
    updated_availability = update_availability(db, availability_id, availability)
    if not updated_availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    return updated_availability

@availability_router.delete("/{availability_id}", response_model=schema.Availability)
def delete_an_availability(availability_id: UUID, db: Session = Depends(database.get_db)):
    db_availability = delete_availability(db, availability_id)
    if not db_availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    return db_availability
