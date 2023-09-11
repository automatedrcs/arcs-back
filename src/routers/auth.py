from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from ..utils import get_secret, encrypt
from fastapi import FastAPI
from datetime import datetime, timedelta

# Initialize the router
auth_router = APIRouter()

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


@auth_router.get('/google/login')
async def login(request: Request):
    redirect_uri = url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@auth_router.get('/google/callback')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    
    # Now, save the refresh token into the "person" table
    encrypted_refresh_token = encrypt(token['refresh_token'])
    query = "INSERT INTO person (data) VALUES (:data)"
    values = {"data": {"refresh_token": encrypted_refresh_token}}
    
    # await database.execute(query=query, values=values)  # Uncomment when ready to save to DB
    
    return {"token": token['access_token'], "user": user}
