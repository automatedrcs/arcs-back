from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from database.database import Base
from cryptography.fernet import Fernet
from sqlalchemy.ext.hybrid import hybrid_property
from config import SECRET_KEY

class Organization(Base):
    __tablename__ = "organization"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    data = Column(JSONB)

    users = relationship("User", back_populates="organization")
    people = relationship("Person", back_populates="organization")
    jobs = relationship("Job", back_populates="organization")
    templates = relationship("Template", back_populates="organization")
    events = relationship("Event", back_populates="organization")


class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship("Organization", back_populates="users")

    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String, nullable=True)
    permission = Column(String, default="user")
    _access_token = Column("access_token", String, nullable=True)  # Raw encrypted token
    _refresh_token = Column("refresh_token", String, nullable=True)  # Raw encrypted token
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    people = relationship("Person", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    @hybrid_property
    def access_token(self):
        return cipher_suite.decrypt(self._access_token.encode()).decode() if self._access_token else None

    @access_token.setter
    def access_token(self, value):
        self._access_token = cipher_suite.encrypt(value.encode()).decode()

    @hybrid_property
    def refresh_token(self):
        return cipher_suite.decrypt(self._refresh_token.encode()).decode() if self._refresh_token else None

    @refresh_token.setter
    def refresh_token(self, value):
        self._refresh_token = cipher_suite.encrypt(value.encode()).decode()


class Notification(Base):
    __tablename__ = "notification"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship("User", back_populates="notifications")

    type = Column(String)
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Person(Base):
    __tablename__ = "person"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    organization = relationship("Organization")
    user = relationship("User", back_populates="people")

    email = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(String)
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    availabilities = relationship("Availability", back_populates="person")


class Availability(Base):
    __tablename__ = "availability"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    person_id = Column(UUID(as_uuid=True), ForeignKey('person.id'))
    person = relationship("Person", back_populates="availabilities")

    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = "job"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    data = Column(JSONB)

    templates = relationship("Template", back_populates="job")


class Template(Base):
    __tablename__ = "template"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    job_id = Column(UUID(as_uuid=True), ForeignKey('job.id'), nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('template.id'), nullable=True)

    template_name = Column(String)
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    events = relationship("Event", back_populates="template")


class Event(Base):
    __tablename__ = "event"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    template_id = Column(UUID(as_uuid=True), ForeignKey('template.id'))
    template = relationship("Template", back_populates="events")

    completed = Column(Boolean, default=False)
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
