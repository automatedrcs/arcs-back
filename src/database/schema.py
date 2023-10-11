# database/schema.py
# Pydantic Schemas

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class OrganizationBase(BaseModel):
    name: str
    data: Dict[str, Any]

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: Optional[int]

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str
    name: Optional[str]

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    organization_email: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRefreshToken(BaseModel):
    refresh_token: str

class UserUpdate(UserBase):
    password: Optional[str]

class User(UserBase):
    id: UUID
    last_login: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    organization_id: int
    user_id: UUID
    type: str
    data: dict

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PersonBase(BaseModel):
    email: str
    name: str
    role: str
    data: dict

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

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

class AvailabilityUpdate(AvailabilityBase):
    pass

class Availability(AvailabilityBase):
    id: UUID

    class Config:
        orm_mode = True

class JobBase(BaseModel):
    organization_id: int
    data: dict

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    pass

class Job(JobBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TemplateBase(BaseModel):
    organization_id: int
    template_name: str
    data: dict

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(TemplateBase):
    pass

class Template(TemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class MeetingBase(BaseModel):
    organization_id: int
    template_id: UUID
    completed: bool
    data: dict

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(MeetingBase):
    pass

class Meeting(MeetingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
