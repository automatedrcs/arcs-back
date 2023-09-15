# Desc: Pydantic schemas for database models
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    username: str
    name: Optional[str]
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID
    last_login: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int

    class Config:
        orm_mode = True

class PersonBase(BaseModel):
    email: str
    name: str

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    email: Optional[str]
    name: Optional[str]

class Person(PersonBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AvailabilityBase(BaseModel):
    start_time: datetime
    end_time: datetime

class AvailabilityCreate(AvailabilityBase):
    pass

class Availability(AvailabilityBase):
    id: UUID

    class Config:
        orm_mode = True

class JobBase(BaseModel):
    organization_id: int

class Job(JobBase):
    id: UUID

    class Config:
        orm_mode = True

class EventBase(BaseModel):
    organization_id: int
    template_id: UUID

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TemplateBase(BaseModel):
    organization_id: int
    template_name: str

class TemplateCreate(TemplateBase):
    pass

class Template(TemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    organization_id: int
    user_id: UUID

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
