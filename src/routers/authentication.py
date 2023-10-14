# routers/authentication.py

from fastapi import APIRouter, Depends, HTTPException, Request, responses
from sqlalchemy.orm import Session
from database import database, schema, models
from utils import get_secret, encrypt, decrypt
from config import oauth
import logging
import traceback

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def handle_user_oauth_data(db: Session, user: dict, token: dict):
    try:
        refresh_token = token.get('refresh_token')
        print('Raw refresh token: ', refresh_token)

        encrypted_token = encrypt(refresh_token)
        decrypted_token = decrypt(encrypted_token)

        print("Encrypted:", encrypted_token)
        print("Decrypted:", decrypted_token)
        google_data = {
            "refresh_token": token.get('refresh_token', '')
        }

        user_db = db.query(models.User).filter(models.User.email == user["email"]).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        if user_db.data is None:
            user_db.data = {}
        if "authentication" not in user_db.data:
            user_db.data["authentication"] = {}
        user_db.data["authentication"]["google"] = google_data

        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def handle_person_oauth_data(db: Session, person: dict, token: dict):
    try:
        google_data = {
            "refresh_token": encrypt(token.get('refresh_token', ''))
        }

        person_db = db.query(models.Person).filter(models.Person.email == person["email"]).first()
        if not person_db:
            raise HTTPException(status_code=404, detail="Person not found")

        if person_db.data is None:
            person_db.data = {}
        if "authentication" not in person_db.data:
            person_db.data["authentication"] = {}
        person_db.data["authentication"]["google"] = google_data

        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

authentication_router = APIRouter()

@authentication_router.get('/google/login/user')
async def user_login(request: Request):
    try:
        BASE_URL = get_secret("BASE_URL")
        redirect_uri = f"{BASE_URL}/authentication/google/callback/user"
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@authentication_router.get('/google/login/person')
async def person_login(request: Request):
    try:
        BASE_URL = get_secret("BASE_URL")
        redirect_uri = f"{BASE_URL}/authentication/google/callback/person"
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@authentication_router.get('/google/callback/user', name="user_auth")
async def user_auth(request: Request, db: Session = Depends(database.get_db)):
    try:
        print("Initiating user_auth...")

        token = await oauth.google.authorize_access_token(request)
        print(f"Received token: {token}")

        userinfo = await oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        print("retrieved userinfo: ", str(userinfo))
        if "email" not in userinfo.json():
            logger.error("Email not found in the userinfo response.")
            print("print statement: Email not found in the userinfo response")
            raise HTTPException(status_code=400, detail="Email not found.")
        
        user_email = userinfo.json()["email"]

        handle_user_oauth_data(db, {"email": user_email}, token)
        logger.info("User OAuth data handled successfully.")

        return responses.RedirectResponse(url='/authentication/success')
    except HTTPException as he:
        return responses.RedirectResponse(url=f'/authentication/error?detail={he.detail}')
    except Exception as e:
        logger.error(f"Exception occurred in user_auth. Type: {type(e).__name__}, Message: {str(e)}, Traceback: {traceback.format_exc()}")
        return responses.RedirectResponse(url=f'/authentication/error?detail={str(e)}')

@authentication_router.get('/google/callback/person', name="person_auth")
async def person_auth(request: Request, db: Session = Depends(database.get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)

        userinfo = await oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        
        if "email" not in userinfo.json():
            logger.error("Email not found in the userinfo response.")
            raise HTTPException(status_code=400, detail="Email not found.")
        
        person_email = userinfo.json()["email"]

        handle_person_oauth_data(db, {"email": person_email}, token)
        return responses.RedirectResponse(url='/authentication/success')
    except HTTPException as he:
        return responses.RedirectResponse(url=f'/authentication/error?detail={he.detail}')
    except Exception as e:
        logger.error(f"Exception occurred in person_auth. Type: {type(e).__name__}, Message: {str(e)}, Traceback: {traceback.format_exc()}")
        return responses.RedirectResponse(url=f'/authentication/error?detail={str(e)}')

@authentication_router.get('/success')
async def success():
    FRONT_URL = get_secret("FRONT_URL")
    
    content = f"""
    <html>
        <head>
            <title>Authentication Successful</title>
            <script>
                setTimeout(function(){{
                    window.location.href = "{FRONT_URL}";
                }}, 4000);  // Redirects after 4 seconds
            </script>
        </head>
        <body>
            <h2>Authentication Successful! Redirecting...</h2>
        </body>
    </html>
    """
    return responses.HTMLResponse(content=content)

@authentication_router.get('/error')
async def error(detail: str):
    FRONT_URL = get_secret("FRONT_URL")
    
    content = f"""
    <html>
        <head>
            <title>Authentication Failed</title>
            <script>
                setTimeout(function(){{
                    window.location.href = "{FRONT_URL}";
                }}, 4000);  // Redirects after 4 seconds
            </script>
        </head>
        <body>
            <h2>Authentication Failed: {detail}. Redirecting...</h2>
        </body>
    </html>
    """
    return responses.HTMLResponse(content=content)