from sqlalchemy.orm import Session
from database import models
from database import schema
from typing import Optional, Union, Optional

# Organization CRUD operations

def get_orgs(
        db: Session,
        org_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
) -> Union[Organization, List[Organization]]:
    if org_id:
        return db.query(Organization).filter(Organization.id == org_id).first()
    return db.query(Organization).offset(skip).limit(limit).all()

def create_org(db: Session, org: OrganizationCreate) -> Organization:
    db_org = Organization(**org.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def update_org(db: Session, org_id: int, org: OrganizationCreate) -> Organization:
    db_org = db.query(Organization).filter(Organization.id == org_id).first()
    if db_org:
        for key, value in org.dict().items():
            setattr(db_org, key, value)
        db.commit()
        db.refresh(db_org)
    return db_org

def delete_org(db: Session, org_id: int) -> Organization:
    db_org = db.query(Organization).filter(Organization.id == org_id).first()
    if db_org:
        db.delete(db_org)
        db.commit()
    return db_org

# User CRUD operations

def get_user(
        db: Session,
        username: Optional[str] = None,
        user_id: Optional[int] = None
) -> User:
    if username:
        return db.query(User).filter(User.username == username).first()
    if user_id:
        return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_tokens(db: Session, username: str, access_token: str, refresh_token: str) -> User:
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        db_user.access_token = access_token
        db_user.refresh_token = refresh_token
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: uuid.UUID):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

# Person CRUD operations

def create_person(db: Session, person: schema.PersonCreate):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_people(
        db: Session,
        person_id: Optional[UUID] = None,
        org_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
) -> Union[models.Person, List[models.Person]]:
    query = db.query(models.Person)

    # Apply filters based on provided parameters
    if person_id:
        return query.filter(models.Person.id == person_id).first()

    if org_id:
        query = query.filter(models.Person.organization_id == org_id)
        
    if user_id:
        query = query.filter(models.Person.user_id == user_id)

    if role:
        query = query.filter(models.Person.role == role)

    return query.offset(skip).limit(limit).all()

def update_person(db: Session, person_id: UUID, person: schema.PersonUpdate):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person:
        for key, value in person.dict().items():
            setattr(db_person, key, value)
        db.commit()
        db.refresh(db_person)
        return db_person
    return None

def delete_person(db: Session, person_id: UUID):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person:
        db.delete(db_person)
        db.commit()
        return db_person
    return None

# Availability CRUD operations

def get_availabilities(
    db: Session,
    organization_id: int,
    availability_id: Optional[UUID] = None,
    person_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> Union[models.Availability, List[models.Availability]]:
    query = db.query(models.Availability)

    # Always filter by organization
    query = query.filter(models.Availability.organization_id == organization_id)

    # Apply filters based on provided parameters
    if availability_id:
        return query.filter(models.Availability.id == availability_id).first()

    if person_id:
        query = query.filter(models.Availability.person_id == person_id)

    return query.offset(skip).limit(limit).all()


def create_availability(db: Session, availability: schema.AvailabilityCreate):
    db_availability = models.Availability(**availability.dict())
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

def update_availability(db: Session, availability_id: UUID, availability: schema.AvailabilityUpdate):
    db_availability = db.query(models.Availability).filter(models.Availability.id == availability_id).first()
    if db_availability:
        for key, value in availability.dict().items():
            setattr(db_availability, key, value)
        db.commit()
        db.refresh(db_availability)
        return db_availability
    return None

def delete_availability(db: Session, availability_id: UUID):
    db_availability = db.query(models.Availability).filter(models.Availability.id == availability_id).first()
    if db_availability:
        db.delete(db_availability)
        db.commit()
        return db_availability
    return None

# Job CRUD operations

def create_job(db: Session, job: schema.JobCreate):
    db_job = models.Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs(db: Session, organization_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Job)
    
    if organization_id:
        query = query.filter(models.Job.organization_id == organization_id)
    
    return query.offset(skip).limit(limit).all()

def update_job(db: Session, job_id: UUID, job: schema.JobUpdate):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job:
        for key, value in job.dict().items():
            setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
        return db_job
    return None

def delete_job(db: Session, job_id: UUID):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job:
        db.delete(db_job)
        db.commit()
        return db_job
    return None

# Event CRUD operations

def create_event(db: Session, event: schema.EventCreate):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_event(db: Session, event_id: UUID):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def get_events_by_organization_id(db: Session, organization_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Event).filter(models.Event.organization_id == organization_id).offset(skip).limit(limit).all()

def get_events_by_template_id(db: Session, template_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Event).filter(models.Event.template_id == template_id).offset(skip).limit(limit).all()

def update_event(db: Session, event_id: UUID, event: schema.EventUpdate):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        for key, value in event.dict().items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
        return db_event
    return None

def delete_event(db: Session, event_id: UUID):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
        return db_event
    return None

# Template CRUD operations

def create_template(db: Session, template: schema.TemplateCreate):
    db_template = models.Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_template(db: Session, template_id: UUID):
    return db.query(models.Template).filter(models.Template.id == template_id).first()

def get_templates_by_organization_id(db: Session, organization_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Template).filter(models.Template.organization_id == organization_id).offset(skip).limit(limit).all()

def update_template(db: Session, template_id: UUID, template: schema.TemplateUpdate):
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template:
        for key, value in template.dict().items():
            setattr(db_template, key, value)
        db.commit()
        db.refresh(db_template)
        return db_template
    return None

def delete_template(db: Session, template_id: UUID):
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template:
        db.delete(db_template)
        db.commit()
        return db_template
    return None

# Notification CRUD operations

def create_notification(db: Session, notification: schema.NotificationCreate):
    db_notification = models.Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notification(db: Session, notification_id: UUID):
    return db.query(models.Notification).filter(models.Notification.id == notification_id).first()

def get_notifications_by_user_id(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).offset(skip).limit(limit).all()

def get_notifications_by_organization_id(db: Session, organization_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Notification).filter(models.Notification.organization_id == organization_id).offset(skip).limit(limit).all()

def update_notification(db: Session, notification_id: UUID, notification: schema.NotificationUpdate):
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if db_notification:
        for key, value in notification.dict().items():
            setattr(db_notification, key, value)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    return None

def delete_notification(db: Session, notification_id: UUID):
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if db_notification:
        db.delete(db_notification)
        db.commit()
        return db_notification
    return None
