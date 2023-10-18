# routers/calendar.py
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import googleapiclient
from dateutil.parser import parse
import requests

from database import database, models
from utils import decrypt, get_secret

calendar_router = APIRouter()


def get_user_by_id(db: Session, user_id: str) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def refresh_google_token(refresh_token: str) -> dict:
    client_id = get_secret("CLIENT_ID")
    client_secret = get_secret("CLIENT_SECRET")

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': decrypt(refresh_token),
        'grant_type': 'refresh_token'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data)
    return response.json()


async def fetch_google_calendar_events(db: Session, entity, start_time, end_time):
    if "authentication" not in entity.data or "google" not in entity.data["authentication"] or "refresh_token" not in entity.data["authentication"]["google"]:
        raise HTTPException(status_code=403, detail="Refresh Token required for Google Calendar operations")

    refresh_token = entity.data["authentication"]["google"]["refresh_token"]
    refreshed_token = refresh_google_token(refresh_token)

    if 'error' in refreshed_token or 'access_token' not in refreshed_token:
        raise HTTPException(status_code=403, detail="Invalid Refresh Token")

    credentials = Credentials(token=refreshed_token['access_token'])
    service = build("calendar", "v3", credentials=credentials)

    datetime_formats = [
        ('Original Format', '%Y-%m-%dT%H:%M:%SZ'),
        ('SO Answer 1', '%Y-%m-%dT%H:%M:%S'),
        ('SO Answer 2', '%Y-%m-%dT%H:%M:%S.%fZ'),
        ('SO Answer 3 (only datetime)', '%Y-%m-%dT%H:%M:%S.%f'),
    ]

    for format_name, date_format in datetime_formats:
        timeMin_test = start_time.strftime(date_format)
        timeMax_test = end_time.strftime(date_format)
        
        print(f"Testing {format_name}: Start Time - {timeMin_test}, End Time - {timeMax_test}")
        
        try:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=timeMin_test,
                timeMax=timeMax_test,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            print(f"{format_name} - SUCCESS!")
            return events_result.get('items', [])
        except googleapiclient.errors.HttpError as error:
            print(f"{format_name} - FAILED with error: {error}")

    raise HTTPException(status_code=500, detail="All date formats failed for Google Calendar events")


@calendar_router.get("/events/user")
async def get_user_calendar_events(
    user_id: str, 
    start_time: datetime = Query(..., format="%Y-%m-%dT%H:%M:%S"),
    end_time: datetime = Query(..., format="%Y-%m-%dT%H:%M:%S"),
    db: Session = Depends(database.get_db)
):
    user = get_user_by_id(db, user_id)
    return await fetch_google_calendar_events(db, user, start_time, end_time)
