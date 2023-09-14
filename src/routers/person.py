from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from database.database import get_db
from database.schema import PersonCreate, PersonUpdate, Person
from database.crud import (
    get_people, 
    create_person,
    update_person, 
    delete_person
)

person_router = APIRouter()

@person_router.post("/", response_model=Person)
def create_new_person(person: PersonCreate, db: Session = Depends(get_db)):
    return create_person(db, person)

@person_router.get("/{person_id}", response_model=Person)
def read_person(person_id: UUID, db: Session = Depends(get_db)):
    db_person = get_people(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@person_router.get("/organization/{org_id}", response_model=list[Person])
def read_people_by_organization(org_id: UUID, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_people(db, org_id=org_id, skip=skip, limit=limit)

@person_router.get("/user/{user_id}", response_model=list[Person])
def read_people_by_user(user_id: UUID, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_people(db, user_id=user_id, skip=skip, limit=limit)

@person_router.get("/user/{user_id}/role/{role}", response_model=list[Person])
def read_people_by_user_and_role(user_id: UUID, role: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_people(db, user_id=user_id, role=role, skip=skip, limit=limit)

@person_router.get("/organization/{org_id}/role/{role}", response_model=list[Person])
def read_people_by_organization_and_role(org_id: UUID, role: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_people(db, org_id=org_id, role=role, skip=skip, limit=limit)

@person_router.put("/{person_id}", response_model=Person)
def update_existing_person(person_id: UUID, person: PersonUpdate, db: Session = Depends(get_db)):
    updated_person = update_person(db, person_id, person)
    if updated_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return updated_person

@person_router.delete("/{person_id}", response_model=Person)
def delete_a_person(person_id: UUID, db: Session = Depends(get_db)):
    db_person = delete_person(db, person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person
