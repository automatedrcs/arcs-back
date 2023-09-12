from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import DATABASE_URL
from routers.auth import auth_router
from routers.user import user_router
from database.database import get_db, SessionLocal, engine
import database.models

# Create tables if they don't exist
database.models.Base.metadata.create_all(bind=engine)

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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/data")
def get_sample_data():
    sample_data = {"message": "This is a sample data response."}
    return sample_data

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(user_router, prefix="/organization", tags=["Organization"])
