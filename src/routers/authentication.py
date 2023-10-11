from fastapi import APIRouter, Depends, HTTPException, Request, responses
from sqlalchemy.orm import Session
from database import database, schema, models
from utils import get_secret, encrypt
from config import oauth

# ------------------------- CRUD Operations -------------------------

def update_data_by_email(db: Session, email: str, data: dict, model: any) -> any:
    try:
        instance = db.query(model).filter(model.email == email).first()
        if not instance:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")

        for key, value in data.items():
            setattr(instance, key, value)

        db.commit()
        db.refresh(instance)
        return instance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def handle_oauth_data(db: Session, user: dict, token: dict, model: any):
    try:
        google_data = {
            "refresh_token": encrypt(token.get('refresh_token', ''))
        }

        instance = db.query(model).filter(model.email == user["email"]).first()
        if not instance:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")

        if instance.data is None:
            instance.data = {}
        if "authentication" not in instance.data:
            instance.data["authentication"] = {}
        instance.data["authentication"]["google"] = google_data

        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------- FastAPI Router Endpoints -------------------------

authentication_router = APIRouter()

@authentication_router.get('/google/login/user')
async def user_login(request: Request):
    try:
        BASE_URL = get_secret("BASE_URL")
        redirect_uri = f"{BASE_URL}/authentication/google/callback/user"
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@authentication_router.get('/google/login/person')
async def person_login(request: Request):
    try:
        BASE_URL = get_secret("BASE_URL")
        redirect_uri = f"{BASE_URL}/authentication/google/callback/person"
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@authentication_router.get('/google/callback/user', name="user_auth")
async def user_auth(request: Request, db: Session = Depends(database.get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        if 'id_token' not in token:
            raise HTTPException(status_code=400, detail="Missing id_token")
        
        user_info = oauth.google.parse_id_token(request, token)
        handle_oauth_data(db, user_info, token, models.User)

        # Redirect to success page
        return responses.RedirectResponse(url='/authentication/success')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@authentication_router.get('/google/callback/person', name="person_auth")
async def person_auth(request: Request, db: Session = Depends(database.get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        if 'id_token' not in token:
            raise HTTPException(status_code=400, detail="Missing id_token")
        
        user_info = oauth.google.parse_id_token(request, token)
        handle_oauth_data(db, user_info, token, models.Person)

        # Redirect to success page
        return responses.RedirectResponse(url='/authentication/success')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@authentication_router.get('/success')
async def success():
    FRONT_URL = get_secret("FRONT_URL")
    
    content = f"""
    <html>
        <head>
            <title>Authentication Successful</title>
            <script>
                setTimeout(function(){{
                    window.location.href = "{FRONT_URL}";
                }}, 2000);  // Redirects after 2 seconds
            </script>
        </head>
        <body>
            <h2>Authentication Successful! Redirecting...</h2>
        </body>
    </html>
    """
    return responses.HTMLResponse(content=content)