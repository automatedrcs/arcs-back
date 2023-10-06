from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import database, models
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

calendar_router = APIRouter()

def get_user_by_id(db: Session, user_id: str) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@calendar_router.get("/events")
async def get_user_calendar_events(
    user_id: str, 
    start_time: str, 
    end_time: str, 
    db: Session = Depends(database.get_db)
):
    user = get_user_by_id(db, user_id)
    if not user.access_token:
        raise HTTPException(status_code=403, detail="Access Token required for Google Calendar operations")

    # Use the user's decrypted access token to authenticate and get their Google Calendar data
    credentials = Credentials(token=user.access_token)
    service = build("calendar", "v3", credentials=credentials)

    # Fetch events for the user within the given time range
    events_result = service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events
