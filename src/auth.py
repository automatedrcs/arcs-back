
from fastapi_oauth2 import GoogleOAuth2
from databases import Database

google_oauth2 = GoogleOAuth2(
    client_id="YOUR_GOOGLE_CLIENT_ID", 
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    redirect_uri="YOUR_CALLBACK_URL"
)

@app.get("/login")
async def login(request: Request):
    return google_oauth2.redirect(request)

@app.get("/callback")
async def callback(code: str, request: Request):
    token = await google_oauth2.get_access_token(code, request)
    
    # Now, save the refresh token into the "person" table
    encrypted_refresh_token = encrypt(token['refresh_token'])
    query = "INSERT INTO person (data) VALUES (:data)"  # Adjust the SQL as needed
    values = {"data": {"refresh_token": encrypted_refresh_token}}
    
    # await database.execute(query=query, values=values)
    
    # Redirect user or send a response
    return {"token": token['access_token']}  # Just an example

export auth_router