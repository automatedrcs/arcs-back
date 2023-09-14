# Job router
#
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import JobCreate, Job
from database.crud import get_jobs, create_job, get_job_by_id, update_job, delete_job

job_router = APIRouter()

@job_router.post("/", response_model=Job)
def create_new_job(job: JobCreate, db: Session = Depends(get_db)):
    return create_job(db, job)

@job_router.get("/", response_model=List[Job])
def read_jobs(skip: int = 0, limit: int = 10, organization_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get a list of jobs. Can be paginated with skip and limit or filtered by organization_id."""
    jobs = get_jobs(db, skip=skip, limit=limit, organization_id=organization_id)
    return jobs

@job_router.put("/{job_id}", response_model=Job)
def update_existing_job(job_id: int, job: JobCreate, db: Session = Depends(get_db)):
    updated_job = update_job(db, job_id, job)
    if updated_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@job_router.delete("/{job_id}", response_model=Job)
def delete_a_job(job_id: int, db: Session = Depends(get_db)):
    db_job = delete_job(db, job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job