# Template router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.schema import TemplateCreate, Template
from database.crud import get_templates, create_template, get_template_by_id, update_template, delete_template

template_router = APIRouter()

@template_router.post("/", response_model=Template)
def create_new_template(template: TemplateCreate, db: Session = Depends(get_db)):
    return create_template(db, template)

@template_router.get("/", response_model=list[Template])
def read_templates(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get a list of templates. Can be paginated with skip and limit."""
    templates = get_templates(db, skip=skip, limit=limit)
    return templates

@template_router.get("/{template_id}", response_model=Template)
def read_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific template by its ID."""
    db_template = get_template_by_id(db, template_id)
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template

@template_router.put("/{template_id}", response_model=Template)
def update_existing_template(template_id: int, template: TemplateCreate, db: Session = Depends(get_db)):
    updated_template = update_template(db, template_id, template)
    if updated_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated_template

@template_router.delete("/{template_id}", response_model=Template)
def delete_a_template(template_id: int, db: Session = Depends(get_db)):
    db_template = delete_template(db, template_id)
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template