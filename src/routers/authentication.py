from fastapi import APIRouter, Depends, HTTPException, Request, responses
from sqlalchemy.orm import Session
from database import database, schema, models
from utils import get_secret, encrypt, decrypt
import logging
import traceback
import requests

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

authentication_router = APIRouter()

@authentication_router.get('/google/login/user')
async def user_login(request: Request):
    try:
        BASE_URL = get_secret("BASE_URL")
        redirect_uri = f"{BASE_URL}/authentication/google/callback/user"
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={get_secret('GOOGLE_CLIENT_ID')}&redirect_uri={redirect_uri}&scope=https://www.googleapis.com/auth/calendar.readonly+https://www.googleapis.com/auth/userinfo.email"
        return responses.RedirectResponse(auth_url)
    except Exception as e:
        logger.error(traceback.format_exc())
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={str(e)}")

@authentication_router.get('/google/callback/user')
async def user_callback(code: str, db: Session = Depends(database.get_db)):
    try:
        redirect_uri = f"{get_secret('BASE_URL')}/authentication/google/callback/user"
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": get_secret('GOOGLE_CLIENT_ID'),
            "client_secret": get_secret('GOOGLE_CLIENT_SECRET'),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()
        access_token = tokens['access_token']
        
              # Fetch user email using access_token
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        user_info = response.json()
        user_email = user_info['email']

        # Store the refresh token for the user
        user = db.query(models.User).filter_by(email=user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.data is None:
            user.data = {}

        user.data.setdefault("authentication", {}).setdefault("google", {})["refresh_token"] = tokens['refresh_token']
        db.commit()

        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/success")
    
    except HTTPException as he:
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={he.detail}")
    except Exception as e:
        logger.error(traceback.format_exc())
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={str(e)}")

@authentication_router.get('/google/login/person')
async def person_login(request: Request):
    try:
        BASE_URL = get_secret("BASE_URL")
        redirect_uri = f"{BASE_URL}/authentication/google/callback/person"
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={get_secret('GOOGLE_CLIENT_ID')}&redirect_uri={redirect_uri}&scope=https://www.googleapis.com/auth/calendar.readonly+https://www.googleapis.com/auth/userinfo.email"
        return responses.RedirectResponse(auth_url)
    except Exception as e:
        logger.error(traceback.format_exc())
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={str(e)}")

@authentication_router.get('/google/callback/person')
async def person_callback(code: str, db: Session = Depends(database.get_db)):
    try:
        redirect_uri = f"{get_secret('BASE_URL')}/authentication/google/callback/person"
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": get_secret('GOOGLE_CLIENT_ID'),
            "client_secret": get_secret('GOOGLE_CLIENT_SECRET'),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()
        access_token = tokens['access_token']
        
        # Fetch person email using access_token
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        person_info = response.json()
        person_email = person_info['email']

        # Store the refresh token for the person
        person = db.query(models.Person).filter_by(email=person_email).first()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        if person.data is None:
            person.data = {}

        person.data.setdefault("authentication", {}).setdefault("google", {})["refresh_token"] = tokens['refresh_token']
        db.commit()

        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/success")

    except HTTPException as he:
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={he.detail}")
    except Exception as e:
        logger.error(traceback.format_exc())
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={str(e)}")

@authentication_router.get('/success')
async def success():
    FRONT_URL = get_secret("FRONT_URL")
    # You can send a response message or just redirect to your frontend's success page.
    return responses.RedirectResponse(url=f"{FRONT_URL}/authentication-success")

@authentication_router.get('/error')
async def error(detail: str):
    FRONT_URL = get_secret("FRONT_URL")
    # You can send a response message with the error or redirect to your frontend's error page with details.
    return responses.RedirectResponse(url=f"{FRONT_URL}/authentication-error?detail={detail}")