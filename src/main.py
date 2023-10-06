from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ORIGINS
from routers.authentication import authentication_router
from routers.organization import organization_router
from routers.user import user_router
from routers.notification import notification_router
from routers.person import person_router
from routers.availability import availability_router
from routers.job import job_router
from routers.template import template_router
from routers.meeting import meeting_router
from routers.test import test_router
from routers.scheduler import scheduler_router
from routers.calendar import calendar_router

app = FastAPI()

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(authentication_router, prefix="/authentication", tags=["Authentication"])
app.include_router(organization_router, prefix="/organization", tags=["Organization"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(notification_router, prefix="/notification", tags=["Notification"])
app.include_router(person_router, prefix="/person", tags=["Person"])
app.include_router(availability_router, prefix="/availability", tags=["Availability"])
app.include_router(job_router, prefix="/job", tags=["Job"])
app.include_router(template_router, prefix="/template", tags=["Template"])
app.include_router(meeting_router, prefix="/meeting", tags=["Meeting"])
app.include_router(test_router, prefix="/test", tags=["Test"])
app.include_router(scheduler_router, prefix="/scheduler", tags=["Automation", "Scheduler"])
app.include_router(calendar_router, prefix="/calendar", tags=["Calendar"])