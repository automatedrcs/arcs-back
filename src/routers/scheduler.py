from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from scripts.generate_interview import generate_interview
from scripts.schedule_interview import schedule_interview

scheduler_router = FastAPI()

class GenerateInterviewInput(BaseModel):
    job_id: int
    style_id: int
    candidate_id: int
    organization_id: int

class ScheduleInterviewInput(BaseModel):
    # Define fields based on the structure of your interview object
    job_id: int
    # ... other fields

@scheduler_router.post("/generate_interview")
async def generate_interview(
    data: GenerateInterviewInput
):
    try:
        interview = await generate_interview(data.job_id, data.style_id, data.candidate_id, data.organization_id)
        return {"status": "success", "interview": interview}
    except Exception as error:
        raise HTTPException(status_code=400, detail={"status": "failure", "error": str(error)})

@scheduler_router.post("/schedule_interview")
async def schedule_interview_endpoint(
    interview: ScheduleInterviewInput
):
    try:
        scheduled_interview = await schedule_interview(interview)
        return {"status": "success", "interview": scheduled_interview}
    except Exception as error:
        raise HTTPException(status_code=400, detail={"status": "failure", "error": str(error)})
