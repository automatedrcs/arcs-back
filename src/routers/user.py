from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from routers.auth import oauth2_scheme, credentials_exception, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from utils import get_secret, encrypt, decrypt
from database.crud import get_user_by_username, create_user, update_user_tokens_by_username
from database.database import get_db
from sqlalchemy.orm import Session
import jwt
import bcrypt

user_router = APIRouter()

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@user_router.post("/signup/")
async def signup(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = hash_password(password)
    create_user(db, username, hashed_password)  # You might need to add other fields based on the user model
    return {"message": "User created successfully"}

@user_router.post("/login/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    stored_user = get_user_by_username(db, form_data.username)

    if not stored_user or not verify_password(form_data.password, stored_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    refresh_token = create_refresh_token(data={"sub": form_data.username})
    
    update_user_tokens_by_username(db, form_data.username, access_token, refresh_token)  # Save the tokens in the user table
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@user_router.post("/token/refresh/")
def refresh_token(refresh_token: str):
    new_access_token = create_access_token(data={"sub": "test"})  # Replace 'test' with logic to get the user from the refresh token
    return {"access_token": new_access_token, "token_type": "bearer"}

# Helper functions for token creation, moved from auth.py
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
