from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from database.database import get_db
from database import schema, models

# ------------------------- CRUD Operations -------------------------

def create_notification(db: Session, notification: schema.NotificationCreate) -> models.Notification:
    db_notification = models.Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications(
        db: Session,
        organization_id: int,
        notification_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
) -> Union[models.Notification, List[models.Notification]]:
    query = db.query(models.Notification)

    # Apply filters based on provided parameters
    if notification_id:
        return query.filter(models.Notification.id == notification_id).first()
    
    # Always filter by organization
    query = query.filter(models.Notification.organization_id == organization_id)

    if user_id:
        query = query.filter(models.Notification.user_id == user_id)

    return query.offset(skip).limit(limit).all()

def update_notification(db: Session, notification_id: UUID, notification: schema.NotificationUpdate) -> Optional[models.Notification]:
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if db_notification:
        for key, value in notification.dict().items():
            setattr(db_notification, key, value)
        db.commit()
        db.refresh(db_notification)
    return db_notification

def delete_notification(db: Session, notification_id: UUID) -> bool:
    """Returns True if deletion was successful, otherwise False."""
    rows_deleted = db.query(models.Notification).filter(models.Notification.id == notification_id).delete()
    db.commit()
    return bool(rows_deleted)

# ------------------------- FastAPI Router Endpoints -------------------------

notification_router = APIRouter()

@notification_router.post("/notifications/", response_model=schema.Notification)
def create_notification_endpoint(notification: schema.NotificationCreate, db: Session = Depends(get_db)) -> models.Notification:
    return create_notification(db=db, notification=notification)

@notification_router.get("/notifications/", response_model=List[schema.Notification])
def read_notifications(
        organization_id: int,
        notification_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=0, le=500),
        db: Session = Depends(get_db)
) -> List[models.Notification]:
    return get_notifications(db, organization_id, notification_id, user_id, skip, limit)

@notification_router.put("/notifications/{notification_id}", response_model=schema.Notification)
def update_notification_endpoint(notification_id: UUID, notification: schema.NotificationUpdate, db: Session = Depends(get_db)):
    db_notification = update_notification(db, notification_id, notification)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notification

@notification_router.delete("/notifications/{notification_id}", response_model=schema.Notification)
def delete_notification_endpoint(notification_id: UUID, db: Session = Depends(get_db)):
    was_deleted = delete_notification(db, notification_id)
    if not was_deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"id": notification_id, "status": "deleted"}