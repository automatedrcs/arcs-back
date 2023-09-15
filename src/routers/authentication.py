from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from utils import get_secret, encrypt
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import Person

def update_person_data_by_email(db: Session, email: str, data: dict):
    person = db.query(Person).filter(Person.email == email).first()
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

# Setting up OAuth2.0
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=get_secret("CLIENT_ID"),
    client_secret=get_secret("CLIENT_SECRET"),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    redirect_uri=get_secret("REDIRECT_URL"),
    client_kwargs={'scope': 'openid profile email'},
)

authentication_router = APIRouter()

@authentication_router.get('/google/login')
async def login(request: Request):
    redirect_uri = url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@authentication_router.get('/google/callback')
def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = oauth.google.authorize_access_token(request)
        user = oauth.google.parse_id_token(request, token)
        handle_user_oauth_data(db, user, token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth2 error: {e}")
    
    return {"token": token.get('access_token', ''), "user": user}