from utils import get_secret
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging

# Logging configuration
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

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
    "http://localhost:5173"
]

# Constants for JWT
FERNET_KEY = get_secret("FERNET_KEY")
JWT_SECRET_KEY = get_secret("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Setting up OAuth2.0
BASE_URL = get_secret("BASE_URL")
CLIENT_ID = get_secret('CLIENT_ID')
CLIENT_SECRET = get_secret('CLIENT_SECRET')
FRONT_URL = get_secret('FRONT_URL')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Session Middleware
SESSION_MIDDLEWARE_KEY = get_secret("SESSION_MIDDLEWARE_KEY")
