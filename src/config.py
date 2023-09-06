# This will hold the configurations for your application
from .utils import get_secret

USERNAME = get_secret("arcs-391022", "arcs-db-username")
PASSWORD = get_secret("arcs-391022", "arcs-db-password")
HOST = "34.171.204.136"
DBNAME = "arcs-db"
PORT = 5432

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"