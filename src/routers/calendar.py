# routers/calendar.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import database, models
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils import decrypt
import requests

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

@calendar_router.get("/events/user")
async def get_user_calendar_events(
    user_id: str, 
    start_time: str, 
    end_time: str, 
    db: Session = Depends(database.get_db)
):
    user = get_user_by_id(db, user_id)
    
    if "authentication" not in user.data or "google" not in user.data["authentication"] or "refresh_token" not in user.data["authentication"]["google"]:
        raise HTTPException(status_code=403, detail="Refresh Token required for Google Calendar operations")

    refreshed_token = refresh_google_token(user.data["authentication"]["google"]["refresh_token"])
    access_token = refreshed_token['access_token']

    credentials = Credentials(token=access_token)
    service = build("calendar", "v3", credentials=credentials)

    events_result = service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events

@calendar_router.get("/events/person")
async def get_person_calendar_events(
    person_id: str, 
    start_time: str, 
    end_time: str, 
    db: Session = Depends(database.get_db)
):
    person = get_person_by_id(db, person_id)
    
    if "authentication" not in person.data or "google" not in person.data["authentication"] or "refresh_token" not in person.data["authentication"]["google"]:
        raise HTTPException(status_code=403, detail="Refresh Token required for Google Calendar operations")

    refreshed_token = refresh_google_token(person.data["authentication"]["google"]["refresh_token"])
    access_token = refreshed_token['access_token']

    credentials = Credentials(token=access_token)
    service = build("calendar", "v3", credentials=credentials)

    events_result = service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events
