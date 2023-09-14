from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import OrganizationCreate, Organization
from database.crud import get_orgs, create_org, update_org, delete_org

org_router = APIRouter()

@org_router.post("/", response_model=Organization)
def create_new_org(org: OrganizationCreate, db: Session = Depends(get_db)):
    return create_org(db, org)

@org_router.get("/", response_model=list[Organization])
def read_orgs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get a list of orgs. Can be paginated with skip and limit."""
    orgs = get_orgs(db, skip=skip, limit=limit)
    return orgs

@org_router.get("/{org_id}", response_model=Organization)
def read_org(org_id: int, db: Session = Depends(get_db)):
    """Get a specific org by its ID."""
    db_org = get_orgs(db, org_id=org_id)
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_org

@org_router.put("/{org_id}", response_model=Organization)
def update_existing_org(org_id: int, org: OrganizationCreate, db: Session = Depends(get_db)):
    updated_org = update_org(db, org_id, org)
    if updated_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return updated_org

@org_router.delete("/{org_id}", response_model=Organization)
def delete_an_org(org_id: int, db: Session = Depends(get_db)):
    db_org = delete_org(db, org_id)
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_org
