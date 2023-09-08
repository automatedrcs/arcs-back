from fastapi import APIRouter, Depends, HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from .utils import get_secret

# Initialize the router
auth_router = APIRouter()

# Setting up OAuth2.0
oauth = OAuth()
oauth.register(
    name='google',
    client_id=get_secret("CLIENT_ID"),
    client_secret=get_secret("CLIENT_SECRET"),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=get_secret("REDIRECT_URL"),  # Your redirect URL
    client_kwargs={'scope': 'openid profile email'},
)

@auth_router.get('/login')
async def login(request: Request):
    redirect_uri = url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@auth_router.get('/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    
    # Now, save the refresh token into the "person" table
    encrypted_refresh_token = encrypt(token['refresh_token'])
    query = "INSERT INTO person (data) VALUES (:data)"  # Adjust the SQL as needed
    values = {"data": {"refresh_token": encrypted_refresh_token}}
    
    # await database.execute(query=query, values=values)  # Uncomment when ready to save to DB
    
    # Redirect user or send a response
    return {"token": token['access_token'], "user": user}
