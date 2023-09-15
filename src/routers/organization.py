from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import OrganizationCreate, Organization

organization_router = APIRouter()

# CRUD Functions
def get_organization_by_id(db: Session, organization_id: int) -> Organization:
    return db.query(Organization).filter(Organization.id == organization_id).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 10) -> list[Organization]:
    return db.query(Organization).offset(skip).limit(limit).all()

def create_organization(db: Session, org: OrganizationCreate) -> Organization:
    db_org = Organization(**org.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def update_organization(db: Session, organization_id: int, org: OrganizationCreate) -> Organization:
    db_org = db.query(Organization).filter(Organization.id == organization_id).first()
    if db_org:
        for key, value in org.dict().items():
            setattr(db_org, key, value)
        db.commit()
        db.refresh(db_org)
    return db_org

def delete_organization(db: Session, organization_id: int) -> Organization:
    db_org = db.query(Organization).filter(Organization.id == organization_id).first()
    if db_org:
        db.delete(db_org)
        db.commit()
    return db_org

# Router Endpoints
@organization_router.post("/", response_model=Organization)
def create_new_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    return create_organization(db, org)

@organization_router.get("/", response_model=list[Organization])
def read_organizations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_organizations(db, skip=skip, limit=limit)

@organization_router.get("/{organization_id}", response_model=Organization)
def read_organization(organization_id: int, db: Session = Depends(get_db)):
    db_organization = get_organization_by_id(db, organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization

@organization_router.put("/{organization_id}", response_model=Organization)
def update_existing_organization(organization_id: int, org: OrganizationCreate, db: Session = Depends(get_db)):
    updated_organization = update_organization(db, organization_id, org)
    if updated_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return updated_organization

@organization_router.delete("/{organization_id}", response_model=Organization)
def delete_an_organization(organization_id: int, db: Session = Depends(get_db)):
    db_organization = delete_organization(db, organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization
