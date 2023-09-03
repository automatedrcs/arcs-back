from fastapi import FastAPI
from databases import Database
from sqlalchemy import create_engine, MetaData
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import secretmanager
from .config import DATABASE_URL

database = Database(DATABASE_URL)
metadata = MetaData()

app = FastAPI()

# Add CORS middleware configuration
origins = [
    "https://arcs-front-service-ctl3t7ldeq-uc.a.run.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode('UTF-8')
