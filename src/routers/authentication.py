# routers/authentication.py
# prefix "/authentication"

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import database, schema
from utils import get_secret
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
        "access_token": token.get('access_token'),
        "id_token": token.get('id_token'),
        "refresh_token": token.get('refresh_token') if 'refresh_token' in token else None
    }

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
def auth(request: Request, db: Session = Depends(database.get_db)):
    try:
        token = oauth.google.authorize_access_token(request)
        user = oauth.google.parse_id_token(request, token)
        handle_user_oauth_data(db, user, token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth2 error: {e}")

    return {"token": token.get('access_token', ''), "user": user}
