# routers/user.py
# prefix "/user"

from fastapi import APIRouter, HTTPException, status, Depends, Body, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta 
import jwt
import bcrypt
from typing import Optional, List
from uuid import UUID
from config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import models, schema, database
import logging
from utils import encrypt, decrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Utility Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    return jwt.encode(data, JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])

# CRUD Operations
def create_user(db: Session, user: schema.UserCreate, organization_id: int) -> models.User:
    hashed_password = hash_password(user.password)
    db_user = models.User(organization_id=organization_id, username=user.username, password=hashed_password, email=user.email) # Use hashed password directly
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, organization_id: Optional[int] = None, username: Optional[str] = None, user_id: Optional[UUID] = None) -> Optional[models.User]:
    if not any([organization_id, username, user_id]):
        raise ValueError("Must provide at least one filter criteria for get_user")
    
    query = db.query(models.User)
    
    if user_id:
        return query.filter(models.User.id == user_id).first()

    if organization_id:
        query = query.filter(models.User.organization_id == organization_id)

    if username:
        user_by_username = query.filter(models.User.username == username).first()
        if user_by_username:
            return user_by_username
        # If user is not found by username, check for email
        return query.filter(models.User.email == username).first()
        
    return query.first()

def update_user_tokens(db: Session, username: str, access_token: str, refresh_token: str) -> models.User:
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        logging.info(f"Attempted login with username: {username}, but user was not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.access_token = access_token  # Model will handle encryption
    db_user.refresh_token = refresh_token  # Model will handle encryption

    try:
        db.commit()
        db.refresh(db_user)
    except:
        db.rollback()
        raise

    return db_user

def delete_user(db: Session, user_id: UUID) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

def get_current_user(request: Request, db: Session = Depends(database.get_db)) -> models.User:
    encrypted_token = request.cookies.get("access_token")
    decrypted_token = decrypt(encrypted_token)   # Decrypt token after retrieving from client
    if not decrypted_token:
        raise credentials_exception
    try:
        payload = decode_token(decrypted_token)  # Use decrypted_token here
        username = payload.get("sub")
        if not username:
            raise credentials_exception
        user = get_user(db, username=username)
        if not user:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    return user

# Router Endpoints
user_router = APIRouter()

@user_router.post("/signup")
def signup(user_data: schema.UserCreate = Body(...), db: Session = Depends(database.get_db)):
    if get_user(db, username=user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    organization = db.query(models.Organization).filter(models.Organization.data["email"].astext == user_data.organization_email).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Organization not found")
    create_user(db, user_data, organization.id)
    return {"message": "User created successfully"}

@user_router.post("/login")
def login_for_access_token(response: Response, form_data: schema.UserLogin = Body(...), db: Session = Depends(database.get_db)):
    user = get_user(db, username=form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    encrypted_access_token = encrypt(access_token)
    refresh_token = create_refresh_token(data={"sub": form_data.username})
    encrypted_refresh_token = encrypt(refresh_token)  # Encrypting the refresh token as well
    
    response.set_cookie(key="refresh_token", value=encrypted_refresh_token, httponly=True, max_age=30*24*60*60) # 30 days
    response.set_cookie(key="access_token", value=encrypted_access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60)
    return {
        "message": "Logged in successfully",
        "userUUID": str(user.id),
        "organizationId": user.organization_id
    }

@user_router.post("/token")
def login_for_token(form_data: schema.UserLogin = Body(...), db: Session = Depends(database.get_db)):
    user = get_user(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.post("/token/refresh")
def refresh_token_endpoint(request: Request, db: Session = Depends(database.get_db)):
    encrypted_refresh_token_data = request.cookies.get("refresh_token")
    if not encrypted_refresh_token_data:
        raise HTTPException(status_code=400, detail="Refresh token not provided.")

    refresh_token_data = decrypt(encrypted_refresh_token_data)  # Decrypting the token

    try:
        payload = decode_token(refresh_token_data)
        username = payload.get("sub")
        if not username:
            raise credentials_exception
        user = get_user(db, username=username)
        if not user or user.refresh_token != refresh_token_data:  # Checking against decrypted refresh token
            raise credentials_exception
        
        new_access_token = create_access_token(data={"sub": username})
    except jwt.JWTError:
        raise credentials_exception
    return {"access_token": new_access_token, "token_type": "bearer"}

@user_router.get("/me")
def get_my_details(current_user: models.User = Depends(get_current_user)):
    return {
        "userUUID": str(current_user.id),
        "organizationId": str(current_user.organization_id)
    }

@user_router.get("/google-access-token")
def get_google_access_token(current_user: models.User = Depends(get_current_user)):
    """
    Retrieve the Google access token for the current authenticated user.
    """
    # Check if the data field is None or if the googleAccessToken does not exist
    if not current_user.data or "googleAccessToken" not in current_user.data:
        raise HTTPException(status_code=404, detail="Google access token not found")

    google_access_token_encrypted = current_user.data.get("googleAccessToken")
    google_access_token = decrypt(google_access_token_encrypted)
    
    # In reality, Google access tokens often expire after 1 hour. 
    # Depending on your setup, you might want to check the token's validity or expiration.
    # Here we're simply suggesting a potential action on the client-side.
    expiration_message = {
        "message": "Google access token might be expired. Please consider reconnecting your Google account on the client-side."
    }
    
    return {
        "googleAccessToken": google_access_token,
        "warning": expiration_message
    }

@user_router.delete("/user/{user_id}")
def delete_user_endpoint(user_id: UUID, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Delete a user based on their user_id. Only an authenticated user can delete their own account.
    """
    # Ensure the current user is the one trying to delete their own account or add authorization logic here
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Operation not allowed")

    deleted_user = delete_user(db, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}