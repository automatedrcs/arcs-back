# routers/user.py
# prefix "/user"

from fastapi import APIRouter, HTTPException, status, Depends, Body, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta 
import jwt
import bcrypt
from typing import Optional
from uuid import UUID
from config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import models, schema, database

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

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

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

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> models.User:
    try:
        payload = decode_token(token)
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
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, samesite="lax", secure=True)  # Assuming HTTPS

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
def refresh_token_endpoint(request: Request, response: Response, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=400, detail="Token not provided.")

    try:
        payload = decode_token(token)
        username = payload.get("sub")
        user = get_user(db, username=username)
        if not user:
            raise credentials_exception
        new_access_token = create_access_token(data={"sub": username})
        response.set_cookie(key="access_token", value=new_access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, samesite="lax", secure=True)  # Assuming HTTPS
    except jwt.JWTError:
        raise credentials_exception
    return {"message": "Token refreshed successfully"}

@user_router.get("/me")
def get_my_details(current_user: models.User = Depends(get_current_user)):
    return {
        "userUUID": str(current_user.id),
        "organizationId": str(current_user.organization_id)
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