# scripts/generate_interview.py
# refer to git repo arcs-api/src/services/generateInterviewService.js
# for simple algorithm implemented in javascript

from typing import List, Dict, Any, Union
from fastapi import HTTPException
from datetime import timedelta


async def getInterviewDuration(style_id: int) -> int:
    # retrieve interview duration
    return 60  # 60 minutes

async def getCandidateAvailability(candidate_id: int) -> List[Dict[str, Any]]:
    # retrieve candidate's availability
    return []

async def getQualifiedInterviewers(job_id: int, style_id: int, organization_id: int) -> List[Dict[str, Any]]:
    # retrieve list of qualified interviewers
    return []

async def getInterviewerAvailability(interviewer_id: int, start_time: str, end_time: str) -> List[Dict[str, Any]]:
    # retrieve interviewer's availability
    return []

async def getCandidateInfo(candidate_id: int) -> Dict[str, Any]:
    # retrieve candidate's info
    return {}

async def getInterviewerInfo(interviewer_id: int) -> Dict[str, Any]:
    # retrieve interviewer's info
    return {}

def shuffle(lst: List[Any]) -> List[Any]:
    import random
    random.shuffle(lst)
    return lst

async def generate_interview(job_id: int, style_id: int, candidate_id: int, organization_id: int) -> Dict[str, Union[str, int]]:
    interview_duration = await getInterviewDuration(style_id)
    candidate_availability = await getCandidateAvailability(candidate_id)
    qualified_interviewers = await getQualifiedInterviewers(job_id, style_id, organization_id)

    if not qualified_interviewers:
        raise HTTPException(status_code=404, detail="No qualified interviewers found")

    shuffled_interviewers = shuffle(qualified_interviewers)
    shuffled_interviewers.sort(key=lambda x: x['count'])

    for interviewer in shuffled_interviewers:
        interviewer_availability = await getInterviewerAvailability(
            interviewer['id'], 
            candidate_availability[0]['start_time'], 
            candidate_availability[-1]['end_time']
        )
        for c_avail in candidate_availability:
            for i_avail in interviewer_availability:
                if c_avail['start_time'] <= i_avail['end_time'] and c_avail['end_time'] >= i_avail['start_time']:
                    potential_start = max(c_avail['start_time'], i_avail['start_time'])
                    potential_end = min(c_avail['end_time'], i_avail['end_time'])

                    if (potential_end - potential_start).seconds >= interview_duration * 60:
                        interview_end_time = potential_start + timedelta(minutes=interview_duration)
                        
                        candidate_info = await getCandidateInfo(candidate_id)
                        interviewer_info = await getInterviewerInfo(interviewer['id'])
                        
                        return {
                            "candidate_id": candidate_id,
                            "candidate_name": candidate_info['name'],
                            "candidate_email": candidate_info['email'],
                            "interviewer_id": interviewer['id'],
                            "interviewer_name": interviewer_info['name'],
                            "interviewer_email": interviewer_info['email'],
                            "job_id": job_id,
                            "style_id": style_id,
                            "start_time": potential_start,
                            "end_time": interview_end_time
                        }

    raise HTTPException(status_code=404, detail="No available slot found")
