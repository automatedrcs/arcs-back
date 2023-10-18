# routers/calendar.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import database, models
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import googleapiclient
from utils import decrypt, get_secret
import requests
from datetime import datetime
from dateutil.parser import parse

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

    r = requests.post('https://oauth2.googleapis.com/token', data=data)
    return r.json()

async def fetch_google_calendar_events(db: Session, entity, start_time, end_time):
    if "authentication" not in entity.data or "google" not in entity.data["authentication"] or "refresh_token" not in entity.data["authentication"]["google"]:
        raise HTTPException(status_code=403, detail="Refresh Token required for Google Calendar operations")

    refresh_token = entity.data["authentication"]["google"]["refresh_token"]
    refreshed_token = refresh_google_token(refresh_token)

    if 'error' in refreshed_token or 'access_token' not in refreshed_token:
        print(f"Refresh token error: {refreshed_token.get('error_description', 'Unknown error')}")
        del entity.data["authentication"]["google"]["refresh_token"]
        db.commit()
        raise HTTPException(status_code=403, detail="Invalid Refresh Token")

    access_token = refreshed_token['access_token']
    credentials = Credentials(token=access_token)
    service = build("calendar", "v3", credentials=credentials)

    # Print out the start and end times
    print(f"Start time: {start_time.isoformat() + 'Z'}")
    print(f"End time: {end_time.isoformat() + 'Z'}")
    
    # Ensure the timezone information is included only once
    formatted_start_time = start_time.isoformat()
    formatted_end_time = end_time.isoformat()
    
    if not formatted_start_time.endswith('Z'):
        formatted_start_time += 'Z'
    
    if not formatted_end_time.endswith('Z'):
        formatted_end_time += 'Z'
        
    # Print out the start and end times
    print(f"Formatted Start time: {formatted_start_time}")
    print(f"Formatted End time: {formatted_end_time}")

    # Print out the access token (remove this after debugging!)
    print(f"Access Token: {access_token}")  # Please ensure this gets removed after debugging!

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=formatted_start_time,
            timeMax=formatted_end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except googleapiclient.errors.HttpError as error:
        print(f"Google Calendar API error: {error.resp.status} - {error.resp.reason}")
        if error.resp.status == 400:
            print(f"Error details: {error.content.decode('utf-8')}")
        raise HTTPException(status_code=500, detail="Error fetching Google Calendar events")

@calendar_router.get("/events/user")
async def get_user_calendar_events(
    user_id: str, 
    start_time: datetime = Query(..., format="%Y-%m-%dT%H:%M:%S"),
    end_time: datetime = Query(..., format="%Y-%m-%dT%H:%M:%S"),
    db: Session = Depends(database.get_db)
):
    user = get_user_by_id(db, user_id)
    return await fetch_google_calendar_events(db, user, start_time, end_time)