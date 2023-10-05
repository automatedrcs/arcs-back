from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from database import models, schema, database

# ------------------------- CRUD Operations -------------------------

def create_person(db: Session, person: schema.PersonCreate) -> models.Person:
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_people(
        db: Session,
        organization_id: int,
        person_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
) -> Union[models.Person, List[models.Person]]:
    query = db.query(models.Person)

    if person_id:
        return query.filter(models.Person.id == person_id).first()

    if organization_id:
        query = query.filter(models.Person.organization_id == organization_id)
        
    if user_id:
        query = query.filter(models.Person.user_id == user_id)

    if role:
        query = query.filter(models.Person.role == role)

    return query.offset(skip).limit(limit).all()

def update_person(db: Session, person_id: UUID, person: schema.PersonUpdate) -> Optional[models.Person]:
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person:
        for key, value in person.dict().items():
            setattr(db_person, key, value)
        db.commit()
        db.refresh(db_person)
    return db_person

def delete_person(db: Session, person_id: UUID) -> Optional[models.Person]:
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person:
        db.delete(db_person)
        db.commit()
    return db_person

# ------------------------- FastAPI Router Endpoints -------------------------

person_router = APIRouter()

@person_router.post("", response_model=schema.Person)
def create_new_person(person: schema.PersonCreate, db: Session = Depends(database.get_db)) -> models.Person:
    return create_person(db, person)

@person_router.get("/organization/{organization_id}/person/{person_id}", response_model=schema.Person)
def read_person_by_id(organization_id: int, person_id: UUID, db: Session = Depends(database.get_db)) -> schema.Person:
    db_person = get_people(db, organization_id, person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@person_router.get("/organization/{organization_id}/people", response_model=List[schema.Person])
def read_people(
        organization_id: int,
        user_id: Optional[UUID] = None,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(database.get_db)
) -> List[schema.Person]:
    people = get_people(db, organization_id, None, user_id, role, skip, limit)
    return people

@person_router.put("/{person_id}", response_model=schema.Person)
def update_existing_person(person_id: UUID, person: schema.PersonUpdate, db: Session = Depends(database.get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    return update_person(db, person_id, person)

@person_router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_person(person_id: UUID, db: Session = Depends(database.get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    delete_person(db, person_id)
    return
