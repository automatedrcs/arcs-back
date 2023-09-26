from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from database import models, schema, database

# ------------------------- CRUD Operations -------------------------

def create_template(db: Session, template: schema.TemplateCreate) -> models.Template:
    db_template = models.Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_templates(
    db: Session,
    template_id: Optional[UUID] = None,
    organization_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> Union[models.Template, List[models.Template]]:
    query = db.query(models.Template)

    if template_id:
        return query.filter(models.Template.id == template_id).first()

    if organization_id:
        query = query.filter(models.Template.organization_id == organization_id)
    
    return query.offset(skip).limit(limit).all()

def update_template(db: Session, template_id: UUID, template: schema.TemplateUpdate) -> Optional[models.Template]:
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template:
        for key, value in template.dict().items():
            setattr(db_template, key, value)
        db.commit()
        db.refresh(db_template)
    return db_template

def delete_template(db: Session, template_id: UUID) -> Optional[models.Template]:
    deleted = db.query(models.Template).filter(models.Template.id == template_id).delete()
    db.commit()
    if not deleted:
        return None
    return deleted

# ------------------------- FastAPI Router Endpoints -------------------------

template_router = APIRouter()

@template_router.post("/templates/", response_model=schema.Template)
def create_new_template(template: schema.TemplateCreate, db: Session = Depends(database.get_db)) -> models.Template:
    return create_template(db, template)

@template_router.get("/templates/", response_model=List[schema.Template])
def read_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    organization_id: Optional[int] = None, 
    db: Session = Depends(database.get_db)
) -> List[models.Template]:
    return get_templates(db, organization_id=organization_id, skip=skip, limit=limit)

@template_router.get("/templates/{template_id}", response_model=schema.Template)
def read_template(template_id: UUID, db: Session = Depends(database.get_db)) -> models.Template:
    db_template = get_templates(db, template_id=template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template

@template_router.put("/templates/{template_id}", response_model=schema.Template)
def update_existing_template(template_id: UUID, template: schema.TemplateUpdate, db: Session = Depends(database.get_db)) -> models.Template:
    updated_template = update_template(db, template_id, template)
    if updated_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated_template

@template_router.delete("/templates/{template_id}", response_model=schema.Template)
def delete_a_template(template_id: UUID, db: Session = Depends(database.get_db)) -> models.Template:
    db_template = delete_template(db, template_id)
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template
