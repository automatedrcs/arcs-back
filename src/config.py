# This will hold the configurations for your application
from utils import get_secret

USERNAME = get_secret("DB_USERNAME")
PASSWORD = get_secret("DB_PASSWORD")
HOST = "10.223.0.8"
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