# This will hold the configurations for your application
from utils import get_secret
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth

USERNAME = get_secret("DB_USERNAME")
PASSWORD = get_secret("DB_PASSWORD")
HOST = "localhost"
DBNAME = "arcs-db"
PORT = 5432

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

# CORS origins
ORIGINS = [
    "https://arcs-front-service-ctl3t7ldeq-uc.a.run.app",
]

# Constants for JWT
FERNET_KEY = get_secret("FERNET_KEY")
JWT_SECRET_KEY = get_secret("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

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