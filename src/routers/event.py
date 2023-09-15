from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from database.database import get_db
from database.schema import EventCreate, Event, EventUpdate
from typing import List, Optional

# Event CRUD operations

def create_event(db: Session, event: EventCreate) -> Event:
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events(db: Session, skip: int, limit: int, **kwargs) -> List[Event]:
    query = db.query(Event)
    
    for key, value in kwargs.items():
        if value:
            query = query.filter(getattr(Event, key) == value)

    return query.offset(skip).limit(limit).all()

def update_event(db: Session, event_id: UUID, event: EventUpdate) -> Optional[Event]:
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event:
        for key, value in event.dict().items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
        return db_event
    return None

def delete_event(db: Session, event_id: UUID) -> Optional[Event]:
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
        return db_event
    return None

# Event router

event_router = APIRouter()

@event_router.post("/", response_model=Event)
def create_new_event(event: EventCreate, db: Session = Depends(get_db)):
    return create_event(db, event)

@event_router.get("/", response_model=List[Event])
def read_events(organization_id: Optional[int] = None, user_id: Optional[UUID] = None, 
                template_id: Optional[UUID] = None, job_id: Optional[UUID] = None, 
                skip: int = Query(0, ge=0), limit: int = Query(10, le=100), db: Session = Depends(get_db)):
    """Get a list of events based on provided filters."""
    return get_events(db, skip=skip, limit=limit, organization_id=organization_id, user_id=user_id, template_id=template_id, job_id=job_id)

@event_router.get("/{event_id}", response_model=Event)
def read_event_by_id(event_id: UUID, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        return event
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

@event_router.put("/{event_id}", response_model=Event)
def update_existing_event(event_id: UUID, event: EventUpdate, db: Session = Depends(get_db)):
    updated_event = update_event(db, event_id, event)
    if updated_event:
        return updated_event
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

@event_router.delete("/{event_id}", response_model=Event)
def delete_an_event(event_id: UUID, db: Session = Depends(get_db)):
    db_event = delete_event(db, event_id)
    if db_event:
        return db_event
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
