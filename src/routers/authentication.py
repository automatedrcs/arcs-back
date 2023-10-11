# routers/authentication.py
# prefix "/authentication"

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import database, schema, models
from utils import get_secret, encrypt
from config import oauth

# ------------------------- CRUD Operations -------------------------

def update_data_by_email(db: Session, email: str, data: dict, model: any) -> any:
    instance = db.query(model).filter(model.email == email).first()
    if not instance:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")

    for key, value in data.items():
        setattr(instance, key, value)

    db.commit()
    db.refresh(instance)
    return instance

def handle_oauth_data(db: Session, user: dict, token: dict, model: any):
    google_data = {
        "refresh_token": encrypt(token.get('refresh_token', ''))
    }

    instance = db.query(model).filter(model.email == user["email"]).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")

    if instance.data is None:
        instance.data = {}
    if "authentication" not in instance.data:
        instance.data["authentication"] = {}
    instance.data["authentication"]["google"] = google_data

    db.commit()

# ------------------------- FastAPI Router Endpoints -------------------------

authentication_router = APIRouter()

@authentication_router.get('/google/login/user')
async def user_login(request: Request):
    BASE_URL = get_secret("BASE_URL")
    redirect_uri = f"{BASE_URL}/authentication/google/callback/user"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@authentication_router.get('/google/login/person')
async def person_login(request: Request):
    BASE_URL = get_secret("BASE_URL")
    redirect_uri = f"{BASE_URL}/authentication/google/callback/person"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@authentication_router.get('/google/callback/user', name="user_auth")
async def user_auth(request: Request, db: Session = Depends(database.get_db)):
    token = await oauth.google.authorize_access_token(request)
    
    if 'id_token' not in token:
        raise HTTPException(status_code=400, detail="Missing id_token")
    
    user_info = oauth.google.parse_id_token(request, token)
    handle_oauth_data(db, user_info, token, models.User)

    return {"token": token.get('access_token', ''), "user": user_info}

@authentication_router.get('/google/callback/person', name="person_auth")
async def person_auth(request: Request, db: Session = Depends(database.get_db)):
    token = await oauth.google.authorize_access_token(request)
    
    if 'id_token' not in token:
        raise HTTPException(status_code=400, detail="Missing id_token")
    
    user_info = oauth.google.parse_id_token(request, token)
    handle_oauth_data(db, user_info, token, models.Person)

    return {"user": user_info}
