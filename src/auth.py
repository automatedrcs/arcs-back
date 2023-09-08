from fastapi_oauth2 import GoogleOAuth2
from utils import get_secret
from databases import Database

auth_router = APIRouter()

google_oauth2 = GoogleOAuth2(
    client_id=get_secret("CLIENT_ID"), 
    client_secret=get_secret("CLIENT_SECRET"),
    redirect_uri=get_secret("REDIRECT_URL")
)

@auth_router.get("/login")
async def login(request: Request):
    return google_oauth2.redirect(request)

@auth_router.get("/callback")
async def callback(code: str, request: Request):
    token = await google_oauth2.get_access_token(code, request)
    
    # Now, save the refresh token into the "person" table
    encrypted_refresh_token = encrypt(token['refresh_token'])
    query = "INSERT INTO person (data) VALUES (:data)"  # Adjust the SQL as needed
    values = {"data": {"refresh_token": encrypted_refresh_token}}
    
    # await database.execute(query=query, values=values)
    
    # Redirect user or send a response
    return {"token": token['access_token']}  # Just an example