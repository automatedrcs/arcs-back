from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from fastapi import Depends
from utils import get_secret

async def get_calendar():
    api_key = await get_secret("API_KEY")
    # The authentication here depends on how exactly you've set up your Google services.
    # If you're using OAuth2, you might need more than just an API key.
    # Here's a simple example using only the API key:
    service = build("calendar", "v3", developerKey=api_key)
    return service

def calendar_dependency() -> str:
    return Depends(get_calendar)

calendar = calendar_dependency()
