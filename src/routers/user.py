from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from routers.auth import oauth2_scheme, credentials_exception, 
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database.crud import get_user, create_user
from database.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta 
import jwt
import bcrypt

user_router = APIRouter()

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@user_router.post("/signup/")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = hash_password(password)
    create_user(db, username=username, password=hashed_password)
    return {"message": "User created successfully"}

@user_router.post("/login/")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    stored_user = get_user(db, username=form_data.username)

    if not stored_user or not verify_password(form_data.password, stored_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    refresh_token = create_refresh_token(data={"sub": form_data.username})
    
    stored_user.access_token = access_token
    stored_user.refresh_token = refresh_token
    db.commit()  # Save the tokens in the user table
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@user_router.post("/token/refresh/")
def refresh_token_endpoint(refresh_token: str):  # changed the function name to avoid conflict with variable
    new_access_token = create_access_token(data={"sub": "test"})  # Placeholder logic
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

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])