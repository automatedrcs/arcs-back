# Event router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import EventCreate, Event
from database.crud import get_events, create_event, get_event_by_id, update_event, delete_event

event_router = APIRouter()

@event_router.post("/", response_model=Event)
def create_new_event(event: EventCreate, db: Session = Depends(get_db)):
    return create_event(db, event)

@event_router.get("/", response_model=list[Event])
def read_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get a list of events. Can be paginated with skip and limit."""
    events = get_events(db, skip=skip, limit=limit)
    return events

@event_router.get("/{event_id}", response_model=Event)
def read_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event by its ID."""
    db_event = get_event_by_id(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@event_router.put("/{event_id}", response_model=Event)
def update_existing_event(event_id: int, event: EventCreate, db: Session = Depends(get_db)):
    updated_event = update_event(db, event_id, event)
    if updated_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@event_router.delete("/{event_id}", response_model=Event)
def delete_an_event(event_id: int, db: Session = Depends(get_db)):
    db_event = delete_event(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event
