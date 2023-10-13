# routers/test.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import models, database
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils import decrypt, get_secret
import requests
from uuid import UUID

test_router = APIRouter()

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

    if response.status_code != 200:
        # Log or print the detailed error message from Google
        print("Error refreshing token:", response.text)

    response.raise_for_status()

    return response.json()

@test_router.get("/api/connection-test")
def test_connection(
    user_uuid: UUID = Header(...),  # This ensures that user_uuid is a required header
    db: Session = Depends(database.get_db)
):
    # Fetch the user using the provided UUID
    user = db.query(models.User).filter(models.User.id == user_uuid).first()
    if not user:
        return {"message": "Connection successful. No user found in the table.", "data": {}}

    google_auth = user.data.get("authentication", {}).get("google", {})
    refresh_token = google_auth.get("refresh_token")
    
    if not refresh_token:
        return {"message": "Connection successful. No Google Refresh Token found for the user.", "data": {}}

    decrypted_refresh_token = decrypt(refresh_token)
    if not decrypted_refresh_token:
        raise HTTPException(status_code=500, detail="Decryption failed or provided an empty refresh token.")  
    
    refreshed_token = refresh_google_token(refresh_token)
    if 'access_token' not in refreshed_token:
        raise HTTPException(status_code=500, detail="Failed to obtain access token.")

    credentials = Credentials(token=refreshed_token['access_token'])
    service = build("calendar", "v3", credentials=credentials)
    events_result = service.events().list(calendarId='primary', timeMax='2100-01-01T00:00:00Z', maxResults=1, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return {
        "message": "Successful calendar connection. Data fetched successfully.",
        "data": {
            "first_event": events[0] if events else "No events found in the calendar.",
            "refresh_token": refresh_token
        }
    }
