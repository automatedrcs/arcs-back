from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from database import schema, database, models

# ------------------------- CRUD Operations -------------------------

def create_job(db: Session, job: schema.JobCreate) -> models.Job:
    db_job = models.Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs(db: Session, organization_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.Job]:
    query = db.query(models.Job)
    
    if organization_id:
        query = query.filter(models.Job.organization_id == organization_id)
    
    return query.offset(skip).limit(limit).all()

def update_job(db: Session, job_id: UUID, job: schema.JobUpdate) -> Optional[models.Job]:
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job:
        for key, value in job.dict().items():
            setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: UUID) -> Optional[models.Job]:
    db_job = db.query(models.Job).filter(models.Job.id == job_id).delete()
    if not db_job:
        return None
    db.commit()
    return db_job

# ------------------------- FastAPI Router Endpoints -------------------------

job_router = APIRouter()

@job_router.post("/jobs/", response_model=schema.Job)
def create_new_job(job: schema.JobCreate, db: Session = Depends(database.get_db)) -> models.Job:
    return crud.create_job(db, job)

@job_router.get("/jobs/", response_model=List[schema.Job])
def read_jobs(
    skip: int = Query(0, ge=0),  # Validate that skip is >= 0
    limit: int = Query(10, le=100),  # Validate that limit is <= 100 and reasonable
    organization_id: Optional[int] = None, 
    db: Session = Depends(database.get_db)
) -> List[models.Job]:
    return crud.get_jobs(db, skip=skip, limit=limit, organization_id=organization_id)

@job_router.put("/jobs/{job_id}", response_model=schema.Job)
def update_existing_job(job_id: UUID, job: schema.JobUpdate, db: Session = Depends(database.get_db)) -> models.Job:
    updated_job = crud.update_job(db, job_id, job)
    if updated_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@job_router.delete("/jobs/{job_id}", response_model=schema.Job)
def delete_a_job(job_id: UUID, db: Session = Depends(database.get_db)) -> models.Job:
    db_job = crud.delete_job(db, job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job
