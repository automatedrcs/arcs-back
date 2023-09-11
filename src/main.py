from fastapi import FastAPI
from databases import Database
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import secretmanager
from .config import DATABASE_URL
from src.routers.auth import auth_router
from src.routers.user import user_router
from .db import get_db

database = Database(DATABASE_URL)

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

@app.get("/api/data")
def get_sample_data():
    sample_data = {"message": "This is a sample data response."}
    return sample_data

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/user", tags=["User"])