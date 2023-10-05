#todo: import schema to clean up imports, implement async

from fastapi import APIRouter, HTTPException, status, Depends, Header, Body
from fastapi.security import OAuth2PasswordBearer
from config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database.database import get_db
from database.schema import User, UserCreate, Organization, UserLogin, UserRefreshToken
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timedelta 
import jwt
import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Utility Functions
def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    return jwt.encode(data, JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])

# CRUD Operations

def create_user(db: Session, user: UserCreate, organization_id: int):
    hashed_password = hash_password(user.password)
    db_user = User(organization_id=organization_id, username=user.username, password=hashed_password, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, organization_id: Optional[int] = None, username: Optional[str] = None, user_id: Optional[UUID] = None):
    if not any([organization_id, username, user_id]):
        raise ValueError("Must provide at least one filter criteria for get_user")
    
    query = db.query(User)
    if organization_id:
        query = query.filter(User.organization_id == organization_id)
    if username:
        query = query.filter(User.username == username)
    if user_id:
        query = query.filter(User.id == user_id)
    return query.first()


def update_user_tokens(db: Session, username: str, access_token: str, refresh_token: str):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        db_user.access_token = access_token
        db_user.refresh_token = refresh_token
        try:
            db.commit()
            db.refresh(db_user)
        except:
            db.rollback()
            raise
    return db_user

def delete_user(db: Session, user_id: UUID):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
    except jwt.JWTError:
        raise credentials_exception
    username = payload.get("sub")
    if not username:
        raise credentials_exception
    user = get_user(db, username=username)
    if not user:
        raise credentials_exception
    return user

# Router Endpoints

user_router = APIRouter()

@user_router.post("/signup")
def signup(user_data: UserCreate = Body(...), db: Session = Depends(get_db)):
    if get_user(db, username=user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    organization = db.query(Organization).filter(Organization.data["email"].astext == user_data.organization_email).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Organization not found")
    create_user(db, user_data, organization.id)
    return {"message": "User created successfully"}


@user_router.post("/login")
def login_for_access_token(form_data: UserLogin = Body(...), db: Session = Depends(get_db)):
    user = get_user(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": form_data.username})
    refresh_token = create_refresh_token(data={"sub": form_data.username})
    update_user_tokens(db, form_data.username, access_token, refresh_token)
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@user_router.post("/token/refresh")
def refresh_token_endpoint(refresh_token_data: UserRefreshToken = Body(...), db: Session = Depends(get_db)):
    refresh_token = refresh_token_data.refresh_token
    try:
        payload = decode_token(refresh_token)
        username = payload.get("sub")
        if not username:
            raise credentials_exception
        
        user = get_user(db, username=username)
        if not user or user.refresh_token != refresh_token:
            raise credentials_exception
        
        new_access_token = create_access_token(data={"sub": username})
        
        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt.JWTError:
        raise credentials_exception

@user_router.get("/me")
def get_my_details(current_user: User = Depends(get_current_user)):
    # Return user details. Modify as needed.
    return {
        "userUUID": str(current_user.id),
        "organizationId": str(current_user.organization_id)
    }