from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from database.database import get_db
from database.schema import MeetingCreate, Meeting, MeetingUpdate
from typing import List, Optional

# Meeting CRUD operations

def create_meeting(db: Session, meeting: MeetingCreate) -> Meeting:
    db_meeting = Meeting(**meeting.dict())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

def get_meetings(db: Session, skip: int, limit: int, **kwargs) -> List[Meeting]:
    query = db.query(Meeting)
    
    for key, value in kwargs.items():
        if value:
            query = query.filter(getattr(Meeting, key) == value)

    return query.offset(skip).limit(limit).all()

def update_meeting(db: Session, meeting_id: UUID, meeting: MeetingUpdate) -> Optional[Meeting]:
    db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if db_meeting:
        for key, value in meeting.dict().items():
            setattr(db_meeting, key, value)
        db.commit()
        db.refresh(db_meeting)
        return db_meeting
    return None

def delete_meeting(db: Session, meeting_id: UUID) -> Optional[Meeting]:
    db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if db_meeting:
        db.delete(db_meeting)
        db.commit()
        return db_meeting
    return None

# Meeting router

meeting_router = APIRouter()

@meeting_router.post("/", response_model=Meeting)
def create_new_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    return create_meeting(db, meeting)

@meeting_router.get("/", response_model=List[Meeting])
def read_meetings(organization_id: Optional[int] = None, user_id: Optional[UUID] = None, 
                template_id: Optional[UUID] = None, job_id: Optional[UUID] = None, 
                skip: int = Query(0, ge=0), limit: int = Query(10, le=100), db: Session = Depends(get_db)):
    """Get a list of meetings based on provided filters."""
    return get_meetings(db, skip=skip, limit=limit, organization_id=organization_id, user_id=user_id, template_id=template_id, job_id=job_id)

@meeting_router.get("/{meeting_id}", response_model=Meeting)
def read_meeting_by_id(meeting_id: UUID, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting:
        return meeting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

@meeting_router.put("/{meeting_id}", response_model=Meeting)
def update_existing_meeting(meeting_id: UUID, meeting: MeetingUpdate, db: Session = Depends(get_db)):
    updated_meeting = update_meeting(db, meeting_id, meeting)
    if updated_meeting:
        return updated_meeting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

@meeting_router.delete("/{meeting_id}", response_model=Meeting)
def delete_an_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    db_meeting = delete_meeting(db, meeting_id)
    if db_meeting:
        return db_meeting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
