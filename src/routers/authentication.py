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
    BASE_URL = get_secret("BASE_URL")
    redirect_uri = f"{BASE_URL}/authentication/google/callback/user"
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={get_secret('CLIENT_ID')}&redirect_uri={redirect_uri}&scope=https://www.googleapis.com/auth/calendar.readonly+https://www.googleapis.com/auth/userinfo.email&prompt=consent&access_type=offline"
    return responses.RedirectResponse(auth_url)

@authentication_router.get('/google/callback/user')
async def user_callback(code: str, db: Session = Depends(database.get_db)):
    try:
        redirect_uri = f"{get_secret('BASE_URL')}/authentication/google/callback/user"
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": get_secret('CLIENT_ID'),
            "client_secret": get_secret('CLIENT_SECRET'),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()

        print("tokens: ", str(tokens))
        access_token = tokens['access_token']

        # Fetch user email using access_token
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        user_info = response.json()
        user_email = user_info['email']
        print("user email: ", str(user_email))

        # Store the refresh token for the user
        user = db.query(models.User).filter_by(email=user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("user: ", str(user.id))
        print(str(user.email))
        if user.data is None:
            user.data = {}

        if 'refresh_token' in tokens:
            encrypted_refresh_token = encrypt(tokens.get('refresh_token'))
            print("encrypted refresh token: ", encrypted_refresh_token)
            if not user.data.get("authentication"):
                print("user.data: ", str(user.data))
                user.data["authentication"] = {}
                print("user.data: ", str(user.data))
            if not user.data["authentication"].get("google"):
                user.data["authentication"]["google"] = {}
                print("user.data: ", str(user.data))
            user.data["authentication"]["google"]["refresh_token"] = encrypted_refresh_token
            print("user.data: ", str(user.data))
        else:
            # Decide how you want to handle the lack of a refresh token. For now, I'll leave this as a log message.
            print(f"No refresh token found for user {user_email}.")

        db.commit()
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/success")
    except HTTPException as he:
        print("HTTPException error: ", he)
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={he.detail}")
    except Exception as e:
        print(traceback.format_exc())
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={str(e)}")

@authentication_router.get('/google/login/person')
async def person_login(request: Request):
    BASE_URL = get_secret("BASE_URL")
    redirect_uri = f"{BASE_URL}/authentication/google/callback/person"
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={get_secret('CLIENT_ID')}&redirect_uri={redirect_uri}&scope=https://www.googleapis.com/auth/calendar.events+https://www.googleapis.com/auth/userinfo.email&prompt=consent&access_type=offline"
    return responses.RedirectResponse(auth_url)

@authentication_router.get('/google/callback/person')
async def person_callback(code: str, db: Session = Depends(database.get_db)):
    try:
        redirect_uri = f"{get_secret('BASE_URL')}/authentication/google/callback/person"
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": get_secret('CLIENT_ID'),
            "client_secret": get_secret('CLIENT_SECRET'),
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

        if 'refresh_token' in tokens:
            encrypted_refresh_token = encrypt(tokens['refresh_token'])

            if not person.data.get("authentication"):
                person.data["authentication"] = {}
            if not person.data["authentication"].get("google"):
                person.data["authentication"]["google"] = {}
            person.data["authentication"]["google"]["refresh_token"] = encrypted_refresh_token
        else:
            # Decide how you want to handle the lack of a refresh token. For now, I'll leave this as a log message.
            print(f"No refresh token found for person {person_email}.")

        db.commit()
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/success")
    except HTTPException as he:
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={he.detail}")
    except Exception as e:
        logger.error(traceback.format_exc())
        return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/error?detail={str(e)}")

@authentication_router.get('/success')
async def success():
    return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/authentication-success")

@authentication_router.get('/error')
async def error(detail: str):
    return responses.RedirectResponse(url=f"{get_secret('FRONT_URL')}/authentication-error?detail={detail}")
