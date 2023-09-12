from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from .config import Base

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship("Organization", back_populates="users")
    people = relationship("Person", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    data = Column(JSONB)
    users = relationship("User", back_populates="organization")
    
class Person(Base):
    __tablename__ = "person"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    organization = relationship("Organization")
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship("User", back_populates="people")
    availability = relationship("Availability", back_populates="person")
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Availability(Base):
    __tablename__ = "availability"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey('person.id'))
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), server_default=func.now())
    person = relationship("Person", back_populates="availability")

class Job(Base):
    __tablename__ = "job"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    data = Column(JSONB)

class Event(Base):
    __tablename__ = "event"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    template_id = Column(UUID(as_uuid=True), ForeignKey('template.id'))
    template = relationship("Template", back_populates="events")
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Template(Base):
    __tablename__="template"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    template_name = Column(String)
    events = relationship("Event", back_populates="template")
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Notification(Base):
    __tablename__="notification"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship("User", back_populates="notifications")
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

