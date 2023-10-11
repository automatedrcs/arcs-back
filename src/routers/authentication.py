# routers/authentication.py
# prefix "/authentication"

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import database, schema
from utils import get_secret, encrypt
from config import oauth

# ------------------------- CRUD Operations -------------------------

def update_person_data_by_email(db: Session, email: str, data: dict) -> schema.Person:
    person = db.query(schema.Person).filter(schema.Person.email == email).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    for key, value in data.items():
        setattr(person, key, value)

    db.commit()
    db.refresh(person)
    return person

def handle_user_oauth_data(db: Session, user: dict, token: dict):
    google_data = {
        "access_token": encrypt(token.get('access_token')),
        "id_token": encrypt(token.get('id_token')),
    }
    
    if 'refresh_token' in token:
        google_data["refresh_token"] = encrypt(token.get('refresh_token'))

    user_db = db.query(schema.User).filter(schema.User.email == user["email"]).first()
    
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    # Save Google Calendar data to user's data field
    if user_db.data is None:
        user_db.data = {}
    if "authentication" not in user_db.data:
        user_db.data["authentication"] = {}
    user_db.data["authentication"]["google"] = google_data

    db.commit()


# ------------------------- FastAPI Router Endpoints -------------------------

authentication_router = APIRouter()

@authentication_router.get('/google/login')
async def login(request: Request):
    BASE_URL = get_secret("BASE_URL")
    redirect_uri = f"{BASE_URL}/authentication/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@authentication_router.get('/google/callback', name="auth")
async def auth(request: Request, db: Session = Depends(database.get_db)):
    token = await oauth.google.authorize_access_token(request)
    
    # To ensure the token includes id_token for OIDC
    if 'id_token' not in token:
        raise HTTPException(status_code=400, detail="Missing id_token")
    
    user_info = oauth.google.parse_id_token(request, token)

    # Use the email in the user_info to fetch or create the user from your db.
    handle_user_oauth_data(db, user_info, token)

    return {"token": token.get('access_token', ''), "user": user_info}
