# Notification router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import NotificationCreate, Notification
from database.crud import get_notifications, create_notification, get_notification_by_id, update_notification, delete_notification

notif_router = APIRouter()

@notif_router.post("/", response_model=Notification)
def create_new_notification(notif: NotificationCreate, db: Session = Depends(get_db)):
    return create_notification(db, notif)

@notif_router.get("/", response_model=list[Notification])
def read_notifications(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get a list of notifications. Can be paginated with skip and limit."""
    notifs = get_notifications(db, skip=skip, limit=limit)
    return notifs

@notif_router.get("/{notif_id}", response_model=Notification)
def read_notification(notif_id: int, db: Session = Depends(get_db)):
    """Get a specific notification by its ID."""
    db_notif = get_notification_by_id(db, notif_id)
    if db_notif is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notif

@notif_router.get("/user/{user_id}", response_model=list[Notification])
def read_notifications_by_user(user_id: int, db: Session = Depends(get_db)):
    """Get a list of notifications by user id."""
    notifs = get_notifications_by_user(db, user_id)
    return notifs

@notif_router.put("/{notif_id}", response_model=Notification)
def update_existing_notification(notif_id: int, notif: NotificationCreate, db: Session = Depends(get_db)):
    updated_notif = update_notification(db, notif_id, notif)
    if updated_notif is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return updated_notif

@notif_router.delete("/{notif_id}", response_model=Notification)
def delete_a_notification(notif_id: int, db: Session = Depends(get_db)):
    db_notif = delete_notification(db, notif_id)
    if db_notif is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notif
