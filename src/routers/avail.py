from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import AvailabilityCreate, Availability
from database.crud import get_availabilities, create_availability, update_availability, delete_availability

avail_router = APIRouter()

@avail_router.post("/", response_model=Availability)
def create_new_availability(availability: AvailabilityCreate, db: Session = Depends(get_db)):
    return create_availability(db, availability)

@avail_router.get("/", response_model=List[Availability])
def read_availabilities(
    organization_id: int,
    skip: int = 0, 
    limit: int = 10, 
    person_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Get a list of availabilities. Can be paginated with skip and limit and filtered by person_id."""
    availabilities = get_availabilities(db, organization_id, skip=skip, limit=limit, person_id=person_id)
    return availabilities

@avail_router.get("/{availability_id}", response_model=Availability)
def read_availability(availability_id: UUID, organization_id: int, db: Session = Depends(get_db)):
    """Get a specific availability by its ID."""
    db_availability = get_availabilities(db, organization_id, availability_id)
    if db_availability is None:
        raise HTTPException(status_code=404, detail="Availability not found")
    return db_availability

@avail_router.put("/{availability_id}", response_model=Availability)
def update_existing_availability(availability_id: int, availability: AvailabilityCreate, db: Session = Depends(get_db)):
    updated_availability = update_availability(db, availability_id, availability)
    if updated_availability is None:
        raise HTTPException(status_code=404, detail="Availability not found")
    return updated_availability

@avail_router.delete("/{availability_id}", response_model=Availability)
def delete_an_availability(availability_id: int, db: Session = Depends(get_db)):
    db_availability = delete_availability(db, availability_id)
    if db_availability is None:
        raise HTTPException(status_code=404, detail="Availability not found")
    return db_availability
