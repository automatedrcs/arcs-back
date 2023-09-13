from sqlalchemy.orm import Session
from database import models
from database import schema

# User CRUD operations
def create_user(db: Session, user: schema.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: uuid.UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: uuid.UUID, user: schema.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def delete_user(db: Session, user_id: uuid.UUID):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

# Organization CRUD operations

def create_organization(db: Session, organization: schema.OrganizationCreate):
    db_organization = models.Organization(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization

def get_organization(db: Session, organization_id: int):
    return db.query(models.Organization).filter(models.Organization.id == organization_id).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization).offset(skip).limit(limit).all()

def update_organization(db: Session, organization_id: int, organization: schema.OrganizationUpdate):
    db_organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if db_organization:
        for key, value in organization.dict().items():
            setattr(db_organization, key, value)
        db.commit()
        db.refresh(db_organization)
        return db_organization
    return None

def delete_organization(db: Session, organization_id: int):
    db_organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if db_organization:
        db.delete(db_organization)
        db.commit()
        return db_organization
    return None

# Person CRUD operations

def create_person(db: Session, person: schema.PersonCreate):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_person(db: Session, person_id: UUID):
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def get_people_by_user_id(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Person).filter(models.Person.user_id == user_id).offset(skip).limit(limit).all()

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

def create_availability(db: Session, availability: schema.AvailabilityCreate):
    db_availability = models.Availability(**availability.dict())
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

def get_availability(db: Session, availability_id: UUID):
    return db.query(models.Availability).filter(models.Availability.id == availability_id).first()

def get_availabilities_by_person_id(db: Session, person_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Availability).filter(models.Availability.person_id == person_id).offset(skip).limit(limit).all()

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

def get_job(db: Session, job_id: UUID):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def get_jobs_by_organization_id(db: Session, organization_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Job).filter(models.Job.organization_id == organization_id).offset(skip).limit(limit).all()

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
