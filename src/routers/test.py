from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import models, database

test_router = APIRouter()

@test_router.get("/api/data")
def get_data():
    return {
        "message": "Data fetched successfully",
        "data": {
            "example_key": "example_value"
        }
    }

@test_router.get("/api/connection-test")
async def test_connection(db: AsyncSession = Depends(database.get_db)):
    try:
        # Attempt to fetch the first row from the Organization table
        result = await db.execute(select(models.Organization).order_by(models.Organization.id).limit(1))
        organization = result.scalars().first()
        if organization:
            return {
                "message": "Connection successful. Data fetched successfully.",
                "data": {
                    "organization_name": organization.name,
                    "organization_data": organization.data
                }
            }
        # If there is no data in the table
        return {"message": "Connection successful. No data found in the table.", "data": {}}
    except Exception as e:
        # If there's an error related to database connection or query execution
        raise HTTPException(status_code=500, detail=str(e))
