from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import OrganizationCreate, Organization, OrganizationUpdate
from database.models import Organization as OrganizationModel

# CRUD Functions

def create_organization(db: Session, org: OrganizationCreate) -> Organization:
    db_org = OrganizationModel(**org.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return Organization.from_orm(db_org)

def get_organizations(db: Session, organization_id: Optional[int] = None, skip: int = 0, limit: int = 10) -> Union[Organization, List[Organization]]:
    query = db.query(OrganizationModel)

    if organization_id:
        db_org = query.filter(OrganizationModel.id == organization_id).first()
        if db_org:
            return Organization.from_orm(db_org)
        return None

    return [Organization.from_orm(org) for org in query.offset(skip).limit(limit).all()]

def update_organization(db: Session, organization_id: int, org: OrganizationCreate) -> Organization:
    db_org = db.query(OrganizationModel).filter(OrganizationModel.id == organization_id).first()
    if db_org:
        for key, value in org.dict().items():
            setattr(db_org, key, value)
        db.commit()
        db.refresh(db_org)
        return Organization.from_orm(db_org)
    return None

def delete_organization(db: Session, organization_id: int) -> Organization:
    db_org = db.query(OrganizationModel).filter(OrganizationModel.id == organization_id).first()
    if db_org:
        db.delete(db_org)
        db.commit()
        return Organization.from_orm(db_org)
    return None

# Router Endpoints

organization_router = APIRouter()

@organization_router.post("", response_model=Organization)
def create_new_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    return create_organization(db, org)

@organization_router.get("", response_model=List[Organization])
def read_all_organizations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_organizations(db, skip=skip, limit=limit)

@organization_router.get("/{organization_id}", response_model=Organization)
def read_organization(organization_id: int, db: Session = Depends(get_db)):
    db_organization = get_organizations(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization

@organization_router.put("/{organization_id}", response_model=Organization)
def update_existing_organization(organization_id: int, org: OrganizationUpdate, db: Session = Depends(get_db)):
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
