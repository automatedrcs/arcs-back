# This will hold the configurations for your application
from .utils import get_secret

USERNAME = get_secret("arcs-391022", "db-username")
PASSWORD = get_secret("arcs-391022", "db-password")
HOST = "arcs-391022:us-central1:arcs-sql-instance"
DBNAME = "arcs_db"

DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DBNAME}"
