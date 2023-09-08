# This will hold the configurations for your application
from .utils import get_secret

USERNAME = get_secret("arcs-db-username")
PASSWORD = get_secret("arcs-db-password")
HOST = "10.223.0.8"
DBNAME = "arcs-db"
PORT = 5432

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"