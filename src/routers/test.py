from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
def test_connection(db: Session = Depends(database.get_db)):
    try:
        # Attempt to fetch the first row from the Organization table
        result = db.query(models.Organization).order_by(models.Organization.id).first()
        
        if result:
            return {
                "message": "Connection successful. Data fetched successfully.",
                "data": {
                    "organization_name": result.name,
                    "organization_data": result.data
                }
            }
        # If there is no data in the table
        return {"message": "Connection successful. No data found in the table.", "data": {}}
    except Exception as e:
        # If there's an error related to database connection or query execution
        raise HTTPException(status_code=500, detail=str(e))
