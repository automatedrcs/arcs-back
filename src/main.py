from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ORIGINS

from routers.auth import auth_router
from routers.user import user_router
from routers.org import org_router
from routers.person import person_router
from routers.avail import avail_router
from routers.job import job_router
from routers.event import event_router
from routers.template import template_router
from routers.notif import notif_router

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
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(org_router, prefix="/org", tags=["Organization"])
app.include_router(person_router, prefix="/person", tags=["Person"])
app.include_router(avail_router, prefix="/avail", tags=["Availability"])
app.include_router(job_router, prefix="/job", tags=["Job"])
app.include_router(event_router, prefix="/event", tags=["Event"])
app.include_router(template_router, prefix="/template", tags=["Template"])
app.include_router(notif_router, prefix="/notif", tags=["Notification"])