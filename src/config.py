# config.py
# This will hold the configurations for your application
from utils import get_secret
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth

# Database constants
DB_USERNAME = get_secret("DB_USERNAME")
DB_PASSWORD = get_secret("DB_PASSWORD")
CLOUD_SQL_CONNECTION_NAME = get_secret("CLOUD_SQL_CONNECTION_NAME")
DB_NAME = get_secret("DB_NAME")
PORT = 5432

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@/{DB_NAME}?host=/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"

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

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
oauth = OAuth()

google = oauth.register(
    name="google",
    server_metadata_url=GOOGLE_DISCOVERY_URL,
    client_kwargs={
        'scope': 'https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email',
        'access_type': 'offline',
        'prompt': 'consent'
    },
    client_id=get_secret("CLIENT_ID"),
    client_secret=get_secret("CLIENT_SECRET"),
    redirect_uri=get_secret("REDIRECT_URL"),
)


# Session Middleware
SESSION_MIDDLEWARE_KEY = get_secret("SESSION_MIDDLEWARE_KEY")