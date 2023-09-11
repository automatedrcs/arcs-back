from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
import jwt
import bcrypt
from .auth import oauth2_scheme, credentials_exception
from .utils import get_secret, encrypt, decrypt

SECRET_KEY = get_secret("SESSION_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

user_router = APIRouter()

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    return token_data
@user_router.post("/signup/")
async def signup(username: str, password: str):
    hashed_password = hash_password(password)
    # Store username and hashed_password in the database.
    # await database.store_user(username, hashed_password)
    return {"message": "User created successfully"}

@user_router.post("/login/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Retrieve the user from the database
    # stored_user = await database.get_user(form_data.username)
    stored_user = None  # This is a placeholder, remove once you integrate a real database

    if not stored_user or not verify_password(form_data.password, stored_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    refresh_token = create_refresh_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@user_router.post("/token/refresh/")
def refresh_token(refresh_token: str):
    new_access_token = create_access_token(data={"sub": "test"})  # Replace 'test' with your logic

    return {"access_token": new_access_token, "token_type": "bearer"}
