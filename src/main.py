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
    print("connecting to database")
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def read_root():
    return {"Hello": "World"}