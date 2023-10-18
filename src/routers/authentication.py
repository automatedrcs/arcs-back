from fastapi import APIRouter, Depends, HTTPException, Request, responses
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from database import database, schema, models
from utils import encrypt, decrypt
from config import BASE_URL, CLIENT_ID, CLIENT_SECRET, FRONT_URL, logger
import traceback
import requests

authentication_router = APIRouter()

def generate_google_auth_url(endpoint: str, scope: str) -> str:
    redirect_uri = f"{BASE_URL}{endpoint}"
    return f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri}&scope={scope}&prompt=consent&access_type=offline"


def store_refresh_token(tokens: dict, model, email: str, db: Session):
    instance = db.query(model).filter_by(email=email).first()
    if not instance:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    
    instance.data = instance.data or {}
    if 'refresh_token' in tokens:
        encrypted_refresh_token = encrypt(tokens['refresh_token'])
        instance.data.setdefault("authentication", {}).setdefault("google", {})["refresh_token"] = encrypted_refresh_token

        db.add(instance)
        flag_modified(instance, "data")
        db.commit()
    else:
        logger.warning(f"No refresh token found for {model.__name__} {email}")


@authentication_router.get('/google/login/user')
async def user_login():
    auth_url = generate_google_auth_url(BASE_URL, '/authentication/google/callback/user', 'https://www.googleapis.com/auth/calendar.readonly+https://www.googleapis.com/auth/userinfo.email')
    return responses.RedirectResponse(auth_url)


@authentication_router.get('/google/callback/user')
async def user_callback(code: str, db: Session = Depends(database.get_db)):
    try:
        # Getting the access token
        redirect_uri = f"{BASE_URL}/authentication/google/callback/user"
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()
        access_token = tokens['access_token']

        # Fetch user email
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        user_email = response.json()['email']

        # Store refresh token
        store_refresh_token(data, tokens, models.User, user_email, db)

        return responses.RedirectResponse(url=f"{FRONT_URL}/success")
    except HTTPException as he:
        logger.error(f"HTTPException error: {he}")
        return responses.RedirectResponse(url=f"{FRONT_URL}/error?detail={he.detail}")
    except Exception as e:
        logger.error(traceback.format_exc())
        return responses.RedirectResponse(url=f"{FRONT_URL}/error?detail={str(e)}")


@authentication_router.get('/google/login/person')
async def person_login():
    auth_url = generate_google_auth_url(BASE_URL, '/authentication/google/callback/person', 'https://www.googleapis.com/auth/calendar.events+https://www.googleapis.com/auth/userinfo.email')
    return responses.RedirectResponse(auth_url)


@authentication_router.get('/google/callback/person')
async def person_callback(code: str, db: Session = Depends(database.get_db)):
    try:
        # Getting the access token
        redirect_uri = f"{BASE_URL}/authentication/google/callback/person"
        data = {
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()
        access_token = tokens['access_token']

        # Fetch person email
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        person_email = response.json()['email']

        # Store refresh token
        store_refresh_token(data, tokens, models.Person, person_email, db)

        return responses.RedirectResponse(url=f"{FRONT_URL}/success")
    except HTTPException as he:
        logger.error(f"HTTPException error: {he}")
        return responses.RedirectResponse(url=f"{FRONT_URL}/error?detail={he.detail}")
    except Exception as e:
        logger.error(traceback.format_exc())
        return responses.RedirectResponse(url=f"{FRONT_URL}/error?detail={str(e)}")


@authentication_router.get('/success')
async def success():
    return responses.RedirectResponse(url=f"{FRONT_URL}/authentication-success")


@authentication_router.get('/error')
async def error(detail: str):
    return responses.RedirectResponse(url=f"{FRONT_URL}/authentication-error?detail={detail}")
