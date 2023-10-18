# routers/calendar.py
# prefix "/calendar"

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import database, models
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils import decrypt, get_secret
import requests
from datetime import datetime

calendar_router = APIRouter()

def get_user_by_id(db: Session, user_id: str) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_person_by_id(db: Session, person_id: str) -> models.Person:
    person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

def refresh_google_token(refresh_token: str) -> dict:
    client_id = get_secret("CLIENT_ID")
    client_secret = get_secret("CLIENT_SECRET")

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': decrypt(refresh_token),
        'grant_type': 'refresh_token'
    }

    r = requests.post('https://oauth2.googleapis.com/token', data=data)
    return r.json()

async def fetch_google_calendar_events(entity, start_time, end_time):
    if "authentication" not in entity.data or "google" not in entity.data["authentication"] or "refresh_token" not in entity.data["authentication"]["google"]:
        raise HTTPException(status_code=403, detail="Refresh Token required for Google Calendar operations")
    print("in fetch_google_calendar_events")
    refresh_token = decrypt(entity.data["authentication"]["google"]["refresh_token"])
    print("refresh_token: ", str(refresh_token))    
    refreshed_token = refresh_google_token(refresh_token)
    access_token = refreshed_token['access_token']
    print("access_token: ", str(access_token))
    credentials = Credentials(token=access_token)
    service = build("calendar", "v3", credentials=credentials)
    print("service built")
    events_result = service.events().list(calendarId='primary', timeMin=start_time.isoformat() + 'Z', timeMax=end_time.isoformat() + 'Z', singleEvents=True, orderBy='startTime').execute()
    print("events_result: ", events_result)
    return events_result.get('items', [])

@calendar_router.get("/events/user")
async def get_user_calendar_events(
    user_id: str, 
    start_time: datetime = Query(..., format="%Y-%m-%dT%H:%M:%S"),
    end_time: datetime = Query(..., format="%Y-%m-%dT%H:%M:%S"),
    db: Session = Depends(database.get_db)
):
    print("events/user endpoint called")
    user = get_user_by_id(db, user_id)
    print("user: ", str(user.username))
    return await fetch_google_calendar_events(user, start_time, end_time)

@calendar_router.get("/events/person")
async def get_person_calendar_events(
    person_id: str, 
    start_time: datetime = Query(..., format="%Y-%m-%dT%H:%M:%S"),
    end_time: datetime = Query(..., format="%Y-%m-%dT%H:%M:%S"),
    db: Session = Depends(database.get_db)
):
    person = get_person_by_id(db, person_id)
    return await fetch_google_calendar_events(person, start_time, end_time)
