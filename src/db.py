from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    organization = relationship("Organization", back_populates="users")

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship("User", back_populates="organization")

class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    organization = relationship("Organization")
    data = Column(JSON)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
