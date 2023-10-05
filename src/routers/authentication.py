from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import database, schema
from utils import encrypt
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
    if 'refresh_token' in token:
        encrypted_refresh_token = encrypt(token['refresh_token'])
        update_person_data_by_email(db, user["email"], {"refresh_token": encrypted_refresh_token})

# ------------------------- FastAPI Router Endpoints -------------------------

authentication_router = APIRouter()

@authentication_router.get('/google/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@authentication_router.get('/google/callback')
def auth(request: Request, db: Session = Depends(database.get_db)):
    try:
        token = oauth.google.authorize_access_token(request)
        user = oauth.google.parse_id_token(request, token)
        handle_user_oauth_data(db, user, token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth2 error: {e}")

    return {"token": token.get('access_token', ''), "user": user}
