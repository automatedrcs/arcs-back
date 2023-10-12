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

    r = requests.post('https://oauth2.googleapis.com/token', data=data)
    if r.status_code != 200:
        raise Exception(f"Failed to refresh token. Google response: {r.json()}")
    return r.json()

@test_router.get("/api/connection-test")
def test_connection(
    user_uuid: UUID = Header(None),  # Add this line to get the user UUID from the header
    db: Session = Depends(database.get_db)
):
    try:
        if not user_uuid:
            raise HTTPException(status_code=400, detail="User UUID not provided in the request header.")
        
        # Fetch the user using the provided UUID
        user = db.query(models.User).filter(models.User.id == user_uuid).first()

        
        if not user:
            return {"message": "Connection successful. No user found in the table.", "data": {}}

        if "authentication" not in user.data or "google" not in user.data["authentication"] or "refresh_token" not in user.data["authentication"]["google"]:
            return {"message": "Connection successful. No Google Refresh Token found for the user.", "data": {}}

        refreshed_token = refresh_google_token(user.data["authentication"]["google"]["refresh_token"])
        if 'access_token' not in refreshed_token:
            raise Exception(f"Failed to obtain access token. Response: {refreshed_token}")

        access_token = refreshed_token['access_token']

        credentials = Credentials(token=access_token)
        service = build("calendar", "v3", credentials=credentials)

        events_result = service.events().list(calendarId='primary', timeMax='2100-01-01T00:00:00Z', maxResults=1, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        return {
            "message": "Successful calendar connection. Data fetched successfully.",
            "data": {
                "first_event": events[0] if events else "No events found in the calendar.",
                "refresh_token": user.data["authentication"]["google"]["refresh_token"]
            }
        }
    except Exception as e:
        # If there's an error related to database connection, API call, or query execution
        raise HTTPException(status_code=500, detail=str(e))
