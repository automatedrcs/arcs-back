from fastapi import FastAPI
from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "postgresql://your_username:your_password@your_host/your_dbname"

database = Database(DATABASE_URL)
metadata = MetaData()

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def read_root():
    return {"Hello": "World"}