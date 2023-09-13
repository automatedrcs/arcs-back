# Person router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import PersonCreate, Person
from database.crud import get_people, create_person, get_person_by_id, update_person, delete_person

person_router = APIRouter()

@person_router.post("/", response_model=Person)
def create_new_person(person: PersonCreate, db: Session = Depends(get_db)):
    return create_person(db, person)

@person_router.get("/", response_model=list[Person])
def read_people(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get a list of people. Can be paginated with skip and limit."""
    people = get_people(db, skip=skip, limit=limit)
    return people

@person_router.get("/{person_id}", response_model=Person)
def read_person(person_id: int, db: Session = Depends(get_db)):
    """Get a specific person by its ID."""
    db_person = get_person_by_id(db, person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@person_router.put("/{person_id}", response_model=Person)
def update_existing_person(person_id: int, person: PersonCreate, db: Session = Depends(get_db)):
    updated_person = update_person(db, person_id, person)
    if updated_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return updated_person

@person_router.delete("/{person_id}", response_model=Person)
def delete_a_person(person_id: int, db: Session = Depends(get_db)):
    db_person = delete_person(db, person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person
