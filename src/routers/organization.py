from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import crud, models, schema
from database.database import get_db

organization_router = APIRouter()

@organization_router.post("/organizations/", response_model=schema.Organization)
def create_organization(organization: schema.OrganizationCreate, db: Session = Depends(get_db)):
    return crud.create_organization(db, organization)

@organization_router.get("/organizations/{organization_id}", response_model=schema.Organization)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    db_organization = crud.get_organization(db, organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization

@organization_router.put("/organizations/{organization_id}", response_model=schema.Organization)
def update_organization(organization_id: int, organization: schema.OrganizationCreate, db: Session = Depends(get_db)):
    return crud.update_organization(db, organization_id, organization)

@organization_router.delete("/organizations/{organization_id}", response_model=schema.Organization)
def delete_organization(organization_id: int, db: Session = Depends(get_db)):
    db_organization = crud.get_organization(db, organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    crud.delete_organization(db, organization_id)
    return db_organization
